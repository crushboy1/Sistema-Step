<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use App\Models\User;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Mail;
use App\Mail\VerificationCodeMail; 
use Carbon\Carbon;
use Illuminate\Support\Facades\Log;
use Illuminate\Validation\ValidationException; 

class AuthApiController extends Controller
{
    /**
     * Maneja el registro de un nuevo usuario.
     *
     * @param  \Illuminate->Http->Request  $request
     * @return \Illuminate->Http->JsonResponse
     */
    public function register(Request $request)
    {
        Log::info('Inicio del proceso de registro.');

        try {
            $validatedData = $request->validate([
                'name' => 'required|string|max:255',
                'email' => 'required|email|unique:users',
                'password' => 'required|min:6|confirmed',
                // Puedes añadir 'last_name' y 'number' aquí si los usas en el registro
                // 'last_name' => 'required|string|max:255',
                // 'number' => 'required|string|max:20',
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
            $user = User::create([
                'name' => $validatedData['name'],
                'email' => $validatedData['email'],
                'password' => Hash::make($validatedData['password']),
                // Incluye aquí 'last_name', 'number', 'registered_ip' si los tienes en fillable
                // 'last_name' => $validatedData['last_name'] ?? null,
                // 'number' => $validatedData['number'] ?? null,
                // 'registered_ip' => $request->ip(),
                // Campos de 2FA y auditoría de login (asegúrate de que tengan un valor por defecto o se pasen como null)
                'two_factor_secret' => null,
                'two_factor_code' => null,
                'two_factor_expires_at' => null,
                'two_factor_enabled_at' => null, // Asegúrate de que tu migración permita null o tenga default(null)
                'two_factor_recovery_codes' => null,
                'last_login_at' => null,
                'last_login_ip' => null,
                'failed_login_attempts' => 0,
                'locked_until' => null,
                'password_changed_at' => Carbon::now(), // O null, dependiendo de tu lógica
                'last_login_user_agent' => null,
            ]);
            Log::info('Usuario creado exitosamente.', ['user_id' => $user->id, 'email' => $user->email]);

            // Opcional: Asignar un rol por defecto al nuevo usuario (ej. 'estudiante')
            // Asegúrate de importar \App\Models\Role si lo usas aquí
            // $defaultRole = \App\Models\Role::where('name', 'estudiante')->first();
            // if ($defaultRole) {
            //     $user->roles()->attach($defaultRole->id);
            //     Log::info('Rol "estudiante" asignado por defecto al nuevo usuario.', ['user_id' => $user->id]);
            // }

        } catch (\Exception $e) {
            Log::error('Error al crear el usuario en la base de datos: ' . $e->getMessage(), ['exception' => $e]);
            return response()->json(['message' => 'Error al crear el usuario.'], 500);
        }

        Log::info('Registro exitoso. Devolviendo respuesta 201 JSON.');
        return response()->json(['message' => 'Usuario registrado correctamente'], 201);
    }

    /**
     * Maneja el intento de login del usuario.
     *
     * @param  \Illuminate->Http->Request  $request
     * @return \Illuminate->Http->JsonResponse
     * @throws \Illuminate\Validation\ValidationException
     */
    public function login(Request $request)
    {
        $request->validate([
            'email' => 'required|email',
            'password' => 'required',
        ]);

        // Intentar autenticar al usuario
        if (!Auth::attempt($request->only('email', 'password'))) {
            throw ValidationException::withMessages([
                'email' => ['Las credenciales proporcionadas son incorrectas.'],
            ]);
        }

        $user = Auth::user(); // Obtener el usuario autenticado

        // Actualizar campos de auditoría de login
        $user->update([
            'last_login_at' => Carbon::now(),
            'last_login_ip' => $request->ip(),
            'last_login_user_agent' => $request->header('User-Agent'),
            'failed_login_attempts' => 0, // Resetear intentos fallidos
            'locked_until' => null, // Desbloquear si estaba bloqueado
        ]);
        Log::info('Login exitoso. Campos de auditoría actualizados.', ['user_id' => $user->id]);


        // Verificar si el 2FA está habilitado para este usuario
        // 'two_factor_enabled_at' indica si 2FA está activo (es un timestamp)
        if ($user->two_factor_enabled_at) {
            $verificationCode = rand(100000, 999999); // Generar un código de 6 dígitos
            // Obtener el tiempo de expiración de la configuración, por defecto 10 minutos
            $expiresAt = Carbon::now()->addMinutes(config('auth.two_factor_code_expiration', 10));

            // Actualizar el usuario con el nuevo código 2FA y su expiración
            $user->update([
                'two_factor_code' => $verificationCode,
                'two_factor_expires_at' => $expiresAt,
            ]);
            Log::info('Código 2FA generado y guardado.', ['code' => $verificationCode]);

            // Enviar el código por correo electrónico
            try {
                Log::info('Intentando enviar correo 2FA a: ' . $user->email);
                Mail::to($user->email)->send(new VerificationCodeMail($verificationCode));
                Log::info('Correo 2FA enviado exitosamente.');
            } catch (\Exception $e) {
                Log::error("Error al enviar el correo 2FA para el usuario {$user->id}: " . $e->getMessage(), ['exception' => $e]);
                return response()->json(['message' => 'Error al enviar el código de verificación. Por favor, inténtelo de nuevo.'], 500);
            }

            // Devolver respuesta indicando que se requiere 2FA
            return response()->json([
                'message' => 'Inicio de sesión exitoso. Se ha enviado un código de verificación a su correo.',
                'requires_2fa' => true,
                'email' => $user->email, // Devolver el email para que Flask lo use en la verificación 2FA
            ], 200);
        }

        // Si el 2FA NO está habilitado, generar el token y devolverlo directamente
        $token = $user->createToken('auth_token')->plainTextToken;
        Log::info('Inicio de sesión exitoso sin 2FA para ' . $user->email, ['user_id' => $user->id]);

        return response()->json([
            'message' => 'Inicio de sesión exitoso.',
            'token' => $token,
            'requires_2fa' => false,
            'user' => $user->load('roles'), // Devolver el objeto user completo con roles
        ], 200);
    }

    /**
     * Verifica el código de dos factores.
     *
     * @param  \Illuminate->Http->Request  $request
     * @return \Illuminate->Http->JsonResponse
     * @throws \Illuminate->Validation\ValidationException
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
            'user' => $user->load('roles'), // Cargar los roles para que Flask los tenga
        ], 200);
    }

    /**
     * Reenvía el código de dos factores.
     *
     * @param  \Illuminate->Http->Request  $request
     * @return \Illuminate->Http->JsonResponse
     * @throws \Illuminate\Validation\ValidationException
     */
    public function resendCode(Request $request)
    {
        $request->validate([
            'email' => 'required|email',
        ]);

        $user = User::where('email', $request->email)->first();

        // Asegurarse de que el usuario existe y tiene 2FA habilitado
        if (!$user || !$user->two_factor_enabled_at) {
            throw ValidationException::withMessages([
                'email' => ['No se puede reenviar el código. El usuario no existe o no tiene 2FA habilitado.'],
            ]);
        }

        // Generar un nuevo código 2FA
        $verificationCode = rand(100000, 999999);
        $expiresAt = Carbon::now()->addMinutes(config('auth.two_factor_code_expiration', 10));

        $user->update([
            'two_factor_code' => $verificationCode,
            'two_factor_expires_at' => $expiresAt,
        ]);

        // Enviar el nuevo código por correo electrónico
        try {
            Mail::to($user->email)->send(new VerificationCodeMail($verificationCode));
            Log::info('Código 2FA reenviado a ' . $user->email, ['user_id' => $user->id]);
        } catch (\Exception $e) {
            Log::error("Error al reenviar el correo 2FA para el usuario {$user->id}: " . $e->getMessage(), ['exception' => $e]);
            return response()->json(['message' => 'Error al reenviar el código de verificación. Por favor, inténtelo de nuevo.'], 500);
        }

        return response()->json(['message' => 'Nuevo código de verificación enviado a su correo.']);
    }

    /**
     * Obtiene los datos del usuario autenticado.
     *
     * @param  \Illuminate->Http->Request  $request
     * @return \Illuminate->Http->JsonResponse
     */
    public function user(Request $request)
    {
        // El usuario autenticado está disponible a través de $request->user()
        // Asegúrate de cargar las relaciones necesarias, como los roles
        return response()->json($request->user()->load('roles')); // Cargar los roles para que Flask los tenga
    }

    /**
     * Invalida el token del usuario (logout).
     *
     * @param  \Illuminate->Http->Request  $request
     * @return \Illuminate->Http->JsonResponse
     */
    public function logout(Request $request)
    {
        // Revocar el token actual del usuario autenticado
        $request->user()->currentAccessToken()->delete();
        Log::info('Usuario ' . $request->user()->email . ' ha cerrado sesión.', ['user_id' => $request->user()->id]);

        return response()->json(['message' => 'Cierre de sesión exitoso']);
    }
}
