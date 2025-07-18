<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use App\Models\AcademicSession;
use Illuminate\Support\Facades\Auth;

class AcademicSessionApiController extends Controller
{
    /**
     * Lista sesiones académicas filtradas por estudiante o tutor.
     *
     * @param  \Illuminate\Http\Request  $request
     * @return \Illuminate\Http\JsonResponse
     */
    public function index(Request $request)
    {
        $query = AcademicSession::query();

        // Filtrar por estudiante
        if ($request->has('student_id')) {
            $query->where('student_id', $request->student_id);
        }
        // Filtrar por tutor
        if ($request->has('tutor_id')) {
            $query->where('tutor_id', $request->tutor_id);
        }
        // Opcional: solo sesiones finalizadas
        if ($request->has('only_finished') && $request->only_finished) {
            $query->whereNotNull('end_time');
        }

        // Incluir las relaciones con rating, tutor, student y course
        $sessions = $query->with(['rating', 'tutor', 'student', 'course'])->orderByDesc('start_time')->get();

        return response()->json([
            'status' => 'success',
            'data' => $sessions
        ], 200);
    }

    /**
     * Crea una nueva sesión académica.
     *
     * @param  \Illuminate\Http\Request  $request
     * @return \Illuminate\Http\JsonResponse
     */
    public function store(Request $request)
    {
        $user = Auth::user();
        if (!$user) {
            return response()->json(['message' => 'No autenticado.'], 401);
        }
        // Solo estudiantes o tutores pueden crear sesiones
        if (!$user->hasRole('estudiante') && !$user->hasRole('tutor')) {
            return response()->json(['message' => 'Solo estudiantes o tutores pueden agendar sesiones.'], 403);
        }
        $validated = $request->validate([
            'student_id' => 'required|exists:users,id',
            'tutor_id' => 'required|exists:users,id',
            'course_id' => 'required|exists:courses,id',
            'start_time' => 'required|date',
            'end_time' => 'nullable|date|after_or_equal:start_time',
            'notes' => 'nullable|string|max:500',
        ]);
        $session = AcademicSession::create($validated);
        return response()->json([
            'status' => 'success',
            'message' => 'Sesión académica creada exitosamente.',
            'data' => $session
        ], 201);
    }
} 