<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use App\Strategies\NombreSearch;
use App\Strategies\ApellidoSearch;

class Estudiante extends Model
{
    use HasFactory;

    // protected $fillable = ['nombre', 'apellido', 'edad'];
    // private $nombre;
    // private $apellido;
    // private $edad;

    // public function setNombre($nombre) {
    //     $this->nombre = $nombre;
    // }

    // public function setApellido($apellido) {
    //     $this->apellido = $apellido;
    // }

    // public function setEdad($edad) {
    //     $this->edad = $edad;
    // }

    // public function __toString() {
    //     return "Estudiante: {$this->nombre} {$this->apellido}, Edad: {$this->edad}";
    // }

    protected $guarded = []; // Permitir asignación masiva

    public function cursos()
    {
        return $this->belongsToMany(Curso::class)->withPivot('nota', 'estado');
    }

    public function asignarCurso($cursoId, $nota = null, $estado = null)
{
    $this->cursos()->attach($cursoId, ['nota' => $nota, 'estado' => $estado]);
}

public function actualizarCurso($cursoId, $nota, $estado)
{
    $this->cursos()->updateExistingPivot($cursoId, ['nota' => $nota, 'estado' => $estado]);
}


    public static function searchByNombreOApellido($query)
    {
    $resultByName = (new NombreSearch())->search($query);
    $resultByApellido = (new ApellidoSearch())->search($query);

    // Combinar los resultados únicos
    return $resultByName->merge($resultByApellido)->unique('id');
    }

    public function getNombreCompleto()
    {
        return $this->nombre . ' ' . $this->apellido;
    }

    public function getEdad()
    {
        return $this->edad;
    }

}
