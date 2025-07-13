<?php

namespace Database\Seeders;

use App\Models\User;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\Hash;

class DatabaseSeeder extends Seeder
{
    /**
     * Seed the application's database.
     */
    public function run(): void
    {
        // 1. Llama a otros seeders para configurar roles y permisos
        // El orden es importante: primero roles y permisos, luego sus pivotes
        $this->call([
            RoleSeeder::class,
            PermissionSeeder::class,
            PermissionRoleSeeder::class, // Asigna permisos a roles
        ]);

        // 2. Crea un usuario de prueba o administrador con todos los campos necesarios
        // Asegúrate de que 'password' esté hasheada
        User::factory()->create([
            'name' => 'Admin',
            'last_name' => 'User', // Asegúrate de poblar este campo
            'number' => '999999999', // Asegúrate de poblar este campo
            'email' => 'admin@example.com',
            'password' => Hash::make('password'), // ¡Siempre hashea las contraseñas!
            'email_verified_at' => now(), // Opcional: marca el email como verificado
            // Los campos de seguridad y 2FA se pueden dejar nulos o con sus valores por defecto
            // ya que la migración los define como nullable() o con default(0)
            'last_login_at' => null,
            'last_login_ip' => null,
            'registered_ip' => '127.0.0.1', // Opcional: IP de registro
            'failed_login_attempts' => 0,
            'locked_until' => null,
            'password_changed_at' => now(), // Opcional: fecha de cambio de contraseña inicial
            'last_login_user_agent' => null,
            'two_factor_code' => null,
            'two_factor_expires_at' => null,
            'two_factor_enabled_at' => \Carbon\Carbon::now(),
            'two_factor_secret' => null,
            'two_factor_recovery_codes' => null,
        ]);

        // 3. Ahora llama al seeder que asigna roles a usuarios
        $this->call([
            RoleUserSeeder::class,
        ]);

        // Opcional: Crear más usuarios de prueba usando el factory si lo necesitas
        // User::factory(10)->create();
    }
}
