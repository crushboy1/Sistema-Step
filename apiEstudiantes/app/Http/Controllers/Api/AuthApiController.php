<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\User; 
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Auth;
use App\Mail\VerificationCodeMail; 
use Illuminate\Support\Facades\Mail;
use Carbon\Carbon; 
use Illuminate\Support\Facades\Log; 
use Illuminate\Validation\ValidationException; 

class AuthApiController extends Controller
{
    
    public function register(Request $request)
    {
        Log::info('Inicio del proceso de registro.');
        Log::info('Datos recibidos para registro.', $request->all());

        
        try {
            
            $validatedData = $request->validate([
                'name' => 'required|string|max:100', 
                
                'email' => 'required|email|unique:users', 
                'password' => 'required|min:6|confirmed', 
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
            
            $usuario = User::create([
                'name' => $validatedData['name'], 
                'email' => $validatedData['email'],
                
                'password' => Hash::make($validatedData['password']), 
                
            ]);
            Log::info('Usuario creado exitosamente.', ['user_id' => $usuario->id ?? 'N/A', 'email' => $usuario->email]); 

        } catch (\Exception $e) {
            Log::error('Error al crear el usuario en la base de datos: ' . $e->getMessage(), ['exception' => $e]);
            return response()->json(['message' => 'Error al crear el usuario.'], 500);
        }

        
        Log::info('Registro exitoso. Devolviendo respuesta 201 JSON.');
        return response()->json([
            'message' => 'Usuario registrado exitosamente.',
            'user' => $usuario,
        ], 201);
    }

    
    public function login(Request $request)
    {
        Log::info('Inicio del proceso de login.');
        Log::info('Datos recibidos para login.', $request->only('email')); 

        
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
        
        Log::info('Intentando autenticar usuario con Auth::attempt.');
        
        if (!Auth::attempt(['email' => $credentials['email'], 'password' => $credentials['password']])) {
            Log::warning('Autenticación fallida para el email: ' . $credentials['email']);
            
            return response()->json(['message' => 'Credenciales inválidas'], 401);
        }

        
        $user = Auth::user(); 
        Log::info('Usuario autenticado exitosamente.', ['user_id' => $user->id, 'email' => $user->email]);

        
        Log::info('Iniciando proceso 2FA para usuario: ' . $user->email);

        
        if ($user->requiresTwoFactorAuthentication()) {
             Log::info('Usuario requiere 2FA.');

            
            $verificationCode = $user->generateTwoFactorCode();
            Log::info('Código 2FA generado y guardado.', ['code' => $verificationCode]);

            
            try {
                Log::info('Intentando enviar correo 2FA a: ' . $user->email);
                $user->sendTwoFactorCodeNotification($verificationCode);
                Log::info('Correo 2FA enviado exitosamente.');
            } catch (\Exception $e) {
                
                \Log::error("Error sending 2FA email: " . $e->getMessage(), ['exception' => $e]); 
                return response()->json(['message' => 'Error al enviar el código de verificación. Por favor, inténtelo de nuevo.'], 500);
            }

            
            Log::info('Login exitoso, se requiere 2FA. Devolviendo respuesta 200 JSON.');
            return response()->json([
                'message' => 'Inicio de sesión exitoso. Se ha enviado un código de verificación a su correo.',
                'requires_2fa' => true, 
                'email' => $user->email 
            ], 200); 

        } else {
            
            Log::info('Usuario NO requiere 2FA. Generando token Sanctum directamente.');
            $token = $user->createToken('auth_token')->plainTextToken;
            Log::info('Token Sanctum generado.');

            
            Log::info('Login exitoso sin 2FA. Devolviendo respuesta 200 JSON con token.');
             return response()->json([
                'message' => 'Inicio de sesión exitoso.',
                'token' => $token,
                'user' => $user, 
            ], 200);
        }
    }

    
    public function verifyCode(Request $request)
    {
        Log::info('Inicio del proceso de verificación de código 2FA.');
        Log::info('Datos recibidos para verificación.', $request->all());

        
        try {
            $request->validate([
                'email' => 'required|email',
                'code' => 'required|integer|digits:6', 
            ]);
            Log::info('Datos de verificación validados.');

        } catch (ValidationException $e) {
            Log::error('Error de validación en la verificación de código 2FA.', ['errors' => $e->errors()]);
            return response()->json(['message' => 'Error de validación', 'errors' => $e->errors()], 422);
        } catch (\Exception $e) {
            Log::error('Excepción inesperada durante la validación de código 2FA: ' . $e->getMessage(), ['exception' => $e]);
            return response()->json(['message' => 'Error interno del servidor durante la validación.'], 500);
        }
    
        Log::info('Buscando usuario para verificación de código: ' . $request->email);      
        $user = User::where('email', $request->email)->first();
        Log::info('Resultado de búsqueda de usuario.', ['user_found' => $user ? true : false]);
        Log::info('Verificando código y expiración.');
        if (!$user || (int)$request->code !== (int)$user->two_factor_code || ( $user->two_factor_expires_at && Carbon::now()->isAfter($user->two_factor_expires_at) ) ) {
            Log::warning('Verificación de código 2FA fallida.', [
                'user_exists' => $user ? true : false,
                'code_match' => $user ? ((int)$request->code === (int)$user->two_factor_code) : 'N/A',
                'expired' => $user ? ($user->two_factor_expires_at && Carbon::now()->isAfter($user->two_factor_expires_at)) : 'N/A'
            ]);
            
            return response()->json(['message' => 'Código de verificación inválido o expirado'], 401);
        }

        
        Log::info('Verificación de código 2FA exitosa para usuario: ' . $user->email);

        
        try {
            $user->update([
                'two_factor_code' => null,
                'two_factor_expires_at' => null,
            ]);
            Log::info('Código 2FA y expiración limpiados en la base de datos.');
        } catch (\Exception $e) {
            Log::error('Error al limpiar código 2FA en la base de datos: ' . $e->getMessage(), ['exception' => $e]);
            
            
        }


        
        Log::info('Generando token Sanctum para usuario: ' . $user->email);
        $token = $user->createToken('auth_token')->plainTextToken;
        Log::info('Token Sanctum generado.');

        
        Log::info('Verificación de código 2FA completa. Devolviendo respuesta 200 JSON con token.');
        return response()->json([
            'message' => 'Código verificado exitosamente',
            'token' => $token,
            'user' => $user, 
        ], 200);
    }

    
    public function resendCode(Request $request)
    {
        Log::info('Inicio del proceso de reenvío de código 2FA.');
        Log::info('Datos recibidos para reenvío.', $request->all());

        
        try {
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


        
        Log::info('Buscando usuario para reenvío de código: ' . $request->email);
        
        $user = User::where('email', $request->email)->first();
        Log::info('Resultado de búsqueda de usuario para reenvío.', ['user_found' => $user ? true : false]);


        
        if (!$user) {
            Log::warning('Intento de reenvío de código para usuario no encontrado: ' . $request->email);
            return response()->json(['message' => 'Usuario no encontrado.'], 404);
        }

        
        Log::info('Generando y enviando NUEVO código 2FA para usuario: ' . $user->email);

        
        $verificationCode = $user->generateTwoFactorCode();
        Log::info('Nuevo código 2FA generado y guardado.', ['code' => $verificationCode]);


        
        try {
            Log::info('Intentando enviar NUEVO correo 2FA a: ' . $user->email);
            $user->sendTwoFactorCodeNotification($verificationCode);
            Log::info('NUEVO correo 2FA enviado exitosamente.');
        } catch (\Exception $e) {
            
            \Log::error("Error sending 2FA resend email: " . $e->getMessage(), ['exception' => $e]);
            return response()->json(['message' => 'Error al reenviar el código de verificación. Por favor, inténtelo de nuevo.'], 500);
        }

        
        Log::info('Reenvío de código 2FA exitoso. Devolviendo respuesta 200 JSON.');
        return response()->json(['message' => 'Se ha reenviado un nuevo código de verificación a su correo.'], 200);
    }


    
    public function user(Request $request)
    {
        Log::info('Acceso a ruta protegida /user.');
        
        $user = $request->user();
        Log::info('Usuario autenticado obtenido.', ['user_id' => $user->id, 'email' => $user->email]);
        return response()->json($user);
    }


    
    public function logout(Request $request)
    {
        Log::info('Inicio del proceso de logout.');
        $user = $request->user(); 
        Log::info('Usuario solicitando logout.', ['user_id' => $user->id, 'email' => $user->email]);

        
        try {
            $request->user()->currentAccessToken()->delete();
            Log::info('Token de acceso actual revocado para usuario: ' . $user->email);
        } catch (\Exception $e) {
            Log::error('Error al revocar token de acceso actual: ' . $e->getMessage(), ['exception' => $e]);
            
        }


        
        Log::info('Logout exitoso. Devolviendo respuesta 200 JSON.');
        return response()->json([
            'message' => 'Sesión cerrada exitosamente.',
        ], 200);
    }
}


