<?php

namespace Database\Seeders;

use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB; // Importar la fachada DB
class PermissionSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        // Insertar los permisos en la tabla 'permissions'
        DB::table('permissions')->insert([
            ['name' => 'view_courses', 'display_name' => 'Ver Cursos', 'description' => 'Permite ver la lista de cursos', 'created_at' => now(), 'updated_at' => now()],
            ['name' => 'create_course', 'display_name' => 'Crear Curso', 'description' => 'Permite crear nuevos cursos', 'created_at' => now(), 'updated_at' => now()],
            ['name' => 'view_course_details', 'display_name' => 'Ver Detalles de Curso', 'description' => 'Permite ver la información detallada de un curso', 'created_at' => now(), 'updated_at' => now()],
            ['name' => 'edit_course', 'display_name' => 'Editar Curso', 'description' => 'Permite editar cursos existentes', 'created_at' => now(), 'updated_at' => now()],
            ['name' => 'delete_course', 'display_name' => 'Eliminar Curso', 'description' => 'Permite eliminar cursos', 'created_at' => now(), 'updated_at' => now()],
            ['name' => 'register_course', 'display_name' => 'Registrarse en Curso', 'description' => 'Permite a los estudiantes registrarse en cursos', 'created_at' => now(), 'updated_at' => now()],
            ['name' => 'view_users', 'display_name' => 'Ver usuarios', 'description' => 'Permite ver a los estudiantes registrados en el sistema', 'created_at' => now(), 'update_at' => now()],
            ['name' => 'edit_user', 'display_name' => 'Editar usuario', 'description' => 'Permite editar usuario registrado en el sistema', 'created_at' => now(), 'update_at' => now()],
            ['name' => 'delete_user', 'display_name' => 'Eliminar usuario', 'description' => 'Permite eliminar usuario registrado en el sistema', 'created_at' => now(), 'update_at' => now()],
            // Puedes añadir más permisos si es necesario (ej. view_students, edit_students, etc.)
        ]);
    }
}
