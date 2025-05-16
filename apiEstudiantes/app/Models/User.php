<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Foundation\Auth\User as Authenticatable; // Importa la clase Authenticatable
use Illuminate\Notifications\Notifiable;
use Laravel\Sanctum\HasApiTokens; // Importa el trait HasApiTokens
use Illuminate\Database\Eloquent\Relations\BelongsToMany; // Importa BelongsToMany
use App\Models\Role; // Importa el modelo Role
use Carbon\Carbon; // Importar Carbon si aún no está para last_login_at
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
        'email',
        'password',
        'two_factor_code',
        'two_factor_expires_at',
        'two_factor_enabled',
        'last_login_at',
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
        'two_factor_enabled' => 'boolean',
        'last_login_at' => 'datetime',
    ];

    // Puedes añadir aquí cualquier método personalizado para tu modelo
    // Por ejemplo, un método para generar el código 2FA o verificar si 2FA está activo

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
}
