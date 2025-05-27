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
        Schema::create('courses', function (Blueprint $table) {
            $table->id();
            $table->string('nombre');
            $table->text('descripcion')->nullable();
            $table->decimal('monto', 8, 2); // Ejemplo: 999999.99
            $table->string('frecuencia')->nullable(); // Ej: "Semanal", "Mensual"
            $table->string('imagen_url')->nullable(); // Para la URL de una imagen del curso
            // El 'user_id' (tutor) se añadirá en una migración posterior para mantener el orden
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('courses');
    }
};
