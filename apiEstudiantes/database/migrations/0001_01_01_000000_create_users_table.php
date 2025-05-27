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
        Schema::create('users', function (Blueprint $table) {
            $table->id();
            $table->string('name');
            $table->string('last_name');
            $table->string('number');
            $table->string('email')->unique();
            $table->timestamp('email_verified_at')->nullable();
            $table->string('password');
            $table->rememberToken();

            // --- Campos de Seguridad y Auditoría ---
            // Última vez que el usuario inició sesión
            $table->timestamp('last_login_at')->nullable();
            // Dirección IP del último inicio de sesión (45 para IPv6)
            $table->string('last_login_ip', 45)->nullable();
            // Dirección IP desde la que se registró el usuario
            $table->string('registered_ip', 45)->nullable();
            // Contador de intentos fallidos de inicio de sesión
            $table->integer('failed_login_attempts')->default(0);
            // Timestamp hasta el cual la cuenta está bloqueada por intentos fallidos
            $table->timestamp('locked_until')->nullable();
            // Timestamp de la última vez que el usuario cambió su contraseña
            $table->timestamp('password_changed_at')->nullable();
            // User Agent del último inicio de sesión (puede ser largo)
            $table->text('last_login_user_agent')->nullable();

            // --- Campos para Autenticación de Doble Factor (2FA) ---
            // Código de verificación 2FA (para email/SMS)
            $table->string('two_factor_code')->nullable();
            // Tiempo de expiración del código 2FA
            $table->timestamp('two_factor_expires_at')->nullable();
            // Indica si 2FA está habilitado para el usuario (si usas autenticadores o lo controlas así)
            $table->timestamp('two_factor_enabled_at')->nullable()->default(null);
            // Campo para almacenar el secreto de 2FA (si usas autenticadores como Google Authenticator)
            $table->text('two_factor_secret')->nullable();
            // Campo para almacenar códigos de recuperación de 2FA (separados por comas o JSON)
            $table->text('two_factor_recovery_codes')->nullable();


            $table->timestamps(); // created_at y updated_at
        });

        Schema::create('password_reset_tokens', function (Blueprint $table) {
            $table->string('email')->primary();
            $table->string('token');
            $table->timestamp('created_at')->nullable();
        });

        Schema::create('sessions', function (Blueprint $table) {
            $table->string('id')->primary();
            $table->foreignId('user_id')->nullable()->index();
            $table->string('ip_address', 45)->nullable();
            $table->text('user_agent')->nullable();
            $table->longText('payload');
            $table->integer('last_activity')->index();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('users');
        Schema::dropIfExists('password_reset_tokens');
        Schema::dropIfExists('sessions');
    }
};
