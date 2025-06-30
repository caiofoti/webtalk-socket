# WebTalk Socket

Sistema de comunicação em tempo real baseado em WebSockets desenvolvido para a disciplina de **Fundamentos de Redes e Sistemas Distribuídos** - UFCSPA.

## Visão Geral

Aplicação web que implementa chat em tempo real utilizando Flask, Socket.IO e SQLite. Demonstra conceitos de arquitetura cliente-servidor, comunicação assíncrona e sistemas distribuídos.

### Funcionalidades

- ✅ Salas de chat com acesso público/protegido por senha
- ✅ Comunicação bidirecional em tempo real (WebSocket)
- ✅ Persistência de dados (SQLite)
- ✅ Interface administrativa
- ✅ API REST para gerenciamento de salas
- ✅ Interface responsiva

## Stack Tecnológica

- **Backend**: Python 3.8+, Flask, Flask-SocketIO
- **Frontend**: HTML5, CSS3, JavaScript ES6+, Bootstrap 5
- **Database**: SQLite3
- **Comunicação**: WebSocket, REST API

## Estrutura do Projeto

```
webtalk-socket/
├── app.py                  # Aplicação principal
├── config.py              # Configurações
├── models/
│   └── room.py            # Modelo de salas e gerenciamento
├── routes/
│   ├── main.py            # Rotas principais
│   └── admin.py           # Rotas administrativas
├── socketio_handlers/
│   └── events.py          # Eventos WebSocket
├── templates/             # Templates HTML
├── static/               # Assets estáticos
└── db.sqlite3           # Banco de dados
```

## Instalação e Execução

### Pré-requisitos
- Python 3.8+
- pip

### Setup

1. **Clone o repositório**
```bash
git clone <repository-url>
cd webtalk-socket
```

2. **Instale dependências**
```bash
pip install flask flask-socketio
```

3. **Execute a aplicação**
```bash
python app.py
```

4. **Acesse o sistema**
- Interface principal: http://localhost:5000
- Painel admin: http://localhost:5000/admin
- Senha admin padrão: `admin123`

## API Endpoints

### Salas
- `GET /api/salas` - Lista salas ativas
- `POST /api/salas` - Criar nova sala
- `POST /api/salas/{id}/entrar` - Validar acesso à sala

### Admin
- `GET /api/admin/estatisticas` - Estatísticas do sistema
- `DELETE /api/admin/salas/{id}` - Excluir sala
- `POST /api/admin/configuracoes` - Atualizar configurações

## Eventos WebSocket

### Cliente → Servidor
- `entrar` - Entrar em sala
- `sair` - Sair da sala
- `mensagem_chat` - Enviar mensagem

### Servidor → Cliente
- `usuario_entrou` - Notificar entrada de usuário
- `usuario_saiu` - Notificar saída de usuário
- `mensagem_chat` - Distribuir mensagem
- `erro` - Notificar erro

## Configuração

Edite `config.py` para ajustar:

```python
class Config:
    HOST = '0.0.0.0'
    PORT = 5000
    DEBUG = True
    SECRET_KEY = 'your-secret-key'
    ADMIN_PASSWORD = 'admin123'
```