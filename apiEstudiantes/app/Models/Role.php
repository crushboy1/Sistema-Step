<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model; 
use Illuminate\Database\Eloquent\Relations\BelongsToMany; 

class Role extends Model 
{
    use HasFactory;

    
    protected $fillable = [
        'name',
        'display_name',
        'description',
    ];

    
    
    public function permissions(): BelongsToMany
    {
        
        
        
        return $this->belongsToMany(Permission::class, 'permission_role', 'role_id', 'permission_id');
    }

    
    
    public function users(): BelongsToMany
    {
        
        
        
        
        return $this->belongsToMany(\App\Models\User::class, 'role_user', 'role_id', 'user_id');
    }
}