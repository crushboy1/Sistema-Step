<?php

namespace Database\Seeders;

use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB; // Importar la fachada DB
use App\Models\Role; // Importar el modelo Role
use App\Models\Permission; // Importar el modelo Permission
class PermissionRoleSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        // Obtener los IDs de los roles y permisos
        $adminRole = Role::where('name', 'administrador')->first();
        $tutorRole = Role::where('name', 'tutor')->first();
        $estudianteRole = Role::where('name', 'estudiante')->first();

        $viewCoursesPermission = Permission::where('name', 'view_courses')->first();
        $createCoursePermission = Permission::where('name', 'create_course')->first();
        $viewCourseDetailsPermission = Permission::where('name', 'view_course_details')->first();
        $editCoursePermission = Permission::where('name', 'edit_course')->first();
        $deleteCoursePermission = Permission::where('name', 'delete_course')->first();
        $registerCoursePermission = Permission::where('name', 'register_course')->first();
        $viewUsersPermission = Permission::where('name', 'view_users')->first();
        $editUserPermission = Permission::where('name', 'edit_user')->first();
        $deleteUserPermission = Permission::where('name', 'delete_user')->first();

       
        if ($adminRole) {
            $adminRole->permissions()->attach([
                $viewCoursesPermission->id,
                $createCoursePermission->id,
                $viewCourseDetailsPermission->id,
                $editCoursePermission->id,
                $deleteCoursePermission->id,
                $registerCoursePermission->id, 
                $viewUsersPermission->id,
                $editUserPermission->id,
                $deleteUserPermission->id,
              
            ]);
        }

        
        if ($tutorRole) {
            $tutorRole->permissions()->attach([
                $viewCoursesPermission->id,
                $createCoursePermission->id,
                $viewCourseDetailsPermission->id,
                $editCoursePermission->id,
                $deleteCoursePermission->id,
            ]);
        }

     
        if ($estudianteRole) {
            $estudianteRole->permissions()->attach([
                $viewCoursesPermission->id,
                $viewCourseDetailsPermission->id,
                $registerCoursePermission->id,
            ]);
        }
    }
}
