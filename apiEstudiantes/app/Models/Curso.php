<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Curso extends Model
{
    use HasFactory;
    protected $table = 'courses';
    // Campos permitidos para la asignación masiva
        protected $fillable = [
        'nombre',
        'descripcion',
        'monto',
        'frecuencia',
        'imagen_url', // Si guardas la URL de la imagen
        'user_id', // ¡Importante! ID del tutor que creó el curso
        'dias_tutoria', // NUEVO
        'forma_pago',   // NUEVO
        'otros',        // NUEVO
    ];

    /**
     * Get the tutor (user) that owns the course.
     */
    public function tutor()
    {
        return $this->belongsTo(User::class, 'user_id');
    }

    /**
     * Get the students (users) that are registered for this course.
     */
    public function estudiantes()
    {
        return $this->belongsToMany(User::class, 'course_user', 'curso_id', 'user_id');
    }
}
