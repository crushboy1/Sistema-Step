<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use App\Models\User; // Ahora trabajamos con el modelo User
use App\Models\Role; // Necesario para buscar el rol 'estudiante'
use App\Models\Curso; // Para las relaciones de cursos
use Illuminate\Support\Facades\Hash;
use Illuminate\Validation\ValidationException;
use Illuminate\Support\Facades\Log;


class EstudianteApiController extends Controller
{
    // Método auxiliar para obtener usuarios con rol de estudiante
    private function getEstudianteUsers()
    {
        return User::whereHas('roles', function ($query) {
            $query->where('name', 'estudiante');
        });
    }

    /**
     * Display a listing of the students (users with 'estudiante' role).
     *
     * @return \Illuminate->Http->JsonResponse
     */
    public function index()
    {
        Log::info('Fetching all students (users with estudiante role).');
        $estudiantes = $this->getEstudianteUsers()->get();

        return response()->json($estudiantes);
    }

    /**
     * Store a newly created student (user with 'estudiante' role) in storage.
     * Este método crearía un usuario directamente con rol estudiante.
     * Considera si el registro general ya cubre esto (AuthApiController::register).
     *
     * @param  \Illuminate->Http->Request  $request
     * @return \Illuminate->Http->JsonResponse
     */
    public function store(Request $request)
    {
        Log::info('Attempting to store a new student user.');
        try {
            $validatedData = $request->validate([
                'name' => 'required|string|max:255',
                'last_name' => 'required|string|max:255',
                'number' => 'required|string|max:20',
                'email' => 'required|email|unique:users',
                'password' => 'required|min:6', // No 'confirmed' aquí a menos que el frontend lo envíe
                
            ]);
            Log::info('Validated data for new student.', $validatedData);

            $user = User::create([
                'name' => $validatedData['name'],
                'last_name' => $validatedData['last_name'],
                'number' => $validatedData['number'],
                'email' => $validatedData['email'],
                'password' => Hash::make($validatedData['password']),
                'registered_ip' => $request->ip(),
            ]);
            Log::info('User created successfully. Assigning role...', ['user_id' => $user->id]);

            $estudianteRole = Role::where('name', 'estudiante')->first();
            if ($estudianteRole) {
                $user->roles()->attach($estudianteRole->id);
                Log::info('Role "estudiante" assigned to user.', ['user_id' => $user->id]);
            } else {
                Log::warning('Role "estudiante" not found during student creation. Please ensure it exists.');
                // Consider rolling back user creation or notifying admin
            }

            return response()->json($user, 201);

        } catch (ValidationException $e) {
            Log::error('Validation error when storing student.', ['errors' => $e->errors()]);
            return response()->json(['message' => 'Validation failed', 'errors' => $e->errors()], 422);
        } catch (\Exception $e) {
            Log::error('Error storing student: ' . $e->getMessage(), ['exception' => $e]);
            return response()->json(['message' => 'Internal server error'], 500);
        }
    }

    /**
     * Display the specified student (user with 'estudiante' role).
     *
     * @param  int  $id
     * @return \Illuminate->Http->JsonResponse
     */
    public function show($id)
    {
        Log::info('Fetching student with ID: ' . $id);
        $estudiante = $this->getEstudianteUsers()->find($id);

        if (!$estudiante) {
            Log::warning('Student not found with ID: ' . $id);
            return response()->json(['message' => 'Estudiante no encontrado'], 404);
        }

        return response()->json($estudiante);
    }

    /**
     * Update the specified student (user with 'estudiante' role) in storage.
     *
     * @param  \Illuminate->Http->Request  $request
     * @param  int  $id
     * @return \Illuminate->Http->JsonResponse
     */
    public function update(Request $request, $id)
    {
        Log::info('Updating student with ID: ' . $id);
        try {
            $user = $this->getEstudianteUsers()->find($id);

            if (!$user) {
                Log::warning('Student not found for update with ID: ' . $id);
                return response()->json(['message' => 'Estudiante no encontrado'], 404);
            }

            $validatedData = $request->validate([
                'name' => 'sometimes|required|string|max:255',
                'last_name' => 'sometimes|required|string|max:255',
                'number' => 'sometimes|required|string|max:20',
                'email' => 'sometimes|required|email|unique:users,email,' . $id,
        
            ]);
            Log::info('Validated data for student update.', $validatedData);

            $user->update($validatedData);
            Log::info('Student updated successfully.', ['user_id' => $user->id]);

            return response()->json($user);

        } catch (ValidationException $e) {
            Log::error('Validation error when updating student.', ['errors' => $e->errors()]);
            return response()->json(['message' => 'Validation failed', 'errors' => $e->errors()], 422);
        } catch (\Exception $e) {
            Log::error('Error updating student: ' . $e->getMessage(), ['exception' => $e]);
            return response()->json(['message' => 'Internal server error'], 500);
        }
    }

    /**
     * Remove the specified student (user with 'estudiante' role) from storage.
     * Esto eliminará al usuario completo.
     *
     * @param  int  $id
     * @return \Illuminate->Http->JsonResponse
     */
    public function destroy($id)
    {
        Log::info('Deleting student with ID: ' . $id);
        $user = $this->getEstudianteUsers()->find($id);

        if (!$user) {
            Log::warning('Student not found for deletion with ID: ' . $id);
            return response()->json(['message' => 'Estudiante no encontrado'], 404);
        }

        try {
            // Esto también eliminará las entradas en la tabla pivot `role_user` y `course_user` (si se usa onDelete('cascade'))
            $user->delete();
            Log::info('Student deleted successfully.', ['user_id' => $user->id]);
            return response()->json(['message' => 'Estudiante eliminado exitosamente']);
        } catch (\Exception $e) {
            Log::error('Error deleting student: ' . $e->getMessage(), ['exception' => $e]);
            return response()->json(['message' => 'Error al eliminar el estudiante'], 500);
        }
    }

    // --- Métodos para la gestión de cursos por parte de estudiantes ---

    /**
     * Asignar un curso a un estudiante.
     * Esto asume una relación many-to-many entre User (estudiante) y Curso.
     *
     * @param  \Illuminate->Http->Request  $request
     * @param  int  $id (ID del usuario estudiante)
     * @return \Illuminate->Http->JsonResponse
     */
    public function asignarCurso(Request $request, $id)
    {
        Log::info('Attempting to assign course to student ID: ' . $id);
        try {
            $request->validate([
                'curso_id' => 'required|exists:courses,id', // ¡Cambiado de 'cursos' a 'courses'!
            ]);
            Log::info('Validated data for course assignment.', ['student_id' => $id, 'curso_id' => $request->curso_id]);

            $estudiante = $this->getEstudianteUsers()->find($id);

            if (!$estudiante) {
                Log::warning('Student not found for course assignment with ID: ' . $id);
                return response()->json(['message' => 'Estudiante no encontrado'], 404);
            }

            $curso = Curso::find($request->curso_id);
            if (!$curso) {
                Log::warning('Course not found for assignment with ID: ' . $request->curso_id);
                return response()->json(['message' => 'Curso no encontrado'], 404);
            }

            // Asegurarse de que el estudiante no esté ya en el curso
            if ($estudiante->cursos->contains($curso->id)) {
                Log::info('Student already registered for this course.', ['student_id' => $id, 'curso_id' => $request->curso_id]);
                return response()->json(['message' => 'El estudiante ya está registrado en este curso'], 409); // Conflict
            }

            // Asignar el curso al estudiante (asumiendo una relación many-to-many 'cursos' en el modelo User)
            $estudiante->cursos()->attach($curso->id);
            Log::info('Course assigned successfully to student.', ['student_id' => $id, 'curso_id' => $curso->id]);

            return response()->json(['message' => 'Curso asignado exitosamente al estudiante'], 200);

        } catch (ValidationException $e) {
            Log::error('Validation error during course assignment.', ['errors' => $e->errors()]);
            return response()->json(['message' => 'Validation failed', 'errors' => $e->errors()], 422);
        } catch (\Exception $e) {
            Log::error('Error assigning course: ' . $e->getMessage(), ['exception' => $e]);
            return response()->json(['message' => 'Internal server error'], 500);
        }
    }

    /**
     * Actualizar la relación de un curso con un estudiante.
     * Este método podría servir para "desregistrar" o "cambiar estado" si la tabla pivote tuviera más campos.
     * Por ahora, asume que es para desregistrar si el curso ya no existe en la solicitud.
     * Para 'actualizar' un curso asignado, quizás es mejor un detach y luego un attach.
     * O si es cambiar el estado de la matrícula, la tabla pivote necesitaría un campo 'estado'.
     *
     * @param  \Illuminate->Http->Request  $request
     * @param  int  $id (ID del usuario estudiante)
     * @param  int  $cursoId (ID del curso a actualizar/desregistrar)
     * @return \Illuminate->Http->JsonResponse
     */
    public function actualizarCurso(Request $request, $id, $cursoId)
    {
        Log::info('Attempting to update/detach course from student ID: ' . $id . ' Course ID: ' . $cursoId);

        $estudiante = $this->getEstudianteUsers()->find($id);

        if (!$estudiante) {
            Log::warning('Student not found for course update with ID: ' . $id);
            return response()->json(['message' => 'Estudiante no encontrado'], 404);
        }

        $curso = Curso::find($cursoId);
        if (!$curso) {
            // Si el curso no existe, podemos interpretar que se quiere desasociar
            Log::info('Course not found for update, assuming detach operation.', ['curso_id' => $cursoId]);
            $estudiante->cursos()->detach($cursoId); // Intenta desasociar de todas formas
            return response()->json(['message' => 'Curso no encontrado, si estaba asociado, se ha desasociado del estudiante'], 200);
        }

        // Aquí puedes añadir lógica para "actualizar" la relación si tu tabla pivote `course_user`
        // tiene campos adicionales (ej. 'estado_matricula', 'calificacion').
        // Por ejemplo: $estudiante->cursos()->updateExistingPivot($cursoId, ['estado_matricula' => 'completado']);

        // Si es una simple actualización (ej. reconfirmar la matrícula), no hay necesidad de hacer nada
        // a menos que cambien otros campos de la tabla pivote.
        // Si la intención es solo asegurarse de que esté asociado, puedes hacer:
        if (!$estudiante->cursos->contains($cursoId)) {
            $estudiante->cursos()->attach($cursoId);
            Log::info('Course re-attached (if not already) to student.', ['student_id' => $id, 'curso_id' => $cursoId]);
        }
        Log::info('Course association confirmed for student.', ['student_id' => $id, 'curso_id' => $cursoId]);
        return response()->json(['message' => 'Curso asociado al estudiante (o relación confirmada)'], 200);
    }

}