<?php

namespace App\Http\Controllers;

use App\Models\Estudiante;
use Illuminate\Http\Request;

class EstudianteSoapController extends Controller
{
    public function index(Request $request)
    {
        $server = new \SoapServer(null, [
            'uri' => 'http://localhost:8000/api/v1/soap',
            'location' => 'http://localhost:8000/api/v1/soap',
            'soap_version' => SOAP_1_1,
        ]);

        $server->setClass(EstudianteSoapController::class);
        $server->handle();
    }

    // Obtener la lista de estudiantes
    public function getEstudiantes()
    {
        $estudiantes = Estudiante::all();

        // Convertir a un array para la respuesta SOAP
        return $estudiantes->map(function($estudiante) {
            return [
                'id' => $estudiante->id,
                'nombre' => $estudiante->nombre,
                'apellido' => $estudiante->apellido,
                'edad' => $estudiante->edad,
                'created_at' => $estudiante->created_at,
                'updated_at' => $estudiante->updated_at,
            ];
        })->toArray();
    }

    // Crear un nuevo estudiante
    public function crearEstudiante($nombre, $apellido, $edad)
    {
        $estudiante = Estudiante::create([
            'nombre' => $nombre,
            'apellido' => $apellido,
            'edad' => $edad,
        ]);

        return [
            'id' => $estudiante->id,
            'nombre' => $estudiante->nombre,
            'apellido' => $estudiante->apellido,
            'edad' => $estudiante->edad,
            'created_at' => $estudiante->created_at,
            'updated_at' => $estudiante->updated_at,
        ];
    }

    // Obtener un estudiante específico
    public function getEstudiante($id)
    {
        $estudiante = Estudiante::find($id);

        if ($estudiante) {
            return [
                'id' => $estudiante->id,
                'nombre' => $estudiante->nombre,
                'apellido' => $estudiante->apellido,
                'edad' => $estudiante->edad,
                'created_at' => $estudiante->created_at,
                'updated_at' => $estudiante->updated_at,
            ];
        }

        return null; // O manejar el error de otra manera
    }
    // Actualizar un estudiante
    public function actualizarEstudiante($id, $nombre, $apellido, $edad)
    {
        $estudiante = Estudiante::find($id);

        if ($estudiante) {
            $estudiante->update([
                'nombre' => $nombre,
                'apellido' => $apellido,
                'edad' => $edad,
            ]);

            return [
                'id' => $estudiante->id,
                'nombre' => $estudiante->nombre,
                'apellido' => $estudiante->apellido,
                'edad' => $estudiante->edad,
                'created_at' => $estudiante->created_at,
                'updated_at' => $estudiante->updated_at,
            ];
        }

        return ['message' => 'Estudiante no encontrado']; // Manejar el error si el estudiante no existe
    }

    // Eliminar un estudiante
    public function eliminarEstudiante($id)
    {
        $estudiante = Estudiante::find($id);

        if ($estudiante) {
            $estudiante->delete();
            return ['message' => 'Estudiante eliminado exitosamente'];
        }

        return ['message' => 'Estudiante no encontrado']; // Manejar el error si el estudiante no existe
    }
}