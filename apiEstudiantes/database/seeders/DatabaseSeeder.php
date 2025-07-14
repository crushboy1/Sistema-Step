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

        // 2. Crea usuarios de prueba (admin, tutores, estudiantes)
        User::factory()->create([
            'name' => 'Admin',
            'last_name' => 'User',
            'number' => '999999999',
            'email' => 'admin@example.com',
            'password' => Hash::make('password'),
            'email_verified_at' => now(),
            'last_login_at' => null,
            'last_login_ip' => null,
            'registered_ip' => '127.0.0.1',
            'failed_login_attempts' => 0,
            'locked_until' => null,
            'password_changed_at' => now(),
            'last_login_user_agent' => null,
            'two_factor_code' => null,
            'two_factor_expires_at' => null,
            'two_factor_enabled_at' => \Carbon\Carbon::now(),
            'two_factor_secret' => null,
            'two_factor_recovery_codes' => null,
        ]);
        User::factory()->create([
            'name' => 'Juan',
            'last_name' => 'Perez',
            'number' => '987654321',
            'email' => 'jj@gmail.com',
            'password' => Hash::make('password'),
            'email_verified_at' => now(),
        ]);
        User::factory()->create([
            'name' => 'Ana',
            'last_name' => 'Gomez',
            'number' => '982147474',
            'email' => 'estudiante1@example.com',
            'password' => Hash::make('password'),
            'email_verified_at' => now(),
        ]);
        User::factory()->create([
            'name' => 'Carlos',
            'last_name' => 'Ruiz',
            'number' => '923549879',
            'email' => 'estudiante2@example.com',
            'password' => Hash::make('password'),
            'email_verified_at' => now(),
        ]);
        User::factory()->create([
            'name' => 'Lucia',
            'last_name' => 'Martinez',
            'number' => '912345678',
            'email' => 'lucia.martinez@example.com',
            'password' => Hash::make('password'),
            'email_verified_at' => now(),
        ]);

        // 3. Ahora llama al seeder que asigna roles a usuarios
        $this->call([
            RoleUserSeeder::class,
        ]);

        // 4. Crear 5 cursos de ejemplo
        $tutorUser = \App\Models\User::where('email', 'jj@gmail.com')->first();
        $luciaUser = \App\Models\User::where('email', 'lucia.martinez@example.com')->first();
        \App\Models\Curso::create([
            'nombre' => 'Matemáticas Básicas',
            'descripcion' => 'Curso introductorio de matemáticas para estudiantes de secundaria.',
            'monto' => 120.00,
            'frecuencia' => 'Semanal',
            'imagen_url' => 'https://ejemplo.com/matematicas.jpg',
            'user_id' => $tutorUser ? $tutorUser->id : null,
        ]);
        \App\Models\Curso::create([
            'nombre' => 'Física para Todos',
            'descripcion' => 'Aprende los conceptos fundamentales de la física.',
            'monto' => 150.00,
            'frecuencia' => 'Semanal',
            'imagen_url' => 'https://ejemplo.com/fisica.jpg',
            'user_id' => $luciaUser ? $luciaUser->id : null,
        ]);
        \App\Models\Curso::create([
            'nombre' => 'Inglés Conversacional',
            'descripcion' => 'Mejora tu inglés hablado con clases prácticas.',
            'monto' => 100.00,
            'frecuencia' => 'Diario',
            'imagen_url' => 'https://ejemplo.com/ingles.jpg',
            'user_id' => $tutorUser ? $tutorUser->id : null,
        ]);
        \App\Models\Curso::create([
            'nombre' => 'Programación en Python',
            'descripcion' => 'Curso básico de programación usando Python.',
            'monto' => 200.00,
            'frecuencia' => 'Semanal',
            'imagen_url' => 'https://ejemplo.com/python.jpg',
            'user_id' => $luciaUser ? $luciaUser->id : null,
        ]);
        \App\Models\Curso::create([
            'nombre' => 'Historia Universal',
            'descripcion' => 'Explora los eventos más importantes de la historia mundial.',
            'monto' => 90.00,
            'frecuencia' => 'Mensual',
            'imagen_url' => 'https://ejemplo.com/historia.jpg',
            'user_id' => $tutorUser ? $tutorUser->id : null,
        ]);

        // Opcional: Crear más usuarios de prueba usando el factory si lo necesitas
        // User::factory(10)->create();
    }
}
