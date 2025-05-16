<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Curso;
use Illuminate\Http\Request;

class CursoApiController extends Controller
{
    // Obtener lista de cursos
    public function index()
    {
        $cursos = Curso::all();
        return response()->json($cursos, 200);
    }

    // Crear un nuevo curso
public function store(Request $request)
{
    $validatedData = $request->validate([
        'nombre' => 'required|string|max:255',
        'descripcion' => 'nullable|string',
        'creditos' => 'required|numeric|min:1|max:10',
    ]);

    $curso = Curso::create($validatedData);

    // Reorganizar la respuesta con el 'id' primero
    $response = [
        'id' => $curso->id,
        'nombre' => $curso->nombre,
        'descripcion' => $curso->descripcion,
        'creditos' => $curso->creditos,
        'created_at' => $curso->created_at,
        'updated_at' => $curso->updated_at,
    ];

    return response()->json($response, 201);
}


    // Mostrar un curso específico
    public function show($id)
    {
        $curso = Curso::find($id);

        if ($curso) {
            return response()->json($curso, 200);
        } else {
            return response()->json(['message' => 'Curso no encontrado'], 404);
        }
    }

    // Actualizar un curso
    public function update(Request $request, $id)
    {
        $curso = Curso::find($id);

        if ($curso) {
            $validatedData = $request->validate([
                'nombre' => 'string|max:255',
                'descripcion' => 'nullable|string',
                'creditos' => 'required|numeric|min:1|max:10',

            ]);

            $curso->update($validatedData);
            return response()->json($curso, 200);
        } else {
            return response()->json(['message' => 'Curso no encontrado'], 404);
        }
    }

    // Eliminar un curso
    public function destroy($id)
    {
        $curso = Curso::find($id);

        if ($curso) {
            $curso->delete();
            return response()->json(['message' => 'Curso eliminado'], 200);
        } else {
            return response()->json(['message' => 'Curso no encontrado'], 404);
        }
    }
}
