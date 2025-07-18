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
        // Crea la tabla 'ratings' para almacenar las calificaciones de los tutores.
        Schema::create('ratings', function (Blueprint $table) {
            $table->id(); // Columna de ID auto-incremental (clave primaria, BIGINT UNSIGNED).
            $table->foreignId('student_id')->constrained('users')->onDelete('cascade'); // ID del estudiante que califica, con clave foránea a la tabla 'users'.
            $table->foreignId('tutor_id')->constrained('users')->onDelete('cascade'); // ID del tutor calificado, con clave foránea a la tabla 'users'.

            // Cambiar session_id a unsignedBigInteger y apuntar a academic_sessions
            $table->unsignedBigInteger('session_id')->nullable(); // ID de la sesión académica relacionada, opcional
            $table->foreign('session_id')
                  ->references('id')
                  ->on('academic_sessions')
                  ->onDelete('set null');

            $table->unsignedTinyInteger('rating'); // Valor de la calificación (ej. 1 a 5). unsignedTinyInteger es ideal para esto.
            $table->text('comment')->nullable(); // Comentario opcional del estudiante sobre la calificación.
            $table->timestamps(); // Columnas `created_at` y `updated_at` para registrar la fecha de creación y última actualización.

            // Añade una restricción única para asegurar que un estudiante solo califique a un tutor por sesión una vez (si session_id no es nulo).
            // Si session_id puede ser nulo, esta restricción debe ser más compleja o manejarse a nivel de aplicación.
            // Para este caso, asumimos que una calificación está ligada a una sesión específica.
            $table->unique(['student_id', 'tutor_id', 'session_id']);
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        // Elimina la tabla 'ratings' si se revierte la migración.
        Schema::dropIfExists('ratings');
    }
};

