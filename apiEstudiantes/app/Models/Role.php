<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;
use App\Models\Permission; // Importa el modelo Permission
use App\Models\User; // Importa el modelo User (aunque ya lo usabas con \App\Models\User)

class Role extends Model
{
    use HasFactory;

    /**
     * Los atributos que son asignables masivamente.
     *
     * @var array<int, string>
     */
    protected $fillable = [
        'name',         // Nombre único del rol (ej. 'administrador', 'tutor', 'estudiante')
        'display_name', // Nombre legible para humanos (ej. 'Administrador del Sistema')
        'description',  // Descripción del rol
    ];

    /**
     * Define la relación muchos a muchos con el modelo Permission.
     * Un rol puede tener múltiples permisos.
     *
     * @return \Illuminate\Database\Eloquent\Relations\BelongsToMany
     */
    public function permissions(): BelongsToMany
    {
        // 'permission_role' es el nombre de la tabla pivote.
        // 'role_id' es la clave foránea en la tabla pivote que apunta a este modelo (Role).
        // 'permission_id' es la clave foránea en la tabla pivote que apunta al modelo relacionado (Permission).
        return $this->belongsToMany(Permission::class, 'permission_role', 'role_id', 'permission_id');
    }

    /**
     * Define la relación muchos a muchos con el modelo User.
     * Un rol puede ser asignado a múltiples usuarios.
     *
     * @return \Illuminate\Database\Eloquent\Relations\BelongsToMany
     */
    public function users(): BelongsToMany
    {
        // 'role_user' es el nombre de la tabla pivote.
        // 'role_id' es la clave foránea en la tabla pivote que apunta a este modelo (Role).
        // 'user_id' es la clave foránea en la tabla pivote que apunta al modelo relacionado (User).
        return $this->belongsToMany(User::class, 'role_user', 'role_id', 'user_id');
    }
}
