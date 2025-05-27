<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Código de Verificación</title>
    <style>
        body {
            font-family: sans-serif;
            line-height: 1.6;
            color: #333;
        }
        .container {
            max-width: 600px;
            margin: 20px auto;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 8px;
        }
        .code {
            font-size: 24px;
            font-weight: bold;
            color: #007bff; /* O un color que prefieras */
        }
    </style>
</head>
<body>
    <div class="container">
        <p>Hola,</p>
        <p>Tu código de verificación para iniciar sesión es:</p>
        <p class="code">{{ $code }}</p>
        <p>Este código es válido por un tiempo limitado. Por favor, úsalo para completar tu inicio de sesión.</p>
        <p>Si no solicitaste este código, por favor ignora este correo.</p>
        <p>Gracias.</p>
        {{ config('app.name') }}
    </div>
</body>
</html>