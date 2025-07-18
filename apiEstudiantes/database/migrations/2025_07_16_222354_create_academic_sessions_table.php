<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        // Crea la tabla 'academic_sessions' para almacenar las sesiones de tutoría.
        Schema::create('academic_sessions', function (Blueprint $table) {
            $table->id(); // ID de la sesión académica (BIGINT UNSIGNED)

            // Claves foráneas para estudiante, tutor y curso
            $table->foreignId('student_id')->constrained('users')->onDelete('cascade'); // ID del estudiante
            $table->foreignId('tutor_id')->constrained('users')->onDelete('cascade'); // ID del tutor
            $table->foreignId('course_id')->constrained('courses')->onDelete('cascade'); // ID del curso relacionado

            $table->timestamp('start_time'); // Hora de inicio de la sesión
            $table->timestamp('end_time');   // Hora de fin de la sesión

            // Estado de la sesión (ej. 'scheduled', 'completed', 'cancelled', 'pending')
            $table->string('status')->default('scheduled');

            $table->text('notes')->nullable(); // Notas o descripción de la sesión

            $table->timestamps(); // created_at y updated_at

            // Opcional: Añadir un índice para búsquedas rápidas por estudiante o tutor
            $table->index(['student_id', 'tutor_id']);
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        // Elimina la tabla 'academic_sessions' si se revierte la migración.
        Schema::dropIfExists('academic_sessions');
    }
};

