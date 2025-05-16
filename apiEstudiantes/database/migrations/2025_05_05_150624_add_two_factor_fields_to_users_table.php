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
        Schema::table('users', function (Blueprint $table) { 
            $table->string('two_factor_code')->nullable()->after('password'); // Añade después de 'password'
            $table->timestamp('two_factor_expires_at')->nullable()->after('two_factor_code'); // Añade después del código
            $table->boolean('two_factor_enabled')->default(false)->after('two_factor_expires_at');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('users', function (Blueprint $table) { 
            $table->dropColumn(['two_factor_code', 'two_factor_expires_at']);
            $table->dropColumn('two_factor_enabled');
        });
    }
};
