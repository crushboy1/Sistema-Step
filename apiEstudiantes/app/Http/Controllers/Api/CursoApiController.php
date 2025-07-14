<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use App\Models\User; 
use App\Models\Role; 
use Illuminate\Support\Facades\Auth; 
use Illuminate\Support\Facades\Hash; 
use Illuminate\Validation\ValidationException; 
use Illuminate\Support\Facades\Log; 
use App\Models\Curso; 

class CursoApiController extends Controller
{
    /**
     * Display a listing of the courses based on user role.
     * Tutors see their own courses. Students see all available courses with optional filtering.
     *
     * @param  \Illuminate\Http\Request  $request
     * @return \Illuminate\Http\JsonResponse
     */
    public function index(Request $request)
    {
        $user = Auth::user(); // Obtener el usuario autenticado

        // Verificar si el usuario está autenticado y tiene roles
        if (!$user) {
            Log::warning('Unauthenticated user attempting to access courses index.');
            return response()->json(['message' => 'No autenticado.'], 401);
        }

        Log::info('Fetching courses. User ID: ' . $user->id . ', Roles: ' . json_encode($user->roles->pluck('name')->toArray()));

        if ($user->hasRole('tutor')) {
            // Tutor: Mostrar solo los cursos que este tutor imparte
            $cursos = $user->cursosEnseñados()->with(['tutor' => function($query) {
                $query->select('id', 'name', 'last_name', 'email', 'number');
            }])->get();
        } elseif ($user->hasRole('administrador')) {
            // Administrador: Mostrar todos los cursos
            $cursos = Curso::with(['tutor' => function($query) {
                $query->select('id', 'name', 'last_name', 'email', 'number');
            }])->get();
        } else {
            // Otros roles: lógica actual (puedes personalizar)
            $cursos = collect(); // Retorna una colección vacía
        }

        return response()->json($cursos);
    }

    /**
     * Store a newly created course in storage. (Only for Tutors)
     *
     * @param  \Illuminate\Http\Request  $request
     * @return \Illuminate\Http\JsonResponse
     */
    public function store(Request $request)
    {
        $user = Auth::user();

        // Permitir que tanto tutores como administradores creen cursos
        // Esto da flexibilidad operativa y permite al admin ayudar o gestionar la oferta académica.
        // El campo user_id del curso reflejará quién lo creó (tutor o admin), lo que mantiene la trazabilidad.
        if (!$user || (!$user->hasRole('tutor') && !$user->hasRole('administrador'))) {
            Log::warning('Non-tutor/non-admin user or unauthenticated user attempted to store a course.', ['user_id' => $user ? $user->id : 'guest']);
            return response()->json(['message' => 'Acceso denegado. Solo tutores o administradores pueden crear cursos.'], 403);
        }

        Log::info('Attempting to store a new course by tutor.', ['tutor_id' => $user->id]);

        try {
            $validatedData = $request->validate([
                'nombre' => 'required|string|max:255',
                'descripcion' => 'nullable|string',
                'monto' => 'required|numeric|min:0', 
                'frecuencia' => 'nullable|string|max:255', 
                'imagen_url' => 'nullable|url', 
                'dias_tutoria' => 'nullable|string|max:255',
                'forma_pago' => 'nullable|string|max:255',
                'otros' => 'nullable|string',
            ]);
            Log::info('Validated data for new course.', $validatedData);

            // Asignar el curso al tutor autenticado
            $curso = $user->cursosEnseñados()->create($validatedData);
            Log::info('Course created successfully by tutor.', ['course_id' => $curso->id, 'tutor_id' => $user->id]);

            // Cargar la relación del tutor con el número de contacto para la respuesta
            $curso->load(['tutor' => function($query) {
                $query->select('id', 'name', 'last_name', 'email', 'number'); // CAMBIADO: Usar 'number'
            }]);

            return response()->json($curso, 201);

        } catch (ValidationException $e) {
            Log::error('Validation error when storing course.', ['errors' => $e->errors()]);
            return response()->json(['message' => 'Validation failed', 'errors' => $e->errors()], 422);
        } catch (\Exception $e) {
            Log::error('Error storing course: ' . $e->getMessage(), ['exception' => $e]);
            return response()->json(['message' => 'Internal server error'], 500);
        }
    }

    /**
     * Display the specified course.
     * Any authenticated user can view a course.
     *
     * @param  int  $id
     * @return \Illuminate\Http\JsonResponse
     */
    public function show($id)
    {
        Log::info('Fetching course with ID: ' . $id);
        // Cargar el tutor y sus roles, asegurando que incluya el 'number'
        $curso = Curso::with(['tutor' => function($query) {
            $query->select('id', 'name', 'last_name', 'email', 'number'); // CAMBIADO: Usar 'number'
        }])->find($id);

        if (!$curso) {
            Log::warning('Course not found with ID: ' . $id);
            return response()->json(['message' => 'Curso no encontrado'], 404);
        }

        return response()->json($curso);
    }

    /**
     * Update the specified course in storage. (Only for Tutors, only for their own courses)
     *
     * @param  \Illuminate\Http\Request  $request
     * @param  int  $id
     * @return \Illuminate\Http->JsonResponse
     */
    public function update(Request $request, $id)
    {
        $user = Auth::user();

        // Permitir que tutores propietarios o administradores actualicen cursos
        if (!$user || (!$user->hasRole('tutor') && !$user->hasRole('administrador'))) {
            Log::warning('Non-tutor/non-admin user or unauthenticated user attempted to update a course.', ['user_id' => $user ? $user->id : 'guest']);
            return response()->json(['message' => 'Acceso denegado. Solo tutores propietarios o administradores pueden actualizar cursos.'], 403);
        }

        $curso = Curso::find($id);

        if (!$curso) {
            Log::warning('Course not found for update with ID: ' . $id);
            return response()->json(['message' => 'Curso no encontrado'], 404);
        }

        // Si es tutor, solo puede actualizar sus propios cursos. El admin puede actualizar cualquiera.
        if ($user->hasRole('tutor') && !$user->hasRole('administrador') && $curso->user_id !== $user->id) {
            Log::warning('Tutor attempted to update a course they do not own.', ['tutor_id' => $user->id, 'course_id' => $id, 'owner_id' => $curso->user_id]);
            return response()->json(['message' => 'No tienes permiso para actualizar este curso.'], 403);
        }

        try {
            $validatedData = $request->validate([
                'nombre' => 'sometimes|string|max:255',
                'descripcion' => 'nullable|string',
                'monto' => 'sometimes|required|numeric|min:0',
                'frecuencia' => 'nullable|string|max:255',
                'imagen_url' => 'nullable|url',
                'dias_tutoria' => 'nullable|string|max:255',
                'forma_pago' => 'nullable|string|max:255',
                'otros' => 'nullable|string',
            ]);
            Log::info('Validated data for course update.', $validatedData);

            $curso->update($validatedData);
            Log::info('Course updated successfully.', ['course_id' => $curso->id, 'updated_by' => $user->id]);

            // Cargar la relación del tutor con el número de contacto para la respuesta
            $curso->load(['tutor' => function($query) {
                $query->select('id', 'name', 'last_name', 'email', 'number'); // CAMBIADO: Usar 'number'
            }]);

            return response()->json($curso);

        } catch (ValidationException $e) {
            Log::error('Validation error when updating course.', ['errors' => $e->errors()]);
            return response()->json(['message' => 'Validation failed', 'errors' => $e->errors()], 422);
        } catch (\Exception $e) {
            Log::error('Error updating course: ' . $e->getMessage(), ['exception' => $e]);
            return response()->json(['message' => 'Internal server error'], 500);
        }
    }

    /**
     * Remove the specified course from storage. (Only for Tutors, only for their own courses)
     *
     * @param  int  $id
     * @return \Illuminate\Http\JsonResponse
     */
    public function destroy($id)
    {
        $user = Auth::user();

        // Permitir que tutores propietarios o administradores eliminen cursos
        if (!$user || (!$user->hasRole('tutor') && !$user->hasRole('administrador'))) {
            Log::warning('Non-tutor/non-admin user or unauthenticated user attempted to delete a course.', ['user_id' => $user ? $user->id : 'guest']);
            return response()->json(['message' => 'Acceso denegado. Solo tutores propietarios o administradores pueden eliminar cursos.'], 403);
        }

        $curso = Curso::find($id);

        if (!$curso) {
            Log::warning('Course not found for deletion with ID: ' . $id);
            return response()->json(['message' => 'Curso no encontrado'], 404);
        }

        // Si es tutor, solo puede eliminar sus propios cursos. El admin puede eliminar cualquiera.
        if ($user->hasRole('tutor') && !$user->hasRole('administrador') && $curso->user_id !== $user->id) {
            Log::warning('Tutor attempted to delete a course they do not own.', ['tutor_id' => $user->id, 'course_id' => $id, 'owner_id' => $curso->user_id]);
            return response()->json(['message' => 'No tienes permiso para eliminar este curso.'], 403);
        }

        try {
            $curso->delete();
            Log::info('Course deleted successfully.', ['course_id' => $curso->id, 'deleted_by' => $user->id]);
            return response()->json(['message' => 'Curso eliminado exitosamente']);
        } catch (\Exception $e) {
            Log::error('Error deleting course: ' . $e->getMessage(), ['exception' => $e]);
            return response()->json(['message' => 'Error al eliminar el curso'], 500);
        }
    }
}
