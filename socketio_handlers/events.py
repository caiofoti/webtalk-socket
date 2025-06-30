from flask import request
from flask_socketio import emit, join_room, leave_room
from models.room import gerenciador_salas
from datetime import datetime


def registrar_eventos_socketio(socketio):
    """Registra todos os manipuladores de eventos WebSocket"""

    @socketio.on('connect')
    def manipular_conexao():
        """Manipula nova conexão WebSocket"""
        print(f'[WEBSOCKET] Nova conexão estabelecida: SID={request.sid}')
        return True

    @socketio.on('disconnect')
    def manipular_desconexao():
        """Manipula desconexão WebSocket"""
        print(f'[WEBSOCKET] Conexão encerrada: SID={request.sid}')

    @socketio.on('entrar')
    def manipular_entrada(dados):
        """Processa entrada de usuário em sala de chat"""
        try:
            id_sala = dados.get('id_sala')
            nome_usuario = dados.get('nome_usuario')

            if not id_sala or not nome_usuario:
                emit(
                    'erro', {'mensagem': 'ID da sala e nome de usuário são obrigatórios'})
                return

            sala = gerenciador_salas.obter_sala(id_sala)
            if not sala:
                emit('erro', {'mensagem': 'Sala não encontrada'})
                return

            if not sala.esta_ativa:
                emit('erro', {'mensagem': 'Sala não está ativa'})
                return

            join_room(id_sala)
            sala.adicionar_usuario(nome_usuario)

            emit('usuario_entrou', {
                 'nome_usuario': nome_usuario}, room=id_sala)
            print(f'[ROOM] Usuário "{nome_usuario}" entrou na sala {id_sala}')

            # Enviar mensagens históricas para o usuário que acabou de entrar
            for mensagem in sala.mensagens[-20:]:  # Últimas 20 mensagens
                emit('mensagem_chat', mensagem)

        except Exception as e:
            print(f"[ERROR] Falha ao processar entrada na sala: {e}")
            emit('erro', {'mensagem': 'Erro interno do servidor'})

    @socketio.on('sair')
    def manipular_saida(dados):
        """Processa saída de usuário de sala de chat"""
        try:
            id_sala = dados.get('id_sala')
            nome_usuario = dados.get('nome_usuario')

            if id_sala and nome_usuario:
                sala = gerenciador_salas.obter_sala(id_sala)
                if sala:
                    sala.remover_usuario(nome_usuario)

                leave_room(id_sala)
                emit('usuario_saiu', {
                     'nome_usuario': nome_usuario}, room=id_sala)
                print(
                    f'[ROOM] Usuário "{nome_usuario}" saiu da sala {id_sala}')

        except Exception as e:
            print(f"[ERROR] Falha ao processar saída da sala: {e}")

    @socketio.on('mensagem_chat')
    def manipular_mensagem(dados):
        """Processa e distribui mensagens de chat"""
        try:
            id_sala = dados.get('id_sala')
            nome_usuario = dados.get('nome_usuario')
            mensagem = dados.get('mensagem', '').strip()

            if not id_sala or not nome_usuario or not mensagem:
                emit('erro', {'mensagem': 'Dados incompletos'})
                return

            # Validações
            if len(mensagem) > 500:
                emit(
                    'erro', {'mensagem': 'Mensagem muito longa (máximo 500 caracteres)'})
                return

            sala = gerenciador_salas.obter_sala(id_sala)
            if not sala:
                emit('erro', {'mensagem': 'Sala não encontrada'})
                return

            if not sala.esta_ativa:
                emit('erro', {'mensagem': 'Sala não está ativa'})
                return

            horario = datetime.now().strftime('%H:%M:%S')

            dados_mensagem = {
                'nome_usuario': nome_usuario,
                'mensagem': mensagem,
                'horario': horario
            }

            # Salvar mensagem
            gerenciador_salas.adicionar_mensagem_na_sala(
                id_sala, nome_usuario, mensagem)

            # Enviar para todos na sala
            emit('mensagem_chat', dados_mensagem, room=id_sala)

        except Exception as e:
            print(f"[ERROR] Falha ao processar mensagem: {e}")
            emit('erro', {'mensagem': 'Erro ao enviar mensagem'})
