import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()


class Config:
    """Configurações base da aplicação WebTalk Socket"""

    # Configurações básicas do Flask
    SECRET_KEY = os.environ.get(
        'SECRET_KEY') or 'webtalk-socket-dev-key-ufcspa-2024'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'

    # Configurações de rede
    HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
    PORT = int(os.environ.get('FLASK_PORT', 5000))

    # Configurações de segurança
    SESSION_COOKIE_SECURE = os.environ.get(
        'SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

    # Configurações administrativas
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

    # Configurações de banco de dados
    DATABASE_PATH = os.environ.get('DATABASE_PATH', 'webtalk_socket.db')

    # Configurações de upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'uploads')
    ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}

    # Configurações de rate limiting
    RATELIMIT_STORAGE_URL = "memory://"
    RATELIMIT_DEFAULT = "100 per hour"

    # Configurações de Socket.IO
    SOCKETIO_ASYNC_MODE = 'threading'
    SOCKETIO_CORS_ALLOWED_ORIGINS = "*"
    SOCKETIO_LOGGER = DEBUG
    SOCKETIO_ENGINEIO_LOGGER = False

    # Configurações de PWA
    PWA_NAME = "WebTalk Socket"
    PWA_SHORT_NAME = "WebTalk"
    PWA_DESCRIPTION = "Sistema de comunicação distribuída em tempo real - UFCSPA"
    PWA_THEME_COLOR = "#0B354F"
    PWA_BACKGROUND_COLOR = "#0B354F"

    # Configurações de cache (para produção)
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'simple')
    CACHE_DEFAULT_TIMEOUT = 300

    # Configurações de logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'webtalk_socket.log')

    # Configurações de sessão de salas
    ROOM_TIMEOUT_HOURS = int(os.environ.get('ROOM_TIMEOUT_HOURS', 24))
    MAX_ROOMS = int(os.environ.get('MAX_ROOMS', 100))
    MAX_USERS_PER_ROOM = int(os.environ.get('MAX_USERS_PER_ROOM', 50))
    MAX_MESSAGES_PER_ROOM = int(os.environ.get('MAX_MESSAGES_PER_ROOM', 1000))

    # Configurações de backup automático
    AUTO_BACKUP_ENABLED = os.environ.get(
        'AUTO_BACKUP_ENABLED', 'True').lower() == 'true'
    BACKUP_INTERVAL_HOURS = int(os.environ.get('BACKUP_INTERVAL_HOURS', 6))
    BACKUP_RETENTION_DAYS = int(os.environ.get('BACKUP_RETENTION_DAYS', 30))

    @staticmethod
    def init_app(app):
        """Inicialização da aplicação com configurações específicas"""
        # Criar diretórios necessários
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

        # Configurar logging baseado no nível definido
        import logging
        log_level = getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO)
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(Config.LOG_FILE),
                logging.StreamHandler()
            ]
        )

        # Configurações específicas para produção
        if not Config.DEBUG:
            # Configurações de segurança para produção
            app.config['SESSION_COOKIE_SECURE'] = True
            app.config['PREFERRED_URL_SCHEME'] = 'https'


class DevelopmentConfig(Config):
    """Configurações para ambiente de desenvolvimento"""
    DEBUG = True
    SOCKETIO_LOGGER = True
    SOCKETIO_ENGINEIO_LOGGER = True


class ProductionConfig(Config):
    """Configurações para ambiente de produção"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    SOCKETIO_LOGGER = False
    SOCKETIO_ENGINEIO_LOGGER = False

    # Configurações mais restritivas para produção
    RATELIMIT_DEFAULT = "50 per hour"
    MAX_ROOMS = 50
    MAX_USERS_PER_ROOM = 25


class TestingConfig(Config):
    """Configurações para testes"""
    TESTING = True
    DEBUG = True
    DATABASE_PATH = ':memory:'
    WTF_CSRF_ENABLED = False


# Dicionário de configurações
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
