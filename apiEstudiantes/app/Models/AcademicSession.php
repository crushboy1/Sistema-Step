<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class AcademicSession extends Model
{
    use HasFactory;

    /**
     * The table associated with the model.
     *
     * @var string
     */
    protected $table = 'academic_sessions'; // Nombre de la tabla en la base de datos

    /**
     * The attributes that are mass assignable.
     *
     * @var array<int, string>
     */
    protected $fillable = [
        'student_id',
        'tutor_id',
        'course_id',
        'start_time',
        'end_time',
        'status',
        'notes',
    ];

    /**
     * The attributes that should be cast.
     *
     * @var array<string, string>
     */
    protected $casts = [
        'start_time' => 'datetime',
        'end_time' => 'datetime',
    ];

    /**
     * Get the student that owns the academic session.
     */
    public function student()
    {
        return $this->belongsTo(User::class, 'student_id');
    }

    /**
     * Get the tutor for the academic session.
     */
    public function tutor()
    {
        return $this->belongsTo(User::class, 'tutor_id');
    }

    /**
     * Get the course that the academic session belongs to.
     */
    public function course()
    {
        return $this->belongsTo(Curso::class, 'course_id');
    }

    /**
     * Get the rating associated with the academic session.
     * Una sesión académica puede tener una calificación.
     */
    public function rating()
    {
        return $this->hasOne(Rating::class, 'session_id');
    }
}

