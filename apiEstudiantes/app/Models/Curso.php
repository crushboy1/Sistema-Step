<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Curso extends Model
{
    use HasFactory;

    // Campos permitidos para la asignación masiva
    protected $fillable = ['nombre', 'descripcion', 'creditos'];

    // Relación muchos a muchos con Estudiante
    public function estudiantes()
    {
        return $this->belongsToMany(Estudiante::class)->withPivot('nota'); // Incluye 'withPivot' para acceder a la columna 'nota'
    }
}
