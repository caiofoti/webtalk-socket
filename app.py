from flask import Flask
from flask_socketio import SocketIO
from config import Config
from routes import main_bp, admin_bp
from socketio_handlers import register_socketio_events

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Registrar blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    
    return app

# Criar aplicação
app = create_app()

# Configurar Socket.IO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
# Registrar eventos do Socket.IO
register_socketio_events(socketio)

if __name__ == '__main__':
    print("🚀 WebTalk Socket iniciado!")
    print(f"📍 Acesse: http://localhost:{Config.PORT}")
    print(f"🔧 Admin: http://localhost:{Config.PORT}/admin")
    print(f"🔑 Senha admin: {Config.ADMIN_PASSWORD}")
    
    socketio.run(app, 
                host=Config.HOST, 
                port=Config.PORT, 
                debug=Config.DEBUG)