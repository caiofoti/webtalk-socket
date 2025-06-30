from flask import Flask, request, g
from flask_socketio import SocketIO
from config import Config
from routes import main_bp, admin_bp
from socketio_handlers import registrar_eventos_socketio
import time


def criar_aplicacao():
    """Cria e configura a aplicação Flask"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Middleware de logging compacto para estudo
    @app.before_request
    def log_request_info():
        """Log compacto de requisições HTTP para controle de operações"""
        g.start_time = time.time()

        # Ignorar arquivos estáticos
        if request.endpoint and 'static' in request.endpoint:
            return

        # Log básico da requisição
        timestamp = time.strftime("%H:%M:%S")
        client_ip = request.environ.get('REMOTE_ADDR', 'unknown')

        print(f"[{timestamp}] {request.method} {request.path} - IP: {client_ip}")

        # Log adicional para operações importantes
        if request.method in ['POST', 'PUT', 'DELETE']:
            if request.is_json:
                data = request.get_json()
                if data:
                    # Mascarar senhas
                    safe_data = {k: '[***]' if 'senha' in k.lower() or 'password' in k.lower()
                                 else v for k, v in data.items()}
                    print(f"  Data: {safe_data}")

            # Log de uploads
            if request.files:
                for key, file in request.files.items():
                    if file.filename:
                        file.seek(0, 2)
                        size = file.tell()
                        file.seek(0)
                        print(f"  Upload: {file.filename} ({size/1024:.1f}KB)")

    @app.after_request
    def log_response_info(response):
        """Log compacto da resposta"""
        # Ignorar arquivos estáticos
        if request.endpoint and 'static' in request.endpoint:
            return response

        processing_time = (
            time.time() - g.get('start_time', time.time())) * 1000

        # Log da resposta
        if response.status_code >= 400:
            print(
                f"  Response: {response.status_code} ERROR ({processing_time:.0f}ms)")
        elif processing_time > 1000:  # Log se demorou mais que 1s
            print(
                f"  Response: {response.status_code} OK ({processing_time:.0f}ms) [SLOW]")
        else:
            print(
                f"  Response: {response.status_code} OK ({processing_time:.0f}ms)")

        return response

    # Registrar blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)

    return app


# Criar aplicação
app = criar_aplicacao()

# Configurar Socket.IO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
# Registrar eventos do Socket.IO
registrar_eventos_socketio(socketio)

if __name__ == '__main__':
    print("="*60)
    print("WEBTALK SOCKET - Sistema de Comunicação Distribuída")
    print("UFCSPA - Fundamentos de Redes e Sistemas Distribuídos")
    print("="*60)
    print(f"Servidor: http://localhost:{Config.PORT}")
    print(f"Admin: http://localhost:{Config.PORT}/admin")
    print(f"Senha Admin: {Config.ADMIN_PASSWORD}")
    print("Logging HTTP: ATIVO")
    print("="*60)

    socketio.run(app,
                 host=Config.HOST,
                 port=Config.PORT,
                 debug=Config.DEBUG)
