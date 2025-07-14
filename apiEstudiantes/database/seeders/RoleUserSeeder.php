<?php

namespace Database\Seeders;

use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB; // Importar la fachada DB
use App\Models\User; // Importar el modelo User
use App\Models\Role; // Importar el modelo Role
use Illuminate\Support\Facades\Hash; // Importar la fachada Hash
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

        // Asignar roles a los 5 usuarios de prueba
        $adminUser = User::where('email', 'admin@example.com')->first();
        $tutorUser = User::where('email', 'jj@gmail.com')->first();
        $estudianteUser1 = User::where('email', 'estudiante1@example.com')->first();
        $estudianteUser2 = User::where('email', 'estudiante2@example.com')->first();
        $luciaUser = User::where('email', 'lucia.martinez@example.com')->first();

        if ($adminUser && $adminRole) {
            $adminUser->roles()->syncWithoutDetaching([$adminRole->id]);
        }
        if ($tutorUser && $tutorRole) {
            $tutorUser->roles()->syncWithoutDetaching([$tutorRole->id]);
        }
        if ($estudianteUser1 && $estudianteRole) {
            $estudianteUser1->roles()->syncWithoutDetaching([$estudianteRole->id]);
        }
        if ($estudianteUser2 && $estudianteRole) {
            $estudianteUser2->roles()->syncWithoutDetaching([$estudianteRole->id]);
        }
        if ($luciaUser && $tutorRole) {
            $luciaUser->roles()->syncWithoutDetaching([$tutorRole->id]); // Lucia como tutor de ejemplo
        }

        // Puedes añadir más asignaciones según necesites
    }
}
