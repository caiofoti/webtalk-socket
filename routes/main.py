from flask import Blueprint, render_template, request, jsonify
from models.room import room_manager

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/chat/<room_id>')
def chat(room_id):
    room = room_manager.get_room(room_id)
    if not room:
        return render_template('index.html', error='Sala não encontrada!')
    return render_template('chat.html', room=room)


@main_bp.route('/api/rooms', methods=['GET'])
def get_rooms():
    try:
        rooms = [room.to_dict()
                 for room in room_manager.get_all_rooms() if room.is_active]
        return jsonify(rooms)
    except Exception as e:
        print(f"Erro ao buscar salas: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500


@main_bp.route('/api/rooms', methods=['POST'])
def create_room():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400

        name = data.get('name', '').strip() if data.get('name') else ''
        creator = data.get('creator', '').strip(
        ) if data.get('creator') else ''
        password = data.get('password', '').strip(
        ) if data.get('password') else None

        if not name or not creator:
            return jsonify({'error': 'Nome da sala e criador são obrigatórios'}), 400

        # Verificar se o nome da sala não é muito longo
        if len(name) > 50:
            return jsonify({'error': 'Nome da sala muito longo (máximo 50 caracteres)'}), 400

        if len(creator) > 30:
            return jsonify({'error': 'Nome do criador muito longo (máximo 30 caracteres)'}), 400

        room = room_manager.create_room(name, creator, password)
        return jsonify({'room_id': room.id, 'message': 'Sala criada com sucesso!'})

    except Exception as e:
        print(f"Erro ao criar sala: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500


@main_bp.route('/api/rooms/<room_id>/join', methods=['POST'])
def join_room(room_id):
    try:
        data = request.json or {}
        password = data.get('password', '').strip(
        ) if data.get('password') else ''

        room = room_manager.get_room(room_id)
        if not room:
            return jsonify({'error': 'Sala não encontrada'}), 404

        if not room.is_active:
            return jsonify({'error': 'Sala não está mais ativa'}), 403

        if not room_manager.verify_room_password(room_id, password):
            return jsonify({'error': 'Senha incorreta!'}), 401

        return jsonify({'message': 'Acesso autorizado!'})

    except Exception as e:
        print(f"Erro ao entrar na sala: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500
