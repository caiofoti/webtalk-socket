import os
import uuid
import shutil
from flask import Blueprint, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from models.room import gerenciador_salas

main_bp = Blueprint('main', __name__)

# Configurações de upload
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# Criar pasta de uploads se não existir
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@main_bp.route('/')
def index():
    """Renderiza página inicial da aplicação"""
    return render_template('index.html')


@main_bp.route('/chat/<id_sala>')
def chat(id_sala):
    """Renderiza interface de chat para sala específica"""
    sala = gerenciador_salas.obter_sala(id_sala)
    if not sala:
        return render_template('index.html', erro='Sala não encontrada!')

    # Garantir que o objeto sala tem todos os dados necessários
    room_data = {
        'id': sala.id,
        'name': sala.nome,
        'criador': sala.criador,
        'senha': bool(sala.senha)
    }

    return render_template('chat.html', room=room_data)


@main_bp.route('/api/salas', methods=['GET'])
def obter_salas():
    """API endpoint para listar todas as salas ativas"""
    try:
        # Debug: verificar user agent para mobile
        user_agent = request.headers.get('User-Agent', '')
        is_mobile = any(device in user_agent.lower()
                        for device in ['mobile', 'android', 'iphone', 'ipad'])

        salas = [sala.para_dicionario()
                 for sala in gerenciador_salas.obter_todas_salas() if sala.esta_ativa]

        print(f"[API] Retornando {len(salas)} salas. Mobile: {is_mobile}")

        return jsonify(salas)
    except Exception as e:
        print(f"[API ERROR] Falha ao buscar salas: {e}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500


@main_bp.route('/api/salas', methods=['POST'])
def criar_sala():
    """API endpoint para criação de nova sala de chat"""
    try:
        dados = request.json
        if not dados:
            return jsonify({'erro': 'Dados não fornecidos'}), 400

        nome = dados.get('nome', '').strip() if dados.get('nome') else ''
        criador = dados.get('criador', '').strip(
        ) if dados.get('criador') else ''
        senha = dados.get('senha', '').strip() if dados.get('senha') else None

        if not nome or not criador:
            return jsonify({'erro': 'Nome da sala e criador são obrigatórios'}), 400

        if len(nome) > 50:
            return jsonify({'erro': 'Nome da sala muito longo (máximo 50 caracteres)'}), 400

        if len(criador) > 30:
            return jsonify({'erro': 'Nome do criador muito longo (máximo 30 caracteres)'}), 400

        sala = gerenciador_salas.criar_sala(nome, criador, senha)
        return jsonify({'id_sala': sala.id, 'mensagem': 'Sala criada com sucesso!'})

    except Exception as e:
        print(f"[API ERROR] Falha ao criar sala: {e}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500


@main_bp.route('/api/salas/<id_sala>/entrar', methods=['POST'])
def entrar_sala(id_sala):
    """API endpoint para validação de acesso à sala"""
    try:
        dados = request.json or {}
        senha = dados.get('senha', '').strip() if dados.get('senha') else ''

        sala = gerenciador_salas.obter_sala(id_sala)
        if not sala:
            return jsonify({'erro': 'Sala não encontrada'}), 404

        if not sala.esta_ativa:
            return jsonify({'erro': 'Sala não está mais ativa'}), 403

        if not gerenciador_salas.verificar_senha_sala(id_sala, senha):
            return jsonify({'erro': 'Senha incorreta!'}), 401

        return jsonify({'mensagem': 'Acesso autorizado!'})

    except Exception as e:
        print(f"[API ERROR] Falha ao processar entrada na sala: {e}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500


@main_bp.route('/api/salas/<id_sala>/upload', methods=['POST'])
def upload_arquivo(id_sala):
    """API endpoint para upload de arquivos na sala com validação robusta e suporte móvel"""
    arquivo_salvo = None
    pasta_temp = None
    try:
        sala = gerenciador_salas.obter_sala(id_sala)
        if not sala:
            return jsonify({'erro': 'Sala não encontrada'}), 404

        if not sala.esta_ativa:
            return jsonify({'erro': 'Sala não está ativa'}), 403

        if 'arquivo' not in request.files:
            return jsonify({'erro': 'Nenhum arquivo enviado'}), 400

        arquivo = request.files['arquivo']
        nome_usuario = request.form.get('nome_usuario', '').strip()

        if not nome_usuario:
            return jsonify({'erro': 'Nome de usuário é obrigatório'}), 400

        if arquivo.filename == '':
            return jsonify({'erro': 'Nenhum arquivo selecionado'}), 400

        # MOBILE-SPECIFIC: Better file validation for mobile uploads
        # Check if request is from mobile device
        user_agent = request.headers.get('User-Agent', '').lower()
        is_mobile = any(mobile in user_agent for mobile in [
                        'mobile', 'android', 'iphone', 'ipad', 'tablet'])

        # Verificar tamanho do arquivo
        arquivo.seek(0, os.SEEK_END)
        tamanho_arquivo = arquivo.tell()
        arquivo.seek(0)

        # Mobile devices may have smaller memory constraints
        max_size = MAX_FILE_SIZE if not is_mobile else min(
            MAX_FILE_SIZE, 8 * 1024 * 1024)  # 8MB for mobile

        if tamanho_arquivo > max_size:
            max_mb = max_size // (1024 * 1024)
            return jsonify({'erro': f'Arquivo muito grande (máximo {max_mb}MB para dispositivos móveis)'}), 400

        if tamanho_arquivo == 0:
            return jsonify({'erro': 'Arquivo está vazio'}), 400

        if arquivo and allowed_file(arquivo.filename):
            # Gerar nome único para o arquivo
            nome_original = secure_filename(arquivo.filename)
            if not nome_original:
                return jsonify({'erro': 'Nome de arquivo inválido'}), 400

            # MOBILE FIX: Handle special characters and spaces better
            nome_original = nome_original.replace(' ', '_')

            extensao = nome_original.rsplit('.', 1)[1].lower()
            nome_unico = f"{uuid.uuid4().hex}.{extensao}"

            # Criar pasta da sala se não existir
            pasta_sala = os.path.join(UPLOAD_FOLDER, id_sala)
            if not os.path.exists(pasta_sala):
                os.makedirs(pasta_sala)

            # Salvar primeiro em arquivo temporário
            pasta_temp = os.path.join(UPLOAD_FOLDER, 'temp')
            os.makedirs(pasta_temp, exist_ok=True)

            caminho_temp = os.path.join(pasta_temp, nome_unico)
            caminho_final = os.path.join(pasta_sala, nome_unico)

            # Salvar arquivo temporário
            try:
                arquivo.save(caminho_temp)
                arquivo_salvo = caminho_temp

                # Validar arquivo salvo
                if not os.path.exists(caminho_temp):
                    return jsonify({'erro': 'Falha ao salvar arquivo temporário'}), 500

                tamanho_salvo = os.path.getsize(caminho_temp)
                if tamanho_salvo == 0:
                    return jsonify({'erro': 'Arquivo salvo está vazio'}), 500

                if tamanho_salvo != tamanho_arquivo:
                    return jsonify({'erro': 'Arquivo corrompido durante upload'}), 500

                # Validar conteúdo do arquivo baseado na extensão
                if not validar_conteudo_arquivo(caminho_temp, extensao):
                    return jsonify({'erro': 'Conteúdo do arquivo não corresponde ao tipo esperado'}), 400

            except Exception as save_error:
                print(f"[ERROR] Falha ao salvar arquivo: {save_error}")
                return jsonify({'erro': 'Erro ao salvar arquivo no servidor'}), 500

            # Registrar no banco de dados ANTES de mover o arquivo
            mensagem_arquivo = gerenciador_salas.adicionar_arquivo_na_sala(
                id_sala, nome_usuario, nome_original, caminho_final, extensao
            )

            if not mensagem_arquivo:
                return jsonify({'erro': 'Erro ao registrar arquivo no banco de dados'}), 500

            # Mover arquivo para localização final apenas se tudo deu certo
            try:
                shutil.move(caminho_temp, caminho_final)
                arquivo_salvo = caminho_final

                # Verificar se o arquivo foi movido corretamente
                if not os.path.exists(caminho_final) or os.path.getsize(caminho_final) == 0:
                    # Reverter registro no banco
                    gerenciador_salas.remover_mensagem_da_sala(
                        id_sala, mensagem_arquivo['id'], nome_usuario)
                    return jsonify({'erro': 'Falha ao finalizar upload'}), 500

            except Exception as move_error:
                print(f"[ERROR] Falha ao mover arquivo: {move_error}")
                # Reverter registro no banco
                gerenciador_salas.remover_mensagem_da_sala(
                    id_sala, mensagem_arquivo['id'], nome_usuario)
                return jsonify({'erro': 'Erro ao finalizar upload'}), 500

            return jsonify({
                'mensagem': 'Arquivo enviado com sucesso!',
                'nome_arquivo': nome_original,
                'tipo_arquivo': extensao,
                'id_mensagem': mensagem_arquivo['id'],
                'tamanho': tamanho_arquivo,
                'mobile': is_mobile
            })

        return jsonify({'erro': 'Tipo de arquivo não permitido. Use: PDF, JPG, JPEG, PNG'}), 400

    except Exception as e:
        print(f"[API ERROR] Falha no upload: {e}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500

    finally:
        # Cleanup de arquivos temporários
        if arquivo_salvo and arquivo_salvo.startswith(os.path.join(UPLOAD_FOLDER, 'temp')):
            try:
                if os.path.exists(arquivo_salvo):
                    os.remove(arquivo_salvo)
                    print(
                        f"[CLEANUP] Arquivo temporário removido: {arquivo_salvo}")
            except Exception as cleanup_error:
                print(
                    f"[ERROR] Falha ao limpar arquivo temporário: {cleanup_error}")


def validar_conteudo_arquivo(caminho_arquivo, extensao_esperada):
    """Valida se o conteúdo do arquivo corresponde à extensão"""
    try:
        with open(caminho_arquivo, 'rb') as f:
            cabecalho = f.read(16)

        # Assinaturas de arquivo conhecidas
        assinaturas = {
            'pdf': [b'%PDF'],
            'jpg': [b'\xFF\xD8\xFF'],
            'jpeg': [b'\xFF\xD8\xFF'],
            'png': [b'\x89PNG\r\n\x1a\n']
        }

        if extensao_esperada in assinaturas:
            for assinatura in assinaturas[extensao_esperada]:
                if cabecalho.startswith(assinatura):
                    return True
            return False

        return True  # Para extensões não validadas

    except Exception as e:
        print(f"[ERROR] Falha na validação de conteúdo: {e}")
        return False


@main_bp.route('/api/salas/<id_sala>/download/<path:nome_arquivo>')
def download_arquivo(id_sala, nome_arquivo):
    """API endpoint para download de arquivos da sala"""
    try:
        sala = gerenciador_salas.obter_sala(id_sala)
        if not sala:
            return jsonify({'erro': 'Sala não encontrada'}), 404

        pasta_sala = os.path.join(UPLOAD_FOLDER, id_sala)

        # Procurar o arquivo correto nas mensagens da sala
        arquivo_fisico_encontrado = None

        # Primeiro, procurar nas mensagens para encontrar o arquivo físico correto
        for mensagem in sala.mensagens:
            if (mensagem.get('tipo') == 'arquivo' and
                    mensagem.get('nome_arquivo') == nome_arquivo):
                caminho_arquivo = mensagem.get('caminho_arquivo')
                if caminho_arquivo and os.path.exists(caminho_arquivo):
                    arquivo_fisico_encontrado = os.path.basename(
                        caminho_arquivo)
                    break

        # Se não encontrou, tentar busca direta
        if not arquivo_fisico_encontrado:
            caminho_direto = os.path.join(pasta_sala, nome_arquivo)
            if os.path.exists(caminho_direto):
                arquivo_fisico_encontrado = nome_arquivo

        if not arquivo_fisico_encontrado:
            print(
                f"[DOWNLOAD ERROR] Arquivo não encontrado: {nome_arquivo} na sala {id_sala}")
            return jsonify({'erro': 'Arquivo não encontrado'}), 404

        # Verificar se é uma requisição para visualização (sem download forçado)
        force_download = request.args.get(
            'download', 'false').lower() == 'true'

        return send_from_directory(
            pasta_sala,
            arquivo_fisico_encontrado,
            as_attachment=force_download,
            download_name=nome_arquivo if force_download else None
        )

    except Exception as e:
        print(f"[API ERROR] Falha no download: {e}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500


@main_bp.route('/api/salas/<id_sala>/mensagens/<id_mensagem>', methods=['DELETE'])
def deletar_mensagem(id_sala, id_mensagem):
    """API endpoint para deletar mensagem ou arquivo"""
    try:
        dados = request.json or {}
        nome_usuario = dados.get('nome_usuario', '').strip()

        if not nome_usuario:
            return jsonify({'erro': 'Nome de usuário é obrigatório'}), 400

        sala = gerenciador_salas.obter_sala(id_sala)
        if not sala:
            return jsonify({'erro': 'Sala não encontrada'}), 404

        if not sala.esta_ativa:
            return jsonify({'erro': 'Sala não está ativa'}), 403

        # Tentar remover a mensagem
        sucesso = gerenciador_salas.remover_mensagem_da_sala(
            id_sala, id_mensagem, nome_usuario)

        if sucesso:
            return jsonify({'mensagem': 'Mensagem removida com sucesso'})
        else:
            return jsonify({'erro': 'Mensagem não encontrada ou você não tem permissão para removê-la'}), 403

    except Exception as e:
        print(f"[API ERROR] Falha ao deletar mensagem: {e}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500
        return jsonify({'erro': 'Nome de usuário é obrigatório'}), 400

        sala = gerenciador_salas.obter_sala(id_sala)
        if not sala:
            return jsonify({'erro': 'Sala não encontrada'}), 404

        if not sala.esta_ativa:
            return jsonify({'erro': 'Sala não está ativa'}), 403

        # Tentar remover a mensagem
        sucesso = gerenciador_salas.remover_mensagem_da_sala(
            id_sala, id_mensagem, nome_usuario)

        if sucesso:
            return jsonify({'mensagem': 'Mensagem removida com sucesso'})
        else:
            return jsonify({'erro': 'Mensagem não encontrada ou você não tem permissão para removê-la'}), 403

    except Exception as e:
        print(f"[API ERROR] Falha ao deletar mensagem: {e}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500
