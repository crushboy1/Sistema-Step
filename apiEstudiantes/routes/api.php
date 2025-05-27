<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;

use App\Http\Controllers\Api\AuthApiController;
use App\Http\Controllers\Api\EstudianteApiController;
use App\Http\Controllers\Api\CursoApiController;
use App\Http\Controllers\Api\UserController;
use App\Http\Controllers\EstudianteSoapController;
use App\Http\Controllers\CursoSoapController;


Route::post('/register', [AuthApiController::class, 'register']);
Route::post('/login', [AuthApiController::class, 'login']);
Route::post('/verifyCode', [AuthApiController::class, 'verifyCode']);
Route::post('/resendCode', [AuthApiController::class, 'resendCode']);
Route::middleware('auth:sanctum')->group(function () {
    
    Route::post('/logout', [AuthApiController::class, 'logout']);
    Route::get('/user', [AuthApiController::class, 'user']);

    
    Route::prefix('v1')->group(function () {

        
        Route::get('estudiantes', [EstudianteApiController::class, 'index']); 
        Route::post('estudiantes', [EstudianteApiController::class, 'store']); 
        Route::get('estudiantes/{id}', [EstudianteApiController::class, 'show']); 
        Route::put('estudiantes/{id}', [EstudianteApiController::class, 'update']); 
        Route::delete('estudiantes/{id}', [EstudianteApiController::class, 'destroy']); 
        
        Route::post('estudiantes/{id}/asignar-curso', [EstudianteApiController::class, 'asignarCurso']);
        Route::put('estudiantes/{id}/actualizar-curso/{cursoId}', [EstudianteApiController::class, 'actualizarCurso']);


        
        Route::apiResource('cursos', CursoApiController::class); 
        Route::prefix('admin')->group(function () {
        Route::apiResource('users', UserController::class);
    });
        
       // Route::post('/soap', [EstudianteSoapController::class, 'index']); 
       // Route::post('soap_cursos', [CursoSoapController::class, 'index']); 

    });

    
    

});






