<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Foundation\Auth\User as Authenticatable; 
use Illuminate\Notifications\Notifiable;
use Laravel\Sanctum\HasApiTokens; 
use Illuminate\Database\Eloquent\Relations\BelongsToMany; 
use App\Models\Role; 
use App\Models\Curso; 
use Carbon\Carbon; 
class User extends Authenticatable
{

    use HasApiTokens, HasFactory, Notifiable;

    /**
     * The attributes that are mass assignable.
     *
     * @var array<int, string>
     */
    protected $fillable = [
        'name',
        'last_name',
        'number',
        'email',
        'password',
        'two_factor_code',
        'two_factor_expires_at',
        'two_factor_enabled',
        'two_factor_secret',
        'two_factor_recovery_codes',
        'last_login_at',
        'last_login_ip',
        'registered_ip',
        'failed_login_attempts',
        'locked_until',
        'password_changed_at',
        'last_login_user_agent',
    ];

    /**
     * The attributes that should be hidden for serialization.
     *
     * @var array<int, string>
     */
    protected $hidden = [
        'password',
        'remember_token',
        'two_factor_code',
        'two_factor_expires_at',
        'two_factor_secret',
        'two_factor_recovery_codes',
    ];

    /**
     * The attributes that should be cast.
     *
     * @var array<string, string>
     */
    // Usamos la propiedad $casts en lugar del método casts() para consistencia
    protected $casts = [
        'email_verified_at' => 'datetime',
        'password' => 'hashed',
        'two_factor_expires_at' => 'datetime',
        'two_factor_enabled_at' => 'datetime', // Castear como datetime
        'two_factor_recovery_codes' => 'array', // Castear como array (si almacena JSON)
        'last_login_at' => 'datetime',
        'locked_until' => 'datetime',
        'password_changed_at' => 'datetime',
        // Los demás campos (string, integer) no necesitan casteo explícito si ya son su tipo por defecto
        'failed_login_attempts' => 'integer',
    ];

    // Puedes añadir aquí cualquier método personalizado para tu modelo
    // Por ejemplo, un método para generar el código 2FA o verificar si 2FA está activo
    protected $appends = ['roles_names', 'numero_contacto']; // Añade 'numero_contacto' aquí
    /**
     * Check if the user requires two-factor authentication.
     *
     * @return bool
     */
    public function requiresTwoFactorAuthentication(): bool
    {
        // Implementa tu lógica aquí. Por ejemplo, verifica si two_factor_enabled es true.
        // return $this->two_factor_enabled; // Si tienes el campo two_factor_enabled
        // O simplemente siempre requiere 2FA para todos los logins
        return true; // Si siempre quieres 2FA
    }

    /**
     * Generate a new two-factor authentication code.
     *
     * @return int
     */
    public function generateTwoFactorCode(): int
    {
        $code = rand(100000, 999999); // Genera un código de 6 dígitos
        $expiresAt = \Carbon\Carbon::now()->addMinutes(10); // Código válido por 10 minutos

        $this->update([
            'two_factor_code' => $code,
            'two_factor_expires_at' => $expiresAt,
        ]);

        return $code;
    }

    /**
     * Send the two-factor authentication code via email.
     *
     * @param int $code
     * @return void
     */
    public function sendTwoFactorCodeNotification(int $code): void
    {
        // Asegúrate de que App\Mail\VerificationCodeMail existe
        \Mail::to($this->email)->send(new \App\Mail\VerificationCodeMail($code));
    }

    public function roles(): BelongsToMany
    {
        // 'role_user' es el nombre de la tabla pivote
        // 'user_id' es la clave foránea en la tabla pivote que apunta a este modelo (User)
        // 'role_id' es la clave foránea en la tabla pivote que apunta al modelo relacionado (Role)
        return $this->belongsToMany(Role::class, 'role_user', 'user_id', 'role_id');
    }
    /**
     * Verifica si el usuario tiene un rol específico.
     *
     * @param string $roleName El nombre del rol a verificar (ej. 'admin', 'editor', 'subscriber').
     * @return bool
     */
    public function hasRole(string $roleName): bool
    {
        return $this->roles->contains('name', $roleName);
    }
    public function cursos()
    {
        return $this->belongsToMany(Curso::class, 'course_user', 'user_id', 'course_id');
    }
    public function cursosEnseñados()
    {
        return $this->hasMany(Curso::class, 'user_id'); // 'user_id' in 'cursos' table points to the tutor's ID
    }
    // NUEVO: Accessor para el número de teléfono si no se llama 'phone_number'
    // Si tu campo en la DB se llama 'numero', podrías tener un accessor así:
    // public function getNumeroAttribute($value)
    // {
    //     return $this->attributes['phone_number']; // Asumiendo que 'phone_number' es el nombre real de la columna
    // }
    // O si quieres que se muestre como 'numero_contacto' en la API:
    public function getRolesNamesAttribute()
    {
        return $this->roles->pluck('name');
    }

    public function getNumeroContactoAttribute()
    {
        return $this->number; // Asumiendo que el campo en la DB es 'phone_number'
    }
}
