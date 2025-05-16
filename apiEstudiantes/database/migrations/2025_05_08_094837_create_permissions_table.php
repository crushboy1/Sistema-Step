<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('permissions', function (Blueprint $table) {
            $table->id();
            // Nombre único para el permiso (ej. 'view_courses', 'create_course', 'edit_student')
            $table->string('name')->unique();
            // Nombre legible para mostrar (ej. 'Ver Cursos', 'Crear Curso', 'Editar Estudiante')
            $table->string('display_name')->nullable();
            // Descripción opcional del permiso
            $table->string('description')->nullable();
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('permissions');
    }
};
