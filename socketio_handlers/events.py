from flask import request
from flask_socketio import emit, join_room, leave_room
from models.room import gerenciador_salas
from datetime import datetime
import uuid
import time


def registrar_eventos_socketio(socketio):
    """Registra todos os manipuladores de eventos WebSocket"""

    @socketio.on('connect')
    def manipular_conexao():
        """Manipula nova conexão WebSocket"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] WS Connect: {request.sid[:8]}")
        return True

    @socketio.on('disconnect')
    def manipular_desconexao():
        """Manipula desconexão WebSocket"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] WS Disconnect: {request.sid[:8]}")

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

            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] User Join: {nome_usuario} -> Room {id_sala}")

            # Enviar mensagens históricas VERIFICANDO SOFT DELETE
            for mensagem in sala.mensagens[-20:]:
                # VERIFICAR SE A MENSAGEM FOI DELETADA
                if mensagem.get('deletada'):
                    # Enviar como mensagem deletada
                    if mensagem.get('tipo') == 'arquivo':
                        emit('mensagem_chat', {
                            'id': mensagem['id'],
                            'nome_usuario': mensagem['nome_usuario'],
                            'mensagem': 'Arquivo deletado',
                            'tipo': 'arquivo_deletado',
                            'horario': mensagem['horario'],
                            'deletada': True
                        })
                    else:
                        emit('mensagem_chat', {
                            'id': mensagem['id'],
                            'nome_usuario': mensagem['nome_usuario'],
                            'mensagem': 'Mensagem deletada',
                            'tipo': 'texto_deletado',
                            'horario': mensagem['horario'],
                            'deletada': True
                        })
                elif mensagem.get('tipo') == 'arquivo':
                    emit('arquivo_compartilhado', mensagem)
                else:
                    emit('mensagem_chat', mensagem)

        except Exception as e:
            print(f"[ERROR] Entrada na sala: {e}")
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

                timestamp = time.strftime("%H:%M:%S")
                print(f"[{timestamp}] User Leave: {nome_usuario} <- Room {id_sala}")

        except Exception as e:
            print(f"[ERROR] Saída da sala: {e}")

    @socketio.on('mensagem_chat')
    def manipular_mensagem(dados):
        """Processa e distribui mensagens de chat"""
        try:
            id_sala = dados.get('id_sala')
            nome_usuario = dados.get('nome_usuario')
            mensagem = dados.get('mensagem', '').strip()

            timestamp = time.strftime("%H:%M:%S")
            print(
                f"[{timestamp}] Chat Message: {nome_usuario} in {id_sala} ({len(mensagem)} chars)")

            if not id_sala or not nome_usuario or not mensagem:
                emit('erro', {'mensagem': 'Dados incompletos'})
                return

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

            # Salvar mensagem
            mensagem_obj = gerenciador_salas.adicionar_mensagem_na_sala(
                id_sala, nome_usuario, mensagem)

            if mensagem_obj:
                emit('mensagem_chat', mensagem_obj, room=id_sala)
                print(f"  Message saved: ID {mensagem_obj['id'][:8]}")
            else:
                emit('erro', {'mensagem': 'Erro ao salvar mensagem'})

        except Exception as e:
            print(f"[ERROR] Mensagem chat: {e}")
            emit('erro', {'mensagem': 'Erro ao enviar mensagem'})

    @socketio.on('deletar_mensagem')
    def manipular_deletar_mensagem(dados):
        """Processa deleção de mensagem via WebSocket"""
        try:
            id_sala = dados.get('id_sala')
            id_mensagem = dados.get('id_mensagem')
            nome_usuario = dados.get('nome_usuario')

            timestamp = time.strftime("%H:%M:%S")
            print(
                f"[{timestamp}] Delete Message: {nome_usuario} deleting {id_mensagem[:8]} in {id_sala}")

            if not all([id_sala, id_mensagem, nome_usuario]):
                emit('erro', {'mensagem': 'Dados incompletos'})
                return

            sala = gerenciador_salas.obter_sala(id_sala)
            if not sala:
                emit('erro', {'mensagem': 'Sala não encontrada'})
                return

            # Tentar remover a mensagem
            sucesso = gerenciador_salas.remover_mensagem_da_sala(
                id_sala, id_mensagem, nome_usuario)

            if sucesso:
                emit('mensagem_removida', {
                    'id_mensagem': id_mensagem,
                    'nome_usuario': nome_usuario
                }, room=id_sala)
                print(f"  Delete success: Message {id_mensagem[:8]}")
            else:
                emit(
                    'erro', {'mensagem': 'Não foi possível remover a mensagem'})
                print(f"  Delete failed: Permission denied or not found")

        except Exception as e:
            print(f"[ERROR] Deletar mensagem: {e}")
            emit('erro', {'mensagem': 'Erro ao deletar mensagem'})

    @socketio.on('arquivo_compartilhado')
    def manipular_arquivo_compartilhado(dados):
        """Notifica usuários sobre novo arquivo compartilhado"""
        try:
            id_sala = dados.get('id_sala')
            nome_usuario = dados.get('nome_usuario')
            nome_arquivo = dados.get('nome_arquivo')
            tipo_arquivo = dados.get('tipo_arquivo')
            id_mensagem = dados.get('id')

            timestamp = time.strftime("%H:%M:%S")
            print(
                f"[{timestamp}] File Share: {nome_usuario} shared {nome_arquivo} ({tipo_arquivo}) in {id_sala}")

            if not all([id_sala, nome_usuario, nome_arquivo, tipo_arquivo]):
                emit('erro', {'mensagem': 'Dados incompletos'})
                return

            sala = gerenciador_salas.obter_sala(id_sala)
            if not sala:
                emit('erro', {'mensagem': 'Sala não encontrada'})
                return

            horario = datetime.now().strftime('%H:%M:%S')

            dados_arquivo = {
                'id': id_mensagem or str(uuid.uuid4()),
                'nome_usuario': nome_usuario,
                'tipo': 'arquivo',
                'nome_arquivo': nome_arquivo,
                'tipo_arquivo': tipo_arquivo,
                'horario': horario
            }

            emit('arquivo_compartilhado', dados_arquivo, room=id_sala)
            print(f"  File notification sent to {len(sala.usuarios)} users")

        except Exception as e:
            print(f"[ERROR] Arquivo compartilhado: {e}")
            emit('erro', {'mensagem': 'Erro ao compartilhar arquivo'})
