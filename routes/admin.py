from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
from models.room import room_manager
from config import Config

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin')
def admin():
    return render_template('admin.html')


@admin_bp.route('/api/admin/stats')
def admin_stats():
    try:
        # Executar limpeza de salas expiradas a cada vez que as estatísticas são solicitadas
        expired_count = room_manager.cleanup_expired_rooms()
        if expired_count > 0:
            print(f"Cleaned up {expired_count} expired rooms")

        stats = room_manager.get_stats()
        return jsonify(stats)

    except Exception as e:
        print(f"Erro ao obter estatísticas do admin: {e}")
        return jsonify({
            'total_rooms': 0,
            'active_rooms': 0,
            'online_users': 0,
            'recent_activity': []
        })


@admin_bp.route('/api/admin/rooms/<room_id>', methods=['DELETE'])
def delete_room(room_id):
    try:
        room = room_manager.get_room(room_id)
        if not room:
            return jsonify({'error': 'Sala não encontrada'}), 404

        success = room_manager.delete_room(room_id)

        if success:
            return jsonify({'message': 'Sala excluída com sucesso'})
        return jsonify({'error': 'Erro ao excluir sala'}), 500

    except Exception as e:
        print(f"Erro ao excluir sala: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500


@admin_bp.route('/api/admin/settings', methods=['POST'])
def update_settings():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400

        # Validar senha de admin
        admin_password = data.get('admin_password', '')
        if not admin_password:
            return jsonify({'error': 'Senha de administrador é obrigatória'}), 400

        if admin_password != Config.ADMIN_PASSWORD:
            return jsonify({'error': 'Senha de administrador incorreta'}), 401

        # Atualizar configurações
        # Em um sistema real, você atualizaria as configurações no banco de dados ou arquivo de configuração
        max_rooms = data.get('max_rooms', 50)
        room_timeout = data.get('room_timeout', 24)

        # Validações
        try:
            max_rooms = int(max_rooms)
            room_timeout = int(room_timeout)

            if max_rooms < 1 or max_rooms > 1000:
                return jsonify({'error': 'Máximo de salas deve estar entre 1 e 1000'}), 400

            if room_timeout < 1 or room_timeout > 168:  # Máximo 1 semana
                return jsonify({'error': 'Timeout deve estar entre 1 e 168 horas'}), 400

        except ValueError:
            return jsonify({'error': 'Valores numéricos inválidos'}), 400

        # Por ora, apenas simulamos sucesso
        return jsonify({'message': 'Configurações atualizadas com sucesso'})

    except Exception as e:
        print(f"Erro ao atualizar configurações: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500


@admin_bp.route('/api/admin/cleanup', methods=['POST'])
def cleanup_rooms():
    try:
        expired_count = room_manager.cleanup_expired_rooms()
        return jsonify({
            'message': f'{expired_count} salas expiradas foram limpas',
            'cleaned_count': expired_count
        })

    except Exception as e:
        print(f"Erro ao limpar salas: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500
