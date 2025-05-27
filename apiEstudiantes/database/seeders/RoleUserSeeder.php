<?php

namespace Database\Seeders;

use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB; // Importar la fachada DB
use App\Models\User; // Importar el modelo User
use App\Models\Role; // Importar el modelo Role
class RoleUserSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        // Obtener los IDs de los roles
        // Asegúrate de que estos roles ya existen (ej. creados por RoleSeeder)
        $adminRole = Role::where('name', 'administrador')->first();
        $tutorRole = Role::where('name', 'tutor')->first();
        $estudianteRole = Role::where('name', 'estudiante')->first();

        // Asignar el rol de 'administrador' al usuario 'admin@example.com'
        // Este usuario debería ser creado en DatabaseSeeder
        $adminUser = User::where('email', 'admin@example.com')->first();
        if ($adminUser && $adminRole) {
            $adminUser->roles()->attach($adminRole->id);
            $this->command->info('Rol "administrador" asignado a: ' . $adminUser->email);
        } else {
            $this->command->warn('No se pudo asignar el rol "administrador" (usuario o rol no encontrado).');
        }

        // Crear y asignar el rol de 'tutor'
        // Si 'jj@gmail.com' es un usuario existente, simplemente encuéntralo.
        // Si no, lo creamos aquí.
        $tutorUser = User::where('email', 'jj@gmail.com')->first();
        if (!$tutorUser) {
            $tutorUser = User::factory()->create([
                'name' => 'Juan',
                'last_name' => 'Perez',
                'number' => '987654321',
                'email' => 'jj@gmail.com',
                'password' => Hash::make('password'),
                'email_verified_at' => now(),
            ]);
            $this->command->info('Usuario tutor creado: ' . $tutorUser->email);
        }

        if ($tutorUser && $tutorRole) {
            $tutorUser->roles()->attach($tutorRole->id);
            $this->command->info('Rol "tutor" asignado a: ' . $tutorUser->email);
        } else {
            $this->command->warn('No se pudo asignar el rol "tutor" (usuario o rol no encontrado).');
        }

        // Crear y asignar el rol de 'estudiante' a dos usuarios
        $estudianteUser1 = User::where('email', 'estudiante1@example.com')->first();
        if (!$estudianteUser1) {
            $estudianteUser1 = User::factory()->create([
                'name' => 'Ana',
                'last_name' => 'Gomez',
                'number' => '982147474',
                'email' => 'estudiante1@example.com',
                'password' => Hash::make('password'),
                'email_verified_at' => now(),
            ]);
            $this->command->info('Usuario estudiante 1 creado: ' . $estudianteUser1->email);
        }

        if ($estudianteUser1 && $estudianteRole) {
            $estudianteUser1->roles()->attach($estudianteRole->id);
            $this->command->info('Rol "estudiante" asignado a: ' . $estudianteUser1->email);
        } else {
            $this->command->warn('No se pudo asignar el rol "estudiante" al estudiante 1 (usuario o rol no encontrado).');
        }

        $estudianteUser2 = User::where('email', 'estudiante2@example.com')->first();
        if (!$estudianteUser2) {
            $estudianteUser2 = User::factory()->create([
                'name' => 'Carlos',
                'last_name' => 'Ruiz',
                'number' => '923549879',
                'email' => 'estudiante2@example.com',
                'password' => Hash::make('password'),
                'email_verified_at' => now(),
            ]);
            $this->command->info('Usuario estudiante 2 creado: ' . $estudianteUser2->email);
        }

        if ($estudianteUser2 && $estudianteRole) {
            $estudianteUser2->roles()->attach($estudianteRole->id);
            $this->command->info('Rol "estudiante" asignado a: ' . $estudianteUser2->email);
        } else {
            $this->command->warn('No se pudo asignar el rol "estudiante" al estudiante 2 (usuario o rol no encontrado).');
        }

        // Puedes añadir más asignaciones según necesites
    }
}
