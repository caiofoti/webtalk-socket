from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
from models.room import gerenciador_salas
from config import Config

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin')
def admin():
    return render_template('admin.html')


@admin_bp.route('/api/admin/estatisticas')
def estatisticas_admin():
    try:
        estatisticas = gerenciador_salas.obter_estatisticas()
        return jsonify(estatisticas)

    except Exception as e:
        print(f"Erro ao obter estatísticas do admin: {e}")
        return jsonify({
            'total_salas': 0,
            'salas_ativas': 0,
            'usuarios_online': 0,
            'atividade_recente': []
        })


@admin_bp.route('/api/admin/salas/<id_sala>', methods=['DELETE'])
def excluir_sala(id_sala):
    try:
        sala = gerenciador_salas.obter_sala(id_sala)
        if not sala:
            return jsonify({'erro': 'Sala não encontrada'}), 404

        sucesso = gerenciador_salas.excluir_sala(id_sala)

        if sucesso:
            return jsonify({'mensagem': 'Sala excluída com sucesso'})
        return jsonify({'erro': 'Erro ao excluir sala'}), 500

    except Exception as e:
        print(f"Erro ao excluir sala: {e}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500


@admin_bp.route('/api/admin/configuracoes', methods=['POST'])
def atualizar_configuracoes():
    try:
        dados = request.json
        if not dados:
            return jsonify({'erro': 'Dados não fornecidos'}), 400

        senha_admin = dados.get('senha_admin', '')
        if not senha_admin:
            return jsonify({'erro': 'Senha de administrador é obrigatória'}), 400

        if senha_admin != Config.ADMIN_PASSWORD:
            return jsonify({'erro': 'Senha de administrador incorreta'}), 401

        maximo_salas = dados.get('maximo_salas', 50)
        timeout_sala = dados.get('timeout_sala', 24)

        try:
            maximo_salas = int(maximo_salas)
            timeout_sala = int(timeout_sala)

            if maximo_salas < 1 or maximo_salas > 1000:
                return jsonify({'erro': 'Máximo de salas deve estar entre 1 e 1000'}), 400

            if timeout_sala < 1 or timeout_sala > 168:
                return jsonify({'erro': 'Timeout deve estar entre 1 e 168 horas'}), 400

        except ValueError:
            return jsonify({'erro': 'Valores numéricos inválidos'}), 400

        return jsonify({'mensagem': 'Configurações atualizadas com sucesso'})

    except Exception as e:
        print(f"Erro ao atualizar configurações: {e}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500


@admin_bp.route('/api/admin/limpeza', methods=['POST'])
def limpar_salas():
    try:
        contador_expiradas = gerenciador_salas.limpar_salas_expiradas()
        return jsonify({
            'mensagem': f'{contador_expiradas} salas expiradas foram limpas',
            'contador_limpas': contador_expiradas
        })

    except Exception as e:
        print(f"Erro ao limpar salas: {e}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500
    try:
        contador_expiradas = gerenciador_salas.limpar_salas_expiradas()
        return jsonify({
            'mensagem': f'{contador_expiradas} salas expiradas foram limpas',
            'contador_limpas': contador_expiradas
        })

    except Exception as e:
        print(f"Erro ao limpar salas: {e}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500
