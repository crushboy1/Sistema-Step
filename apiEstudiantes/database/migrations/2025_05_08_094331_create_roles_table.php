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
        Schema::create('roles', function (Blueprint $table) {
            $table->id();
            // Nombre único para el rol (ej. 'administrador', 'tutor', 'estudiante')
            $table->string('name')->unique();
            // Nombre legible para mostrar (ej. 'Administrador', 'Tutor', 'Estudiante')
            $table->string('display_name')->nullable();
            // Descripción opcional del rol
            $table->string('description')->nullable();
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('roles');
    }
};
