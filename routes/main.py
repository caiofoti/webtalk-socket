from flask import Blueprint, render_template, request, jsonify
from models.room import gerenciador_salas

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/chat/<id_sala>')
def chat(id_sala):
    sala = gerenciador_salas.obter_sala(id_sala)
    if not sala:
        return render_template('index.html', erro='Sala não encontrada!')
    return render_template('chat.html', room=sala)


@main_bp.route('/api/salas', methods=['GET'])
def obter_salas():
    try:
        salas = [sala.para_dicionario()
                 for sala in gerenciador_salas.obter_todas_salas() if sala.esta_ativa]
        return jsonify(salas)
    except Exception as e:
        print(f"Erro ao buscar salas: {e}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500


@main_bp.route('/api/salas', methods=['POST'])
def criar_sala():
    try:
        dados = request.json
        if not dados:
            return jsonify({'erro': 'Dados não fornecidos'}), 400

        nome = dados.get('nome', '').strip() if dados.get('nome') else ''
        criador = dados.get('criador', '').strip(
        ) if dados.get('criador') else ''
        senha = dados.get('senha', '').strip(
        ) if dados.get('senha') else None

        if not nome or not criador:
            return jsonify({'erro': 'Nome da sala e criador são obrigatórios'}), 400

        # Verificar se o nome da sala não é muito longo
        if len(nome) > 50:
            return jsonify({'erro': 'Nome da sala muito longo (máximo 50 caracteres)'}), 400

        if len(criador) > 30:
            return jsonify({'erro': 'Nome do criador muito longo (máximo 30 caracteres)'}), 400

        sala = gerenciador_salas.criar_sala(nome, criador, senha)
        return jsonify({'id_sala': sala.id, 'mensagem': 'Sala criada com sucesso!'})

    except Exception as e:
        print(f"Erro ao criar sala: {e}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500


@main_bp.route('/api/salas/<id_sala>/entrar', methods=['POST'])
def entrar_sala(id_sala):
    try:
        dados = request.json or {}
        senha = dados.get('senha', '').strip(
        ) if dados.get('senha') else ''

        sala = gerenciador_salas.obter_sala(id_sala)
        if not sala:
            return jsonify({'erro': 'Sala não encontrada'}), 404

        if not sala.esta_ativa:
            return jsonify({'erro': 'Sala não está mais ativa'}), 403

        if not gerenciador_salas.verificar_senha_sala(id_sala, senha):
            return jsonify({'erro': 'Senha incorreta!'}), 401

        return jsonify({'mensagem': 'Acesso autorizado!'})

    except Exception as e:
        print(f"Erro ao entrar na sala: {e}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500
