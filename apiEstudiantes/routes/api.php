<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;

use App\Http\Controllers\Api\AuthApiController;
use App\Http\Controllers\Api\EstudianteApiController;
use App\Http\Controllers\Api\CursoApiController;
use App\Http\Controllers\Api\UserController;
use App\Http\Controllers\Api\RatingApiController; // <-- NUEVO: Importa el controlador de calificaciones

// Si usas controladores SOAP, asegúrate de que estén correctamente configurados.
// use App\Http\Controllers\EstudianteSoapController;
// use App\Http\Controllers\CursoSoapController;


// Rutas de autenticación (públicas, no requieren token)
Route::post('/register', [AuthApiController::class, 'register']);
Route::post('/login', [AuthApiController::class, 'login']);
Route::post('/verifyCode', [AuthApiController::class, 'verifyCode']);
Route::post('/resendCode', [AuthApiController::class, 'resendCode']);

// Rutas protegidas por autenticación Sanctum
Route::middleware('auth:sanctum')->group(function () {

    // Rutas de autenticación que requieren token
    Route::post('/logout', [AuthApiController::class, 'logout']);
    Route::get('/user', [AuthApiController::class, 'user']);

    // Grupo de rutas con prefijo 'v1'
    Route::prefix('v1')->group(function () {

        // Rutas para Estudiantes
        Route::get('estudiantes', [EstudianteApiController::class, 'index']);
        Route::post('estudiantes', [EstudianteApiController::class, 'store']);
        Route::get('estudiantes/{id}', [EstudianteApiController::class, 'show']);
        Route::put('estudiantes/{id}', [EstudianteApiController::class, 'update']);
        Route::delete('estudiantes/{id}', [EstudianteApiController::class, 'destroy']);

        Route::post('estudiantes/{id}/asignar-curso', [EstudianteApiController::class, 'asignarCurso']);
        Route::put('estudiantes/{id}/actualizar-curso/{cursoId}', [EstudianteApiController::class, 'actualizarCurso']);


        // Rutas para Cursos
        // apiResource cubre index, store, show, update, destroy.
        // Añadimos rutas específicas para la inscripción y listado de cursos del estudiante.
        Route::apiResource('cursos', CursoApiController::class);
        // Ruta para que un estudiante se registre/inscriba en un curso
        Route::post('cursos/{curso}/enroll', [CursoApiController::class, 'enroll']); // <-- NUEVO: Para inscribir a un estudiante
        // Ruta para que un estudiante vea los cursos en los que está inscrito
        Route::get('my-cursos', [CursoApiController::class, 'myCursos']); // <-- NUEVO: Para ver cursos inscritos por el usuario autenticado


        // Rutas de gestión de usuarios (solo para administradores, si aplica)
        Route::apiResource('users', UserController::class);

        // Rutas para Calificaciones (Ratings)
        // Estas rutas permitirán a los estudiantes calificar a los tutores.
        Route::post('ratings', [RatingApiController::class, 'store']); // <-- NUEVO: Crear una calificación
        Route::get('ratings', [RatingApiController::class, 'index']);  // <-- NUEVO: Listar calificaciones (puede filtrar)
        Route::get('ratings/{id}', [RatingApiController::class, 'show']); // <-- NUEVO: Ver una calificación específica

        // Rutas SOAP (descomentar si están en uso y configuradas)
        // Route::post('/soap', [EstudianteSoapController::class, 'index']);
        // Route::post('soap_cursos', [CursoSoapController::class, 'index']);

    });

});

