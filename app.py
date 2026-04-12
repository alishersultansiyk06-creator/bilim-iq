<!DOCTYPE html>
<html lang="kk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bilim IQ - Кіру</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body {
            margin: 0; height: 100vh; display: flex; align-items: center; justify-content: center;
            background: radial-gradient(circle at bottom, #1B2735 0%, #090A0F 100%);
            font-family: 'Segoe UI', sans-serif; color: white; overflow: hidden;
        }
        .glass-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 25px; padding: 40px;
            width: 90%; max-width: 350px; text-align: center;
            box-shadow: 0 20px 50px rgba(0,0,0,0.5);
        }
        h1 { margin-bottom: 30px; letter-spacing: 2px; }
        input {
            width: 100%; padding: 12px; margin: 10px 0; border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.1); background: rgba(255, 255, 255, 0.1); 
            color: white; outline: none; box-sizing: border-box;
        }
        input::placeholder { color: rgba(255,255,255,0.5); }
        
        .btn-main {
            width: 100%; padding: 12px; border-radius: 12px; border: none; margin-top: 10px;
            background: linear-gradient(45deg, #00d2ff, #3a7bd5);
            color: white; font-weight: bold; cursor: pointer; transition: 0.3s;
        }
        .btn-main:hover { transform: scale(1.05); box-shadow: 0 0 20px rgba(0,210,255,0.5); }

        /* Әлеуметтік желілер блогы */
        .separator {
            margin: 25px 0; display: flex; align-items: center; text-align: center;
            color: rgba(255,255,255,0.3); font-size: 0.8rem;
        }
        .separator::before, .separator::after {
            content: ''; flex: 1; border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .separator:not(:empty)::before { margin-right: .5em; }
        .separator:not(:empty)::after { margin-left: .5em; }

        .social-group { display: flex; gap: 10px; justify-content: center; }
        
        .btn-social {
            flex: 1; padding: 10px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1);
            background: rgba(255,255,255,0.05); color: white; text-decoration: none;
            font-size: 0.9rem; transition: 0.3s; display: flex; align-items: center; justify-content: center; gap: 8px;
        }
        .btn-social:hover { background: rgba(255,255,255,0.15); border-color: rgba(255,255,255,0.5); }
        .google-color { color: #DB4437; }
        .fb-color { color: #4267B2; }
    </style>
</head>
<body>
    <div class="glass-card">
        <h1>Bilim <span style="color:#00d2ff;">IQ</span></h1>
        
        <form action="/login" method="POST">
            <input type="text" name="username" placeholder="Логин немесе Email" required>
            <input type="password" name="password" placeholder="Құпия сөз" required>
            <button type="submit" class="btn-main">Кіру</button>
        </form>

        <div class="separator">немесе</div>

        <div class="social-group">
            <a href="/login/google" class="btn-social">
                <i class="fab fa-google google-color"></i> Google
            </a>
            <a href="/login/facebook" class="btn-social">
                <i class="fab fa-facebook fb-color"></i> Facebook
            </a>
        </div>

        <p style="margin-top: 25px; font-size: 0.8rem; opacity: 0.6;">
            Тіркелмегенсіз бе? <a href="#" style="color: #00d2ff; text-decoration: none;">Тіркелу</a>
        </p>
    </div>
</body>
</html>
