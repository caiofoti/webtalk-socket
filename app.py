from flask import Flask
from flask_socketio import SocketIO
from config import Config
from routes import main_bp, admin_bp
from socketio_handlers import registrar_eventos_socketio


def criar_aplicacao():
    app = Flask(__name__)
    app.config.from_object(Config)

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
    print("🚀 WebTalk Socket iniciado!")
    print(f"📍 Acesse: http://localhost:{Config.PORT}")
    print(f"🔧 Admin: http://localhost:{Config.PORT}/admin")
    print(f"🔑 Senha admin: {Config.ADMIN_PASSWORD}")

    socketio.run(app,
                 host=Config.HOST,
                 port=Config.PORT,
                 debug=Config.DEBUG)
