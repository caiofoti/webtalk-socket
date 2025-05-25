from flask import request
from flask_socketio import emit, join_room, leave_room
from models.room import room_manager
from datetime import datetime


def register_socketio_events(socketio):
    @socketio.on('connect')
    def handle_connect():
        print(f'Cliente conectado: {request.sid}')
        return True

    @socketio.on('disconnect')
    def handle_disconnect():
        print(f'Cliente desconectado: {request.sid}')

    @socketio.on('join')
    def handle_join(data):
        try:
            room_id = data.get('room_id')
            username = data.get('username')

            if not room_id or not username:
                emit(
                    'error', {'message': 'Room ID e username são obrigatórios'})
                return

            room = room_manager.get_room(room_id)
            if not room:
                emit('error', {'message': 'Sala não encontrada'})
                return

            if not room.is_active:
                emit('error', {'message': 'Sala não está ativa'})
                return

            join_room(room_id)
            room.add_user(username)

            emit('user_joined', {'username': username}, room=room_id)
            print(f'Usuário {username} entrou na sala {room_id}')

            # Enviar mensagens históricas para o usuário que acabou de entrar
            for message in room.messages[-20:]:  # Últimas 20 mensagens
                emit('chat_message', message)

        except Exception as e:
            print(f"Erro ao entrar na sala: {e}")
            emit('error', {'message': 'Erro interno do servidor'})

    @socketio.on('leave')
    def handle_leave(data):
        try:
            room_id = data.get('room_id')
            username = data.get('username')

            if room_id and username:
                room = room_manager.get_room(room_id)
                if room:
                    room.remove_user(username)

                leave_room(room_id)
                emit('user_left', {'username': username}, room=room_id)
                print(f'Usuário {username} saiu da sala {room_id}')

        except Exception as e:
            print(f"Erro ao sair da sala: {e}")

    @socketio.on('chat_message')
    def handle_message(data):
        try:
            room_id = data.get('room_id')
            username = data.get('username')
            message = data.get('message', '').strip()

            if not room_id or not username or not message:
                emit('error', {'message': 'Dados incompletos'})
                return

            # Validações
            if len(message) > 500:
                emit(
                    'error', {'message': 'Mensagem muito longa (máximo 500 caracteres)'})
                return

            room = room_manager.get_room(room_id)
            if not room:
                emit('error', {'message': 'Sala não encontrada'})
                return

            if not room.is_active:
                emit('error', {'message': 'Sala não está ativa'})
                return

            timestamp = datetime.now().strftime('%H:%M:%S')

            message_data = {
                'username': username,
                'message': message,
                'timestamp': timestamp
            }

            # Salvar mensagem
            room_manager.add_message_to_room(room_id, username, message)

            # Enviar para todos na sala
            emit('chat_message', message_data, room=room_id)

        except Exception as e:
            print(f"Erro ao enviar mensagem: {e}")
            emit('error', {'message': 'Erro ao enviar mensagem'})
