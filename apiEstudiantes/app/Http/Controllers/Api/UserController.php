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

class UserController extends Controller
{
    // La lógica de control de acceso se maneja directamente dentro de cada método,
    // ya que no se utilizan middlewares en la configuración actual.
    public function __construct()
    {
        // No se requiere middleware en el constructor para este escenario.
    }

    /**
     * Display a listing of all users (admin panel view).
     * Only accessible by 'admin' role.
     *
     * @return \Illuminate\Http\JsonResponse
     */
    public function index()
    {
        $user = Auth::user();
        if (!$user || !$user->hasRole('administrador')) {
            Log::warning('Non-admin user or unauthenticated user attempted to access all users list.');
            return response()->json(['message' => 'Acceso denegado. Solo administradores.'], 403);
        }

        Log::info('Admin user accessing all users list.', ['admin_id' => $user->id]);
        // Cargar roles de cada usuario para la vista del panel
        $users = User::with('roles')->get();
        return response()->json($users);
    }

    /**
     * Store a newly created user in storage.
     * Only accessible by 'admin' role.
     *
     * @param  \Illuminate\Http\Request  $request
     * @return \Illuminate\Http\JsonResponse
     */
    public function store(Request $request)
    {
        $admin = Auth::user();
        if (!$admin || !$admin->hasRole('administrador')) {
            Log::warning('Non-admin user or unauthenticated user attempted to create a user.');
            return response()->json(['message' => 'Acceso denegado. Solo administradores.'], 403);
        }

        Log::info('Admin user attempting to create a new user.', ['admin_id' => $admin->id]);

        try {
            $validatedData = $request->validate([
                'name' => 'required|string|max:255',
                'last_name' => 'required|string|max:255',
                'number' => 'required|string|max:20',
                'email' => 'required|email|unique:users',
                'password' => [
                    'required',
                    'string',
                    'min:8',
                    'max:255',
                    'regex:/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/',
                    'confirmed'
                ],
                'role_names' => 'nullable|array', // Array de nombres de roles (ej. ['admin', 'tutor'])
                'role_names.*' => 'string|exists:roles,name', // Cada nombre de rol debe existir en la tabla 'roles'
            ]);
            Log::info('Validated data for new user creation by admin.', $validatedData);

            $user = User::create([
                'name' => $validatedData['name'],
                'last_name' => $validatedData['last_name'],
                'number' => $validatedData['number'],
                'email' => $validatedData['email'],
                'password' => Hash::make($validatedData['password']),
                'registered_ip' => $request->ip(),
            ]);
            Log::info('User created successfully by admin. Assigning roles...', ['user_id' => $user->id]);

            if (isset($validatedData['role_names'])) {
                $roles = Role::whereIn('name', $validatedData['role_names'])->get();
                $user->roles()->sync($roles->pluck('id')); // Sync para adjuntar o desadjuntar roles
                Log::info('Roles assigned to new user.', ['user_id' => $user->id, 'roles' => $roles->pluck('name')->toArray()]);
            } else {
                // Si no se especifican roles, podrías asignar un rol por defecto, ej. 'estudiante'
                $defaultRole = Role::where('name', 'estudiante')->first();
                if ($defaultRole) {
                    $user->roles()->attach($defaultRole->id);
                    Log::info('Default role "estudiante" assigned to new user.', ['user_id' => $user->id]);
                }
            }

            // Recargar el usuario con sus roles para la respuesta
            $user->load('roles');
            return response()->json($user, 201);

        } catch (ValidationException $e) {
            Log::error('Validation error when creating user by admin.', ['errors' => $e->errors()]);
            return response()->json(['message' => 'Validation failed', 'errors' => $e->errors()], 422);
        } catch (\Exception $e) {
            Log::error('Error creating user by admin: ' . $e->getMessage(), ['exception' => $e]);
            return response()->json(['message' => 'Internal server error'], 500);
        }
    }

    /**
     * Display the specified user.
     * Only accessible by 'admin' role.
     *
     * @param  int  $id
     * @return \Illuminate\Http\JsonResponse
     */
    public function show($id)
    {
        $admin = Auth::user();
        if (!$admin || !$admin->hasRole('administrador')) {
            Log::warning('Non-admin user or unauthenticated user attempted to view a user.', ['user_id' => $admin ? $admin->id : 'guest']);
            return response()->json(['message' => 'Acceso denegado. Solo administradores.'], 403);
        }

        Log::info('Admin user viewing user with ID: ' . $id, ['admin_id' => $admin->id]);
        $user = User::with('roles')->find($id);

        if (!$user) {
            Log::warning('User not found by admin.', ['user_id' => $id, 'admin_id' => $admin->id]);
            return response()->json(['message' => 'Usuario no encontrado'], 404);
        }

        return response()->json($user);
    }

    /**
     * Update the specified user in storage.
     * Only accessible by 'admin' role.
     *
     * @param  \Illuminate\Http\Request  $request
     * @param  int  $id
     * @return \Illuminate\Http\JsonResponse
     */
    public function update(Request $request, $id)
    {
        $admin = Auth::user();
        if (!$admin || !$admin->hasRole('administrador')) {
            Log::warning('Non-admin user or unauthenticated user attempted to update a user.', ['user_id' => $admin ? $admin->id : 'guest']);
            return response()->json(['message' => 'Acceso denegado. Solo administradores.'], 403);
        }

        Log::info('Admin user attempting to update user with ID: ' . $id, ['admin_id' => $admin->id]);

        try {
            $user = User::find($id);

            if (!$user) {
                Log::warning('User not found for update by admin.', ['user_id' => $id, 'admin_id' => $admin->id]);
                return response()->json(['message' => 'Usuario no encontrado'], 404);
            }

            // No permitir que un admin se despoje a sí mismo del rol de admin accidentalmente
            if ($user->id === $admin->id && isset($request->role_names) && !in_array('administrador', $request->role_names)) {
                Log::warning('Admin attempted to remove own admin role.', ['admin_id' => $admin->id]);
                return response()->json(['message' => 'No puedes quitarte a ti mismo el rol de administrador.'], 403);
            }

            $validatedData = $request->validate([
                'name' => 'sometimes|required|string|max:255',
                'last_name' => 'sometimes|required|string|max:255',
                'number' => 'sometimes|required|string|max:20',
                'email' => 'sometimes|required|email|unique:users,email,' . $id,
                'password' => 'nullable|min:6', // Contraseña opcional para actualizar
                'role_names' => 'nullable|array', // Array de nombres de roles para actualizar
                'role_names.*' => 'string|exists:roles,name',
            ]);
            Log::info('Validated data for user update by admin.', $validatedData);
            Log::info('Raw request data:', $request->all()); // Debug: datos crudos recibidos

            // Actualizar campos del usuario
            if (isset($validatedData['password'])) {
                $validatedData['password'] = Hash::make($validatedData['password']);
            } else {
                unset($validatedData['password']); // No actualizar si no se envía
            }
            $user->update($validatedData);

            // Actualizar roles del usuario
            if (isset($validatedData['role_names'])) {
                Log::info('Updating roles for user.', ['user_id' => $user->id, 'role_names' => $validatedData['role_names']]);
                $roles = Role::whereIn('name', $validatedData['role_names'])->get();
                Log::info('Found roles in database:', ['roles' => $roles->pluck('name')->toArray()]);
                $user->roles()->sync($roles->pluck('id'));
                Log::info('Roles updated for user.', ['user_id' => $user->id, 'roles' => $roles->pluck('name')->toArray()]);
            } else {
                Log::info('No role_names provided, skipping role update.');
            }

            // Recargar el usuario con sus roles para la respuesta
            $user->load('roles');
            return response()->json($user);

        } catch (ValidationException $e) {
            Log::error('Validation error when updating user by admin.', ['errors' => $e->errors()]);
            return response()->json(['message' => 'Validation failed', 'errors' => $e->errors()], 422);
        } catch (\Exception $e) {
            Log::error('Error updating user by admin: ' . $e->getMessage(), ['exception' => $e]);
            return response()->json(['message' => 'Internal server error'], 500);
        }
    }

    /**
     * Remove the specified user from storage.
     * Only accessible by 'admin' role.
     *
     * @param  int  $id
     * @return \Illuminate\Http\JsonResponse
     */
    public function destroy($id)
    {
        $admin = Auth::user();
        if (!$admin || !$admin->hasRole('administrador')) {
            Log::warning('Non-admin user or unauthenticated user attempted to delete a user.', ['user_id' => $admin ? $admin->id : 'guest']);
            return response()->json(['message' => 'Acceso denegado. Solo administradores.'], 403);
        }

        Log::info('Admin user attempting to delete user with ID: ' . $id, ['admin_id' => $admin->id]);

        try {
            $user = User::find($id);

            if (!$user) {
                Log::warning('User not found for deletion by admin.', ['user_id' => $id, 'admin_id' => $admin->id]);
                return response()->json(['message' => 'Usuario no encontrado'], 404);
            }

            // No permitir que un admin se elimine a sí mismo
            if ($user->id === $admin->id) {
                Log::warning('Admin attempted to delete self.', ['admin_id' => $admin->id]);
                return response()->json(['message' => 'No puedes eliminar tu propia cuenta de administrador.'], 403);
            }

            $user->delete(); // Esto también eliminará las entradas en tablas pivote (role_user, course_user) si onDelete('cascade')
            Log::info('User deleted successfully by admin.', ['user_id' => $id, 'admin_id' => $admin->id]);
            return response()->json(['message' => 'Usuario eliminado exitosamente']);

        } catch (\Exception $e) {
            Log::error('Error deleting user by admin: ' . $e->getMessage(), ['exception' => $e]);
            return response()->json(['message' => 'Error al eliminar el usuario'], 500);
        }
    }
}
