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
        Schema::create('permission_role', function (Blueprint $table) {
            // Clave foránea al ID del permiso
            $table->foreignId('permission_id')->constrained()->onDelete('cascade');
            // Clave foránea al ID del rol
            $table->foreignId('role_id')->constrained()->onDelete('cascade');

            // Define la clave primaria compuesta por permission_id y role_id
            $table->primary(['permission_id', 'role_id']);

            // Opcional: marcas de tiempo si necesitas saber cuándo se asignó el permiso al rol
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('permission_role');
    }
};
