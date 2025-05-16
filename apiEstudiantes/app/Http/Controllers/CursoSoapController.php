<?php

namespace App\Http\Controllers;

use App\Models\Curso;
use Illuminate\Http\Request;

class CursoSoapController extends Controller
{
    public function index(Request $request)
    {
        $server = new \SoapServer(null, [
            'uri' => 'http://localhost:8000/api/soap_soap_cursps',
            'location' => 'http://localhost:8000/api/soap_cursos',
            'soap_version' => SOAP_1_2,
        ]);

        $server->setClass(CursoSoapController::class);
        $server->handle();
    }

    // Obtener la lista de cursos
    public function getCursos()
    {
        $cursos = Curso::all();

        // Convertir a un array para la respuesta SOAP
        return $cursos->map(function ($curso) {
            return [
                'id' => $curso->id,
                'nombre' => $curso->nombre,
                'descripcion' => $curso->descripcion,
                'creditos' => $curso->creditos,
                'created_at' => $curso->created_at,
                'updated_at' => $curso->updated_at,
            ];
        })->toArray();
    }

    public function crearCurso($nombre, $descripcion, $creditos)
{
    // Validar los datos de entrada
    $validator = \Validator::make(
        [
            'nombre' => $nombre,
            'descripcion' => $descripcion,
            'creditos' => $creditos,
        ],
        [
            'nombre' => 'required|string|max:100', // Máximo 100 caracteres
            'descripcion' => 'required|string|max:255', // Máximo 255 caracteres
            'creditos' => 'required|integer|min:1|max:10', // Entre 1 y 10 créditos
        ]
    );

    // Si la validación falla
    if ($validator->fails()) {
        return [
            'success' => false,
            'message' => 'Errores de validación',
            'errors' => $validator->errors(),
        ];
    }

    // Crear el curso en la base de datos
    $curso = Curso::create([
        'nombre' => $nombre,
        'descripcion' => $descripcion,
        'creditos' => $creditos,
    ]);

    return [
        'success' => true,
        'id' => $curso->id,
        'nombre' => $curso->nombre,
        'descripcion' => $curso->descripcion,
        'creditos' => $curso->creditos,
        'created_at' => $curso->created_at,
        'updated_at' => $curso->updated_at,
    ];
}

    // Obtener un curso específico
    public function getCurso($id)
    {
        $curso = Curso::find($id);

        if ($curso) {
            return [
                'id' => $curso->id,
                'nombre' => $curso->nombre,
                'descripcion' => $curso->descripcion,
                'creditos' => $curso->creditos,
                'created_at' => $curso->created_at,
                'updated_at' => $curso->updated_at,
            ];
        }

        return ['message' => 'Curso no encontrado']; // Manejar el error
    }

    // Actualizar un curso
    public function actualizarCurso($id, $nombre, $descripcion, $creditos)
    {
        $curso = Curso::find($id);

        if ($curso) {
            $curso->update([
                'nombre' => $nombre,
                'descripcion' => $descripcion,
                'creditos' => $creditos,
            ]);
            return [
                'id' => $curso->id,
                'nombre' => $curso->nombre,
                'descripcion' => $curso->descripcion,
                'creditos' => $curso->creditos,
                'created_at' => $curso->created_at,
                'updated_at' => $curso->updated_at,
            ];
        }

        return ['message' => 'Curso no encontrado']; // Manejar el error
    }

    // Eliminar un curso
    public function eliminarCurso($id)
    {
        $curso = Curso::find($id);

        if ($curso) {
            $curso->delete();
            return ['message' => 'Curso eliminado'];
        }

        return ['message' => 'Curso no encontrado']; // Manejar el error
    }
}
