<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use App\Models\User; 
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Hash;
use App\Mail\VerificationCodeMail; 
use Illuminate\Support\Facades\Mail;
use Carbon\Carbon; 
use Illuminate\Support\Facades\Log;
    
    class AuthController extends Controller
{
    
    public function register(Request $request)
    {
        
        Log::info('Inicio del proceso de registro.');

        
        try {
            $validatedData = $request->validate([
                'name' => 'required|string|max:255', 
                'email' => 'required|email|unique:users', 
                'password' => 'required|min:6|confirmed',
            ]);
            Log::info('Datos de registro validados correctamente.', $validatedData);

        } catch (\Illuminate\Validation\ValidationException $e) {
            
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
            ]);
            Log::info('Usuario creado exitosamente.', ['user_id' => $user->id, 'email' => $user->email]);

        } catch (\Exception $e) {
            
            Log::error('Error al crear el usuario en la base de datos: ' . $e->getMessage(), ['exception' => $e]);
            return response()->json(['message' => 'Error al crear el usuario.'], 500);
        }


        
        
        Log::info('Registro exitoso. Devolviendo respuesta 201 JSON.');
        return response()->json(['message' => 'Usuario registrado correctamente'], 201);
    }

    
    public function login(Request $request)
    {
        
        $request->validate([
            'email' => 'required|email',
            'password' => 'required',
        ]);

        
        if (!Auth::attempt($request->only('email', 'password'))) {
            
            return response()->json(['message' => 'Credenciales inválidas'], 401);
        }

        
        $user = Auth::user(); 

        

        
        $verificationCode = rand(100000, 999999); 

        
        $expiresAt = Carbon::now()->addMinutes(10);

        
        
        $user->update([
            'two_factor_code' => $verificationCode,
            'two_factor_expires_at' => $expiresAt,
        ]);

        
        try {
            Mail::to($user->email)->send(new VerificationCodeMail($verificationCode));
        } catch (\Exception $e) {
            
            
            \Log::error("Error sending 2FA email: " . $e->getMessage()); 
            return response()->json(['message' => 'Error al enviar el código de verificación. Por favor, inténtelo de nuevo.'], 500);
        }

        
        
        return response()->json([
            'message' => 'Inicio de sesión exitoso. Se ha enviado un código de verificación a su correo.',
            'requires_2fa' => true, 
            'email' => $user->email 
        ], 200); 
    }

    
    public function verifyCode(Request $request)
    {
        
        $request->validate([
            'email' => 'required|email',
            'code' => 'required|integer|digits:6', 
        ]);

        
        $user = User::where('email', $request->email)->first(); 

        
        
        if (!$user || (int)$request->code !== (int)$user->two_factor_code || Carbon::now()->isAfter($user->two_factor_expires_at)) {
            
            return response()->json(['message' => 'Código de verificación inválido o expirado'], 401);
        }

        

        
        $user->update([
            'two_factor_code' => null,
            'two_factor_expires_at' => null,
        ]);

        
        $token = $user->createToken('auth_token')->plainTextToken;

        
        return response()->json([
            'message' => 'Código verificado exitosamente',
            'token' => $token,
            'user' => $user, 
        ], 200);
    }

    
    public function user(Request $request)
    {
        
        return response()->json($request->user());
    }

    
    public function logout(Request $request)
    {
        
        $request->user()->currentAccessToken()->delete();

        
        return response()->json(['message' => 'Cierre de sesión exitoso']);
    }
}
