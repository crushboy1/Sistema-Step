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
        Schema::create('role_user', function (Blueprint $table) {
            // Clave foránea al ID del rol
            $table->foreignId('role_id')->constrained()->onDelete('cascade');
            // Clave foránea al ID del usuario (ajusta 'users' si tu tabla se llama diferente)
            $table->foreignId('user_id')->constrained('users')->onDelete('cascade');

            // Define la clave primaria compuesta por role_id y user_id
            $table->primary(['role_id', 'user_id']);

            // Opcional: marcas de tiempo si necesitas saber cuándo se asignó el rol
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('role_user');
    }
};
