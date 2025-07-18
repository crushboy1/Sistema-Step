<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use App\Models\Rating;
use App\Models\User; // Necesario para verificar tutores/estudiantes
use App\Models\AcademicSession; // <-- CAMBIO AQUÍ: Usar AcademicSession en lugar de Session
use Illuminate\Support\Facades\Auth; // Para obtener el usuario autenticado
use Illuminate\Support\Facades\Validator; // Para validación de datos

class RatingApiController extends Controller
{
    /**
     * Almacena una nueva calificación en la base de datos.
     *
     * @param  \Illuminate\Http\Request  $request
     * @return \Illuminate\Http\JsonResponse
     */
    public function store(Request $request)
    {
        // 1. Validar los datos de entrada
        $validator = Validator::make($request->all(), [
            'tutor_id' => 'required|exists:users,id', // El ID del tutor es requerido y debe existir en la tabla users
            // CAMBIO AQUÍ: session_id ahora hace referencia a la tabla academic_sessions
            'session_id' => 'nullable|exists:academic_sessions,id', // El ID de la sesión académica es opcional, pero si se proporciona, debe existir
            'rating' => 'required|integer|min:1|max:5', // La calificación es requerida, un entero entre 1 y 5
            'comment' => 'nullable|string|max:500', // El comentario es opcional, un string con máximo 500 caracteres
        ]);

        if ($validator->fails()) {
            return response()->json([
                'status' => 'error',
                'message' => 'Error de validación',
                'errors' => $validator->errors()
            ], 422); // Código de estado 422 para errores de validación
        }

        try {
            // Obtener el ID del estudiante autenticado.
            $studentId = Auth::id();

            // Opcional: Verificar que el estudiante no se califique a sí mismo
            if ($studentId == $request->tutor_id) {
                return response()->json([
                    'status' => 'error',
                    'message' => 'Un estudiante no puede calificarse a sí mismo.'
                ], 403); // Código de estado 403 para prohibido
            }

            // Opcional: Verificar que el tutor_id realmente corresponda a un tutor.
            // Esto asume que tienes un campo 'role' o un sistema de roles más sofisticado.
            // Si tienes un campo 'role_id' en la tabla users y un rol 'tutor', podrías hacer:
            // $tutor = User::where('id', $request->tutor_id)->whereHas('roles', function($q){ $q->where('name', 'tutor'); })->first();
            // if (!$tutor) { ... }

            // Opcional: Verificar que el estudiante realmente participó en la sesión si session_id está presente
            if ($request->filled('session_id')) {
                // CAMBIO AQUÍ: Buscar en AcademicSession
                $academicSession = AcademicSession::find($request->session_id);
                if (!$academicSession || $academicSession->student_id !== $studentId || $academicSession->tutor_id !== $request->tutor_id) {
                    return response()->json([
                        'status' => 'error',
                        'message' => 'La sesión académica proporcionada no es válida para esta calificación o no te corresponde.'
                    ], 400); // Código de estado 400 para solicitud incorrecta
                }

                // Opcional: Evitar calificaciones duplicadas para la misma sesión académica
                $existingRating = Rating::where('student_id', $studentId)
                                        ->where('tutor_id', $request->tutor_id)
                                        ->where('session_id', $request->session_id)
                                        ->first();
                if ($existingRating) {
                    return response()->json([
                        'status' => 'error',
                        'message' => 'Ya has calificado a este tutor para esta sesión académica.'
                    ], 409); // Código de estado 409 para conflicto
                }
            }


            // Crear la nueva calificación
            $rating = Rating::create([
                'student_id' => $studentId,
                'tutor_id' => $request->tutor_id,
                'session_id' => $request->session_id, // Este es el ID de la AcademicSession
                'rating' => $request->rating,
                'comment' => $request->comment,
            ]);

            return response()->json([
                'status' => 'success',
                'message' => 'Calificación guardada exitosamente.',
                'data' => $rating
            ], 201); // Código de estado 201 para recurso creado
        } catch (\Exception $e) {
            // Manejo de errores inesperados
            return response()->json([
                'status' => 'error',
                'message' => 'Ocurrió un error al guardar la calificación.',
                'error_details' => $e->getMessage()
            ], 500); // Código de estado 500 para error interno del servidor
        }
    }

    /**
     * Muestra una lista de calificaciones.
     * Puede filtrar por tutor_id o student_id.
     *
     * @param  \Illuminate\Http\Request  $request
     * @return \Illuminate\Http\JsonResponse
     */
    public function index(Request $request)
    {
        try {
            $query = Rating::query();

            // Filtrar por tutor_id si se proporciona
            if ($request->has('tutor_id')) {
                $query->where('tutor_id', $request->tutor_id);
            }

            // Filtrar por student_id si se proporciona
            if ($request->has('student_id')) {
                $query->where('student_id', $request->student_id);
            }

            // Opcional: Incluir relaciones (estudiante, tutor, sesión académica)
            // CAMBIO AQUÍ: Cargar la relación academicSession
            $ratings = $query->with(['student', 'tutor', 'academicSession'])->get();

            // Calcular el promedio de calificación para el tutor si se filtra por tutor_id
            $averageRating = null;
            if ($request->has('tutor_id')) {
                $averageRating = Rating::where('tutor_id', $request->tutor_id)->avg('rating');
            }

            return response()->json([
                'status' => 'success',
                'message' => 'Calificaciones obtenidas exitosamente.',
                'data' => $ratings,
                'average_rating' => $averageRating // Incluir el promedio si aplica
            ], 200);
        } catch (\Exception $e) {
            return response()->json([
                'status' => 'error',
                'message' => 'Ocurrió un error al obtener las calificaciones.',
                'error_details' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Muestra una calificación específica por ID.
     *
     * @param  int  $id
     * @return \Illuminate\Http\JsonResponse
     */
    public function show($id)
    {
        try {
            // Buscar la calificación por ID, incluyendo sus relaciones
            // CAMBIO AQUÍ: Cargar la relación academicSession
            $rating = Rating::with(['student', 'tutor', 'academicSession'])->find($id);

            if (!$rating) {
                return response()->json([
                    'status' => 'error',
                    'message' => 'Calificación no encontrada.'
                ], 404); // Código de estado 404 para no encontrado
            }

            return response()->json([
                'status' => 'success',
                'message' => 'Calificación obtenida exitosamente.',
                'data' => $rating
            ], 200);
        } catch (\Exception $e) {
            return response()->json([
                'status' => 'error',
                'message' => 'Ocurrió un error al obtener la calificación.',
                'error_details' => $e->getMessage()
            ], 500);
        }
    }
}

