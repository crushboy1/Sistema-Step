<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use App\Models\User;
use App\Models\Role; // Asegúrate de que el modelo Role esté importado si usas hasRole()
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Hash;
use Illuminate\Validation\ValidationException;
use Illuminate\Support\Facades\Log;
use App\Models\Curso;

class CursoApiController extends Controller
{
    /**
     * Display a listing of the courses based on user role.
     * Tutors see their own courses. Students see all available courses. Admins see all courses.
     *
     * @param  \Illuminate\Http\Request  $request
     * @return \Illuminate\Http\JsonResponse
     */
    public function index(Request $request)
    {
        $user = Auth::user(); // Obtener el usuario autenticado

        // Verificar si el usuario está autenticado
        if (!$user) {
            Log::warning('Unauthenticated user attempting to access courses index.');
            return response()->json(['message' => 'No autenticado.'], 401);
        }

        Log::info('Fetching courses. User ID: ' . $user->id . ', Roles: ' . json_encode($user->roles->pluck('name')->toArray()));

        try {
            $cursos = collect(); // Inicializa una colección vacía

            if ($user->hasRole('tutor')) {
                // Tutor: Mostrar solo los cursos que este tutor imparte
                $cursos = $user->cursosEnseñados()->with(['tutor' => function($query) {
                    $query->select('id', 'name', 'last_name', 'email', 'number');
                }])->get();
                Log::info('Tutor fetched their own courses.', ['tutor_id' => $user->id, 'course_count' => $cursos->count()]);
            } elseif ($user->hasRole('administrador')) {
                // Administrador: Mostrar todos los cursos
                $cursos = Curso::with(['tutor' => function($query) {
                    $query->select('id', 'name', 'last_name', 'email', 'number');
                }])->get();
                Log::info('Admin fetched all courses.', ['admin_id' => $user->id, 'course_count' => $cursos->count()]);
            } elseif ($user->hasRole('estudiante')) {
                // Estudiante: Mostrar todos los cursos disponibles
                $cursos = Curso::with(['tutor' => function($query) {
                    $query->select('id', 'name', 'last_name', 'email', 'number');
                }])->get();
                Log::info('Student fetched all available courses.', ['student_id' => $user->id, 'course_count' => $cursos->count()]);
            } else {
                // Otros roles o roles no definidos para ver cursos
                Log::warning('User with undefined role attempted to access courses index.', ['user_id' => $user->id, 'roles' => $user->roles->pluck('name')->toArray()]);
                return response()->json(['message' => 'Acceso denegado. Tu rol no tiene permiso para ver cursos.'], 403);
            }

            return response()->json($cursos, 200);

        } catch (\Exception $e) {
            Log::error('Error fetching courses in index method: ' . $e->getMessage(), ['exception' => $e, 'user_id' => $user->id]);
            return response()->json(['message' => 'Error interno del servidor al obtener cursos.'], 500);
        }
    }

    /**
     * Store a newly created course in storage. (Only for Tutors or Administrators)
     *
     * @param  \Illuminate\Http\Request  $request
     * @return \Illuminate\Http\JsonResponse
     */
    public function store(Request $request)
    {
        $user = Auth::user();

        // Permitir que tanto tutores como administradores creen cursos
        if (!$user || (!$user->hasRole('tutor') && !$user->hasRole('administrador'))) {
            Log::warning('Non-tutor/non-admin user or unauthenticated user attempted to store a course.', ['user_id' => $user ? $user->id : 'guest']);
            return response()->json(['message' => 'Acceso denegado. Solo tutores o administradores pueden crear cursos.'], 403);
        }

        Log::info('Attempting to store a new course by user.', ['user_id' => $user->id]);

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

            // Asignar el curso al usuario autenticado (tutor o admin)
            // Si el usuario es un tutor, se asocia directamente.
            // Si es un administrador, se asocia a él, o podrías requerir un 'tutor_id' explícito en el request
            // para que el admin cree un curso para un tutor específico.
            // Por simplicidad, lo asignamos al usuario que lo crea.
            $curso = $user->cursosEnseñados()->create($validatedData);
            Log::info('Course created successfully by user.', ['course_id' => $curso->id, 'creator_id' => $user->id]);

            // Cargar la relación del tutor con el número de contacto para la respuesta
            $curso->load(['tutor' => function($query) {
                $query->select('id', 'name', 'last_name', 'email', 'number');
            }]);

            return response()->json($curso, 201);

        } catch (ValidationException $e) {
            Log::error('Validation error when storing course.', ['errors' => $e->errors(), 'user_id' => $user->id]);
            return response()->json(['message' => 'Validation failed', 'errors' => $e->errors()], 422);
        } catch (\Exception $e) {
            Log::error('Error storing course: ' . $e->getMessage(), ['exception' => $e, 'user_id' => $user->id]);
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
        // No se requiere verificación de rol aquí, ya que cualquier usuario autenticado puede ver un curso.
        $user = Auth::user();
        if (!$user) {
            return response()->json(['message' => 'No autenticado.'], 401);
        }

        Log::info('Fetching course with ID: ' . $id . ' by user ID: ' . $user->id);
        // Cargar el tutor y sus roles, asegurando que incluya el 'number'
        $curso = Curso::with(['tutor' => function($query) {
            $query->select('id', 'name', 'last_name', 'email', 'number');
        }])->find($id);

        if (!$curso) {
            Log::warning('Course not found with ID: ' . $id);
            return response()->json(['message' => 'Curso no encontrado'], 404);
        }

        return response()->json($curso);
    }

    /**
     * Update the specified course in storage. (Only for Tutors, only for their own courses, or Administrators)
     *
     * @param  \Illuminate\Http\Request  $request
     * @param  int  $id
     * @return \Illuminate\Http\JsonResponse
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
                $query->select('id', 'name', 'last_name', 'email', 'number');
            }]);

            return response()->json($curso);

        } catch (ValidationException $e) {
            Log::error('Validation error when updating course.', ['errors' => $e->errors(), 'user_id' => $user->id]);
            return response()->json(['message' => 'Validation failed', 'errors' => $e->errors()], 422);
        } catch (\Exception $e) {
            Log::error('Error updating course: ' . $e->getMessage(), ['exception' => $e, 'user_id' => $user->id]);
            return response()->json(['message' => 'Internal server error'], 500);
        }
    }

    /**
     * Remove the specified course from storage. (Only for Tutors, only for their own courses, or Administrators)
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
            Log::error('Error deleting course: ' . $e->getMessage(), ['exception' => $e, 'user_id' => $user->id]);
            return response()->json(['message' => 'Error al eliminar el curso'], 500);
        }
    }

    /**
     * Enroll an authenticated student in a specific course.
     * Inscribe a un estudiante autenticado en un curso específico.
     *
     * @param  \Illuminate\Http\Request  $request
     * @param  \App\Models\Curso  $curso
     * @return \Illuminate\Http\JsonResponse
     */
    public function enroll(Request $request, Curso $curso)
    {
        $user = Auth::user();

        // Asegurarse de que solo los estudiantes puedan inscribirse
        if (!$user || !$user->hasRole('estudiante')) {
            Log::warning('Non-student user or unauthenticated user attempted to enroll in a course.', ['user_id' => $user ? $user->id : 'guest']);
            return response()->json(['message' => 'Acceso denegado. Solo los estudiantes pueden inscribirse en cursos.'], 403);
        }

        Log::info('Attempting to enroll student in course.', ['student_id' => $user->id, 'course_id' => $curso->id]);

        // Verificar si el estudiante ya está inscrito en el curso
        if ($user->cursos->contains($curso->id)) {
            Log::info('Student already enrolled in course.', ['student_id' => $user->id, 'course_id' => $curso->id]);
            return response()->json([
                'status' => 'error',
                'message' => 'Ya estás inscrito en este curso.'
            ], 409); // 409 Conflict
        }

        try {
            // Adjuntar al estudiante al curso usando la relación muchos a muchos
            $curso->estudiantes()->attach($user->id);
            Log::info('Student successfully enrolled in course.', ['student_id' => $user->id, 'course_id' => $curso->id]);

            return response()->json([
                'status' => 'success',
                'message' => 'Inscripción al curso exitosa.',
                'data' => $curso->load('estudiantes') // Recargar el curso con los estudiantes inscritos
            ], 200);
        } catch (\Exception $e) {
            Log::error('Error enrolling student in course: ' . $e->getMessage(), ['exception' => $e, 'student_id' => $user->id, 'course_id' => $curso->id]);
            return response()->json([
                'status' => 'error',
                'message' => 'Ocurrió un error al inscribirte en el curso.',
                'error_details' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Display a listing of courses the authenticated student is enrolled in.
     * Muestra una lista de los cursos en los que el estudiante autenticado está inscrito.
     * (Solo para estudiantes)
     *
     * @return \Illuminate\Http\JsonResponse
     */
    public function myCursos()
    {
        $user = Auth::user();

        // Asegurarse de que solo los estudiantes puedan ver sus cursos inscritos
        if (!$user || !$user->hasRole('estudiante')) {
            Log::warning('Non-student user or unauthenticated user attempted to access myCursos.', ['user_id' => $user ? $user->id : 'guest']);
            return response()->json(['message' => 'Acceso denegado. Solo los estudiantes pueden ver sus cursos inscritos.'], 403);
        }

        Log::info('Fetching enrolled courses for student ID: ' . $user->id);

        try {
            // Cargar los cursos a los que el estudiante está inscrito
            // Incluimos la relación 'tutor' para obtener la información del tutor del curso
            $enrolledCursos = $user->cursos()->with('tutor')->get();
            Log::info('Enrolled courses fetched successfully for student.', ['student_id' => $user->id, 'course_count' => $enrolledCursos->count()]);

            return response()->json([
                'status' => 'success',
                'message' => 'Cursos en los que estás inscrito obtenidos exitosamente.',
                'data' => $enrolledCursos
            ], 200);
        } catch (\Exception $e) {
            Log::error('Error fetching enrolled courses for student: ' . $e->getMessage(), ['exception' => $e, 'student_id' => $user->id]);
            return response()->json([
                'status' => 'error',
                'message' => 'Ocurrió un error al obtener tus cursos inscritos.',
                'error_details' => $e->getMessage()
            ], 500);
        }
    }
}

