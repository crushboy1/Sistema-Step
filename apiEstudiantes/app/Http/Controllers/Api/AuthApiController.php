<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use App\Models\User; // Asegúrate de que este import está correcto
use App\Models\Role; // ¡Importante! Asegúrate de importar el modelo Role
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Hash;
use App\Mail\VerificationCodeMail; // Asegúrate de que esta clase de Mail existe
use Illuminate\Support\Facades\Mail;
use Carbon\Carbon; // Para trabajar con fechas y horas
use Illuminate\Support\Facades\Log; // Para registrar eventos y errores
use Illuminate\Validation\ValidationException; // Para manejar errores de validación

class AuthApiController extends Controller
{
    /**
     * Registra un nuevo usuario en la aplicación.
     *
     * @param Request $request
     * @return \Illuminate\Http\JsonResponse
     */
    public function register(Request $request)
    {
        Log::info('Inicio del proceso de registro.');
    Log::info('Datos recibidos para registro.', $request->all());

    // --- AÑADE ESTAS LÍNEAS PARA DEPURACIÓN ---
    Log::info('Contenido de password: ' . $request->input('password'));
    Log::info('Contenido de password_confirmation: ' . $request->input('password_confirmation'));
    // --- FIN DE LÍNEAS DE DEPURACIÓN ---

        try {
            // 1. Validación de los datos de entrada
            // Se han añadido 'last_name', 'number' y 'role' a la validación.
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
                'role' => 'required|string|in:tutor,estudiante', 
            ]);
            Log::info('Datos de registro validados correctamente.', $validatedData);

        } catch (ValidationException $e) {
            Log::error('Error de validación en el registro.', ['errors' => $e->errors()]);
            return response()->json(['message' => 'Error de validación', 'errors' => $e->errors()], 422);
        } catch (\Exception $e) {
            Log::error('Excepción inesperada durante la validación del registro: ' . $e->getMessage(), ['exception' => $e]);
            return response()->json(['message' => 'Error interno del servidor durante la validación.'], 500);
        }

        try {
            // 2. Creación del usuario en la base de datos
            // Incluimos todos los campos del usuario que definimos en el modelo User
            $user = User::create([
                'name' => $validatedData['name'],
                'last_name' => $validatedData['last_name'], // Guardar apellidos
                'number' => $validatedData['number'],       // Guardar teléfono
                'email' => $validatedData['email'],
                'password' => Hash::make($validatedData['password']),
                'registered_ip' => $request->ip(), // Registrar la IP desde donde se registra
                'password_changed_at' => Carbon::now(), // Marca cuándo se estableció la contraseña
                // 'two_factor_enabled' por defecto es false si no se envía o si quieres que se active manualmente después
                // Los demás campos como 'two_factor_code', 'two_factor_expires_at', 'failed_login_attempts', etc.
                // se inicializan a null o 0 en la migración por defecto.
            ]);
            Log::info('Usuario creado exitosamente.', ['user_id' => $user->id, 'email' => $user->email]);

            // 3. Asignación del rol al usuario
            // Busca el rol por su nombre ('tutor' o 'estudiante') y lo adjunta al usuario.
            $role = Role::where('name', $validatedData['role'])->first();
            if ($role) {
                $user->roles()->attach($role->id); // Asigna el rol al usuario usando la relación BelongsToMany
                Log::info('Rol asignado al usuario.', ['user_id' => $user->id, 'role' => $role->name]);
            } else {
                Log::warning('Rol no encontrado para asignación.', ['role_name' => $validatedData['role']]);
                // Si el rol no existe, podrías considerar eliminar el usuario o registrar un error crítico.
            }

        } catch (\Exception $e) {
            Log::error('Error al crear el usuario o asignar el rol en la base de datos: ' . $e->getMessage(), ['exception' => $e]);
            return response()->json(['message' => 'Error al crear el usuario.'], 500);
        }

        Log::info('Registro exitoso. Devolviendo respuesta 201 JSON.');
        return response()->json(['message' => 'Usuario registrado exitosamente.'], 201);
    }

    /**
     * Maneja el proceso de inicio de sesión de usuarios.
     * Implementa la autenticación de doble factor y actualiza campos de auditoría.
     *
     * @param Request $request
     * @return \Illuminate\Http\JsonResponse
     */
    public function login(Request $request)
    {
        Log::info('Inicio del proceso de login para: ' . $request->email);

        // 1. Validación de credenciales
        try {
            $credentials = $request->validate([
                'email' => 'required|email',
                'password' => 'required',
            ]);
            Log::info('Credenciales de login validadas.');

        } catch (ValidationException $e) {
            Log::error('Error de validación en el login.', ['errors' => $e->errors()]);
            return response()->json(['message' => 'Error de validación', 'errors' => $e->errors()], 422);
        } catch (\Exception $e) {
            Log::error('Excepción inesperada durante la validación del login: ' . $e->getMessage(), ['exception' => $e]);
            return response()->json(['message' => 'Error interno del servidor durante la validación.'], 500);
        }

        // 2. Intentar autenticar al usuario
        if (!Auth::attempt(['email' => $credentials['email'], 'password' => $credentials['password']])) {
            Log::warning('Autenticación fallida para el email: ' . $credentials['email']);

            // Si las credenciales son inválidas, busca al usuario y incrementa el contador de intentos fallidos
            $user = User::where('email', $request->email)->first();
            if ($user) {
                // Incrementa el contador de intentos fallidos
                $user->increment('failed_login_attempts');
                // Bloqueo temporal de la cuenta si hay muchos intentos fallidos
                //  lógica para $user->locked_until
                    if ($user->failed_login_attempts >= config('auth.max_login_attempts', 3)) {
                        $user->locked_until = Carbon::now()->addMinutes(config('auth.lockout_time', 15));
                        $user->save();
                    Log::warning('Cuenta bloqueada por múltiples intentos fallidos.', ['email' => $user->email]);
                    return response()->json(['message' => 'Demasiados intentos de inicio de sesión. Su cuenta ha sido bloqueada temporalmente.'], 403);
                }
            }
            return response()->json(['message' => 'Credenciales inválidas'], 401);
        }

        // 3. Autenticación exitosa
        $user = Auth::user();
        Log::info('Usuario autenticado exitosamente.', ['user_id' => $user->id, 'email' => $user->email]);

        // Si la autenticación es exitosa, reinicia el contador de intentos fallidos
        if ($user->failed_login_attempts > 0) {
            $user->failed_login_attempts = 0;
            $user->save();
        }

        // 4. Actualizar campos de auditoría de login
        $user->update([
            'last_login_at' => Carbon::now(),
            'last_login_ip' => $request->ip(),
            'last_login_user_agent' => $request->header('User-Agent'),
        ]);
        Log::info('Login exitoso. Campos de auditoría actualizados.', ['user_id' => $user->id]);


        // 5. Generar y enviar código de verificación 2FA (si aplica)
        Log::info('Iniciando proceso 2FA para usuario: ' . $user->email);
        // El método requiresTwoFactorAuthentication() está en el modelo User
        if ($user->requiresTwoFactorAuthentication()) {
            Log::info('Usuario requiere 2FA.');

            $verificationCode = $user->generateTwoFactorCode(); // Método en el modelo User
            Log::info('Código 2FA generado y guardado.', ['code' => $verificationCode]);

            try {
                Log::info('Intentando enviar correo 2FA a: ' . $user->email);
                $user->sendTwoFactorCodeNotification($verificationCode); // Método en el modelo User
                Log::info('Correo 2FA enviado exitosamente.');
            } catch (\Exception $e) {
                Log::error("Error al enviar el correo 2FA: " . $e->getMessage(), ['exception' => $e, 'user_id' => $user->id]);
                return response()->json(['message' => 'Error al enviar el código de verificación. Por favor, inténtelo de nuevo.'], 500);
            }

            // Devolver respuesta indicando que se requiere 2FA
            Log::info('Login exitoso, se requiere 2FA. Devolviendo respuesta 200 JSON.');
            return response()->json([
                'message' => 'Inicio de sesión exitoso. Se ha enviado un código de verificación a su correo.',
                'requires_2fa' => true,
                'email' => $user->email // Devolvemos el email para que el frontend sepa a qué cuenta verificar
            ], 200);

        } else {
            // Si el usuario NO requiere 2FA, se genera y devuelve el token directamente
            Log::info('Usuario NO requiere 2FA. Generando token Sanctum directamente.');
            $token = $user->createToken('auth_token')->plainTextToken;
            Log::info('Token Sanctum generado.');

            // Devolver respuesta con el token y datos del usuario
            Log::info('Login exitoso sin 2FA. Devolviendo respuesta 200 JSON con token.');
            return response()->json([
                'message' => 'Inicio de sesión exitoso.',
                'token' => $token,
                'user' => $user, // Puedes devolver el objeto usuario si lo necesitas en el frontend
            ], 200);
        }
    }

    /**
     * Verifica el código de autenticación de doble factor (2FA).
     *
     * @param Request $request
     * @return \Illuminate\Http\JsonResponse
     */
    public function verifyCode(Request $request)
    {
        Log::info('Inicio del proceso de verificación de código 2FA.');
        Log::info('Datos recibidos para verificación.', $request->all());

        try {
            // 1. Validación de los datos de entrada (email y código)
            // CAMBIO CLAVE AQUÍ: Se espera 'two_factor_code' en lugar de 'code'
            $request->validate([
                'email' => 'required|email',
                'two_factor_code' => 'required|string|digits:6', // El código debe ser una cadena de 6 dígitos
            ]);
            Log::info('Datos de verificación validados.');

        } catch (ValidationException $e) {
            Log::error('Error de validación en la verificación de código 2FA.', ['errors' => $e->errors()]);
            return response()->json(['message' => 'Error de validación', 'errors' => $e->errors()], 422);
        } catch (\Exception $e) {
            Log::error('Excepción inesperada durante la validación de código 2FA: ' . $e->getMessage(), ['exception' => $e]);
            return response()->json(['message' => 'Error interno del servidor durante la validación.'], 500);
        }

        // 2. Buscar al usuario por email
        Log::info('Buscando usuario para verificación de código: ' . $request->email);
        $user = User::where('email', $request->email)->first();
        Log::info('Resultado de búsqueda de usuario.', ['user_found' => $user ? true : false]);

        // 3. Verificar si el usuario existe, el código coincide y no ha expirado
        Log::info('Verificando código y expiración.');
        // CAMBIO CLAVE AQUÍ: Se compara $request->two_factor_code con $user->two_factor_code
        if (!$user || (string)$request->two_factor_code !== (string)$user->two_factor_code || ($user->two_factor_expires_at && Carbon::now()->isAfter($user->two_factor_expires_at))) {
            Log::warning('Verificación de código 2FA fallida.', [
                'user_exists' => $user ? true : false,
                'code_match' => $user ? ((string)$request->two_factor_code === (string)$user->two_factor_code) : 'N/A',
                'expired' => $user ? ($user->two_factor_expires_at && Carbon::now()->isAfter($user->two_factor_expires_at)) : 'N/A',
                'input_code' => $request->two_factor_code, // Para depuración
                'stored_code' => $user ? $user->two_factor_code : 'N/A', // Para depuración
                'stored_expires_at' => $user ? $user->two_factor_expires_at : 'N/A', // Para depuración
            ]);
            return response()->json(['message' => 'Código de verificación inválido o expirado'], 401);
        }

        // 4. Limpiar el código 2FA después de una verificación exitosa
        Log::info('Verificación de código 2FA exitosa para usuario: ' . $user->email);
        try {
            $user->update([
                'two_factor_code' => null,
                'two_factor_expires_at' => null,
            ]);
            Log::info('Código 2FA y expiración limpiados en la base de datos.');
        } catch (\Exception $e) {
            Log::error('Error al limpiar código 2FA en la base de datos: ' . $e->getMessage(), ['exception' => $e]);
            // No se devuelve un error crítico aquí, ya que la autenticación fue exitosa.
        }

        // 5. Generar token de autenticación de Sanctum
        Log::info('Generando token Sanctum para usuario: ' . $user->email);
        $token = $user->createToken('auth_token')->plainTextToken;
        Log::info('Token Sanctum generado.');

        // 6. Devolver respuesta con el token y datos del usuario
        Log::info('Verificación de código 2FA completa. Devolviendo respuesta 200 JSON con token y usuario.');
        return response()->json([
            'message' => 'Código verificado exitosamente',
            'token' => $token,
            'user' => $user->load('roles'),
        ], 200);
    }


    /**
     * Reenvía un nuevo código de verificación 2FA al correo del usuario.
     *
     * @param Request $request
     * @return \Illuminate\Http\JsonResponse
     */
    public function resendCode(Request $request)
    {
        Log::info('Inicio del proceso de reenvío de código 2FA.');
        Log::info('Datos recibidos para reenvío.', $request->all());

        try {
            // 1. Validación del email
            $request->validate([
                'email' => 'required|email',
            ]);
            Log::info('Email para reenvío validado.');

        } catch (ValidationException $e) {
            Log::error('Error de validación en el reenvío de código 2FA.', ['errors' => $e->errors()]);
            return response()->json(['message' => 'Error de validación', 'errors' => $e->errors()], 422);
        } catch (\Exception $e) {
            Log::error('Excepción inesperada durante la validación de reenvío de código 2FA: ' . $e->getMessage(), ['exception' => $e]);
            return response()->json(['message' => 'Error interno del servidor durante la validación.'], 500);
        }

        // 2. Buscar al usuario
        Log::info('Buscando usuario para reenvío de código: ' . $request->email);
        $user = User::where('email', $request->email)->first();
        Log::info('Resultado de búsqueda de usuario para reenvío.', ['user_found' => $user ? true : false]);

        // 3. Verificar si el usuario existe
        if (!$user) {
            Log::warning('Intento de reenvío de código para usuario no encontrado: ' . $request->email);
            return response()->json(['message' => 'Usuario no encontrado.'], 404);
        }

        // 4. Generar y enviar un nuevo código 2FA
        Log::info('Generando y enviando NUEVO código 2FA para usuario: ' . $user->email);
        $verificationCode = $user->generateTwoFactorCode(); // Método en el modelo User
        Log::info('Nuevo código 2FA generado y guardado.', ['code' => $verificationCode]);

        try {
            Log::info('Intentando enviar NUEVO correo 2FA a: ' . $user->email);
            $user->sendTwoFactorCodeNotification($verificationCode); // Método en el modelo User
            Log::info('NUEVO correo 2FA enviado exitosamente.');
        } catch (\Exception $e) {
            Log::error("Error al reenviar el correo 2FA: " . $e->getMessage(), ['exception' => $e]);
            return response()->json(['message' => 'Error al reenviar el código de verificación. Por favor, inténtelo de nuevo.'], 500);
        }

        Log::info('Reenvío de código 2FA exitoso. Devolviendo respuesta 200 JSON.');
        return response()->json(['message' => 'Se ha reenviado un nuevo código de verificación a su correo.'], 200);
    }


    /**
     * Obtiene los datos del usuario autenticado (requiere token Sanctum).
     *
     * @param Request $request
     * @return \Illuminate\Http\JsonResponse
     */
    public function user(Request $request)
    {
        Log::info('Acceso a ruta protegida /user.');
        $user = $request->user(); // Esto obtendrá el usuario autenticado a través del token Sanctum
        Log::info('Usuario autenticado obtenido.', ['user_id' => $user->id, 'email' => $user->email]);
        
        // Cargar los roles del usuario para que estén disponibles en el frontend
        $user->load('roles');
        
        return response()->json($user);
    }

    /**
     * Cierra la sesión del usuario autenticado revocando su token de acceso actual.
     *
     * @param Request $request
     * @return \Illuminate\Http\JsonResponse
     */
    public function logout(Request $request)
    {
        Log::info('Inicio del proceso de logout.');
        $user = $request->user(); // Obtiene el usuario autenticado
        Log::info('Usuario solicitando logout.', ['user_id' => $user->id, 'email' => $user->email]);

        try {
            // Revoca solo el token que se está usando actualmente para la petición
            $request->user()->currentAccessToken()->delete();
            Log::info('Token de acceso actual revocado para usuario: ' . $user->email);
        } catch (\Exception $e) {
            Log::error('Error al revocar token de acceso actual: ' . $e->getMessage(), ['exception' => $e]);
            // No se devuelve un error 500 aquí, ya que el logout es un proceso de "mejor esfuerzo"
            // y no debería impedir que el usuario piense que ha cerrado sesión.
        }

        Log::info('Logout exitoso. Devolviendo respuesta 200 JSON.');
        return response()->json([
            'message' => 'Sesión cerrada exitosamente.',
        ], 200);
    }
}