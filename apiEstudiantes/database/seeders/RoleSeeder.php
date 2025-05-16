<?php

namespace Database\Seeders;

use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB; // Importar la fachada DB

class RoleSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        // Insertar los roles en la tabla 'roles'
        DB::table('roles')->insert([
            ['name' => 'administrador', 'display_name' => 'Administrador', 'description' => 'Usuario con acceso total al sistema', 'created_at' => now(), 'updated_at' => now()],
            ['name' => 'tutor', 'display_name' => 'Tutor', 'description' => 'Usuario encargado de la publicación de tutorias', 'created_at' => now(), 'updated_at' => now()],
            ['name' => 'estudiante', 'display_name' => 'Estudiante', 'description' => 'Usuario que accede a los cursos de las tutorias', 'created_at' => now(), 'updated_at' => now()],
        ]);
    }
}
