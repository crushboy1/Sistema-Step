<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Estudiante;
use App\Models\Curso;  // Agregar el modelo Curso

use Illuminate\Http\Request;

class EstudianteApiController extends Controller
{
    // Obtener lista de estudiantes
    public function index()
    {
        $estudiantes = Estudiante::all();
        return response()->json($estudiantes, 200);
    }

    // Crear un nuevo estudiante
public function store(Request $request)
    {
        $validatedData = $request->validate([
        'nombre' => 'required|string|max:255',
        'apellido' => 'required|string|max:255',
        'edad' => 'required|integer|min:0',
        ]);

    $estudiante = Estudiante::create($validatedData);

    // Reorganizar el array para que 'id' esté al inicio
    $response = [
        'id' => $estudiante->id,
        'nombre' => $estudiante->nombre,
        'apellido' => $estudiante->apellido,
        'edad' => $estudiante->edad,
        'created_at' => $estudiante->created_at,
        'updated_at' => $estudiante->updated_at,
    ];

    // Devolver el array reorganizado
    return response()->json($response, 201);
    }


    // Mostrar un estudiante específico
    public function show($id)
    {
        $estudiante = Estudiante::find($id);

        if ($estudiante) {
            return response()->json($estudiante, 200);
        } else {
            return response()->json(['message' => 'Estudiante no encontrado'], 404);
        }
    }

    // Actualizar un estudiante
    public function update(Request $request, $id)
    {
        $estudiante = Estudiante::find($id);

        if ($estudiante) {
            $validatedData = $request->validate([
                'nombre' => 'string|max:255',
                'apellido' => 'string|max:255',
                'edad' => 'integer|min:0',
            ]);

            $estudiante->update($validatedData);
            return response()->json($estudiante, 200);
        } else {
            return response()->json(['message' => 'Estudiante no encontrado'], 404);
        }
    }
    
    // Asignar un curso a un estudiante
    public function asignarCurso(Request $request, $id)
    {
        $estudiante = Estudiante::find($id);

        if (!$estudiante) {
            return response()->json(['message' => 'Estudiante no encontrado'], 404);
        }

        $validatedData = $request->validate([
            'curso_id' => 'required|exists:cursos,id',
            'nota' => 'nullable|numeric|min:0|max:10',
            'estado' => 'nullable|string|in:Aprobado,Desaprobado',
        ]);

        // Asignar curso con nota y estado si se proporcionan
        $estudiante->cursos()->attach($validatedData['curso_id'], [
            'nota' => $validatedData['nota'],
            'estado' => $validatedData['estado']
        ]);

        return response()->json(['message' => 'Curso asignado correctamente'], 200);
    }

    // Actualizar la nota y el estado de un curso de un estudiante
    public function actualizarCurso(Request $request, $id, $cursoId)
    {
        $estudiante = Estudiante::find($id);

        if (!$estudiante) {
            return response()->json(['message' => 'Estudiante no encontrado'], 404);
        }

        // Verificar si el estudiante ya está inscrito en este curso
        $cursoEstudiante = $estudiante->cursos()->where('curso_id', $cursoId)->first();

        if (!$cursoEstudiante) {
            return response()->json(['message' => 'Este curso no está asignado a este estudiante'], 404);
        }

        $validatedData = $request->validate([
            'nota' => 'nullable|numeric|min:0|max:10',
            'estado' => 'nullable|string|in:Aprobado,Desaprobado',
        ]);

        // Actualizar la información del curso en la tabla intermedia
        $estudiante->cursos()->updateExistingPivot($cursoId, [
            'nota' => $validatedData['nota'],
            'estado' => $validatedData['estado']
        ]);

        return response()->json(['message' => 'Curso actualizado correctamente'], 200);
    }


    // Eliminar un estudiante
    public function destroy($id)
    {
        $estudiante = Estudiante::find($id);

        if ($estudiante) {
            $estudiante->delete();
            return response()->json(['message' => "Estudiante $id eliminado"], 200);
        } else {
            return response()->json(['message' => 'Estudiante no encontrado'], 404);
        }
    }
}
