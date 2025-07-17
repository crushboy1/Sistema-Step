<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Rating extends Model
{
    use HasFactory;

    /**
     * The table associated with the model.
     *
     * @var string
     */
    protected $table = 'ratings'; // Define el nombre de la tabla si no sigue la convención de pluralización de Laravel.

    /**
     * The attributes that are mass assignable.
     *
     * @var array<int, string>
     */
    protected $fillable = [
        'student_id',
        'tutor_id',
        'session_id',
        'rating',
        'comment',
    ];

    /**
     * Get the student that owns the rating.
     * Define la relación: Un Rating pertenece a un Estudiante (User).
     */
    public function student()
    {
        return $this->belongsTo(User::class, 'student_id');
    }

    /**
     * Get the tutor that the rating is for.
     * Define la relación: Un Rating pertenece a un Tutor (User).
     */
    public function tutor()
    {
        return $this->belongsTo(User::class, 'tutor_id');
    }

    /**
     * Get the academic session that the rating belongs to.
     * Define la relación: Un Rating pertenece a una Sesión Académica.
     *
     * @return \Illuminate\Database\Eloquent\Relations\BelongsTo
     */
    public function academicSession() // Cambiado de 'session' a 'academicSession' para mayor claridad
    {
        return $this->belongsTo(AcademicSession::class, 'session_id');
    }
}

