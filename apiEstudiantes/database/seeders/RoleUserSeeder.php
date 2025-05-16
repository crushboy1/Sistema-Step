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
        $adminRole = Role::where('name', 'administrador')->first();
        $tutorRole = Role::where('name', 'tutor')->first();
        $estudianteRole = Role::where('name', 'estudiante')->first();

        // Obtener algunos usuarios existentes (ajústalos según tus usuarios de prueba)
        $adminUser = User::where('email', 'gabriel@example.com')->first(); // Cambia el email por uno real
        $tutorUser = User::where('email', 'jj@gmail.com')->first(); // Cambia el email por uno real
        $estudianteUser1 = User::where('email', 'estudiante1@example.com')->first(); // Cambia el email por uno real
        $estudianteUser2 = User::where('email', 'estudiante2@example.com')->first(); // Cambia el email por uno real

        // Asignar roles a usuarios en la tabla pivote 'role_user'
        if ($adminUser && $adminRole) {
            $adminUser->roles()->attach($adminRole->id);
        }

        if ($tutorUser && $tutorRole) {
            $tutorUser->roles()->attach($tutorRole->id);
        }

        if ($estudianteUser1 && $estudianteRole) {
            $estudianteUser1->roles()->attach($estudianteRole->id);
        }

        if ($estudianteUser2 && $estudianteRole) {
            $estudianteUser2->roles()->attach($estudianteRole->id);
        }

        // Puedes añadir más asignaciones según necesites
    }
}
