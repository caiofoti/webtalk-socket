import uuid
import time
from datetime import datetime, timedelta
import sqlite3
import os
import json
import threading
import shutil


class Sala:
    def __init__(self, id, nome, criador, criado_em=None, senha=None, esta_ativa=True):
        self.id = id
        self.nome = nome
        self.criador = criador
        self.senha = senha
        self.esta_ativa = esta_ativa
        self.criado_em = criado_em or datetime.now().isoformat()
        self.mensagens = []
        self.usuarios = set()
        self.ultima_atividade = time.time()

    def para_dicionario(self):
        """Converte objeto Sala para dicionário serializável"""
        return {
            'id': self.id,
            'nome': self.nome,
            'criador': self.criador,
            'criado_em': self.criado_em,
            'tem_senha': bool(self.senha),
            'esta_ativa': self.esta_ativa,
            'contador_usuarios': len(self.usuarios),
            'contador_mensagens': len(self.mensagens)
        }

    def adicionar_usuario(self, nome_usuario):
        """Adiciona usuário à sala e atualiza atividade"""
        self.usuarios.add(nome_usuario)
        self.atualizar_atividade()

    def remover_usuario(self, nome_usuario):
        """Remove usuário da sala e atualiza atividade"""
        if nome_usuario in self.usuarios:
            self.usuarios.remove(nome_usuario)
        self.atualizar_atividade()

    def adicionar_mensagem(self, mensagem):
        """Adiciona mensagem ao histórico da sala"""
        self.mensagens.append(mensagem)
        self.atualizar_atividade()
        if len(self.mensagens) > 100:  # Limitar a 100 mensagens mais recentes
            self.mensagens = self.mensagens[-100:]

    def adicionar_arquivo(self, nome_usuario, nome_arquivo, caminho_arquivo, tipo_arquivo):
        """Adiciona informação de arquivo compartilhado"""
        mensagem_arquivo = {
            'id': str(uuid.uuid4()),  # Add unique ID for deletion
            'nome_usuario': nome_usuario,
            'tipo': 'arquivo',
            'nome_arquivo': nome_arquivo,
            'caminho_arquivo': caminho_arquivo,
            'tipo_arquivo': tipo_arquivo,
            'horario': datetime.now().strftime('%H:%M:%S')
        }
        self.adicionar_mensagem(mensagem_arquivo)
        return mensagem_arquivo

    def adicionar_mensagem_texto(self, nome_usuario, mensagem):
        """Adiciona mensagem de texto com ID único"""
        mensagem_obj = {
            'id': str(uuid.uuid4()),
            'nome_usuario': nome_usuario,
            'mensagem': mensagem,
            'tipo': 'texto',
            'horario': datetime.now().strftime('%H:%M:%S')
        }
        self.adicionar_mensagem(mensagem_obj)
        return mensagem_obj

    def remover_mensagem(self, id_mensagem, nome_usuario):
        """Marca mensagem como deletada se o usuário for o autor"""
        for mensagem in self.mensagens:
            if mensagem.get('id') == id_mensagem:
                if mensagem.get('nome_usuario') == nome_usuario:
                    # Marcar como deletada ao invés de remover
                    mensagem['deletada'] = True
                    mensagem['conteudo_original'] = mensagem.get(
                        'mensagem', mensagem.get('nome_arquivo', ''))

                    if mensagem.get('tipo') == 'arquivo':
                        mensagem['mensagem'] = 'Arquivo deletado'
                        # Opcional: remover arquivo físico
                        if mensagem.get('caminho_arquivo') and os.path.exists(mensagem['caminho_arquivo']):
                            try:
                                os.remove(mensagem['caminho_arquivo'])
                                print(
                                    f"[DELETE] Arquivo físico removido: {mensagem['caminho_arquivo']}")
                            except Exception as e:
                                print(f"[ERROR] Falha ao remover arquivo: {e}")
                    else:
                        mensagem['mensagem'] = 'Mensagem deletada'

                    return True
                else:
                    return False  # Não é o autor
        return False  # Mensagem não encontrada

    def atualizar_atividade(self):
        self.ultima_atividade = time.time()

    def esta_expirada(self, timeout_horas=24):
        """Verifica se a sala expirou baseado no tempo de inatividade"""
        # Verifica se a sala está inativa por mais do tempo definido
        tempo_decorrido = time.time() - self.ultima_atividade
        return tempo_decorrido > (timeout_horas * 60 * 60) and not self.usuarios


class GerenciadorSalas:
    def __init__(self, caminho_bd='db.sqlite3'):
        self.caminho_bd = caminho_bd
        self.salas = {}
        self._trava = threading.Lock()
        self.inicializar_bd()
        self.carregar_salas()

    def obter_horario(self):
        """Retorna horário atual formatado"""
        return datetime.now().strftime('%H:%M:%S')

    def inicializar_bd(self):
        """Inicializa estrutura do banco de dados SQLite"""
        try:
            conexao = sqlite3.connect(self.caminho_bd)
            cursor = conexao.cursor()

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS salas (
                id TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                criador TEXT NOT NULL,
                senha TEXT,
                criado_em TEXT NOT NULL,
                esta_ativa INTEGER DEFAULT 1
            )
            ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS mensagens (
                id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
                id_sala TEXT NOT NULL,
                nome_usuario TEXT NOT NULL,
                conteudo TEXT NOT NULL,
                tipo TEXT DEFAULT 'texto',
                nome_arquivo TEXT,
                caminho_arquivo TEXT,
                tipo_arquivo TEXT,
                horario TEXT NOT NULL,
                FOREIGN KEY (id_sala) REFERENCES salas (id)
            )
            ''')

            # Verificar se as colunas existem e adicionar se necessário
            cursor.execute("PRAGMA table_info(mensagens)")
            colunas = [coluna[1] for coluna in cursor.fetchall()]

            colunas_para_adicionar = [
                ('tipo', 'TEXT DEFAULT "texto"'),
                ('nome_arquivo', 'TEXT'),
                ('caminho_arquivo', 'TEXT'),
                ('tipo_arquivo', 'TEXT')
            ]

            for nome_coluna, definicao in colunas_para_adicionar:
                if nome_coluna not in colunas:
                    cursor.execute(
                        f'ALTER TABLE mensagens ADD COLUMN {nome_coluna} {definicao}')

            # Verificar se a coluna id é TEXT (para UUIDs)
            if colunas and any(col for col in cursor.execute("PRAGMA table_info(mensagens)").fetchall() if col[1] == 'id' and col[2] != 'TEXT'):
                # Recriar tabela com id como TEXT se necessário
                print("[DATABASE] Atualizando estrutura da tabela mensagens...")
                cursor.execute('ALTER TABLE mensagens RENAME TO mensagens_old')
                cursor.execute('''
                CREATE TABLE mensagens (
                    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
                    id_sala TEXT NOT NULL,
                    nome_usuario TEXT NOT NULL,
                    conteudo TEXT NOT NULL,
                    tipo TEXT DEFAULT 'texto',
                    nome_arquivo TEXT,
                    caminho_arquivo TEXT,
                    tipo_arquivo TEXT,
                    horario TEXT NOT NULL,
                    FOREIGN KEY (id_sala) REFERENCES salas (id)
                )
                ''')
                cursor.execute('''
                INSERT INTO mensagens (id_sala, nome_usuario, conteudo, tipo, nome_arquivo, caminho_arquivo, tipo_arquivo, horario)
                SELECT id_sala, nome_usuario, conteudo, 
                       COALESCE(tipo, 'texto'),
                       nome_arquivo, caminho_arquivo, tipo_arquivo, horario
                FROM mensagens_old
                ''')
                cursor.execute('DROP TABLE mensagens_old')

            conexao.commit()
            conexao.close()
            print("[DATABASE] Estrutura do banco de dados inicializada com sucesso")

        except Exception as e:
            print(f"[ERROR] Falha ao inicializar banco de dados: {e}")

    def carregar_salas(self):
        """Carrega salas existentes do banco de dados para memória"""
        try:
            conexao = sqlite3.connect(self.caminho_bd)
            conexao.row_factory = sqlite3.Row
            cursor = conexao.cursor()

            cursor.execute('SELECT * FROM salas')
            linhas = cursor.fetchall()

            for linha in linhas:
                sala = Sala(
                    id=linha['id'],
                    nome=linha['nome'],
                    criador=linha['criador'],
                    criado_em=linha['criado_em'],
                    senha=linha['senha'],
                    esta_ativa=bool(linha['esta_ativa'])
                )

                # CORREÇÃO: Carregar mensagens considerando soft delete
                cursor.execute(
                    'SELECT * FROM mensagens WHERE id_sala = ? ORDER BY horario DESC LIMIT 50',
                    (sala.id,))
                mensagens = cursor.fetchall()

                for msg in reversed(mensagens):
                    mensagem_obj = {
                        'id': msg['id'] or str(uuid.uuid4()),
                        'nome_usuario': msg['nome_usuario'],
                        'horario': msg['horario']
                    }

                    # VERIFICAR SE FOI SOFT DELETED
                    if msg['tipo'] == 'deletada':
                        # Mensagem foi soft deleted
                        mensagem_obj['deletada'] = True
                        if 'arquivo' in msg['conteudo'].lower():
                            mensagem_obj['tipo'] = 'arquivo'
                            mensagem_obj['mensagem'] = 'Arquivo deletado'
                            mensagem_obj['nome_arquivo'] = 'Arquivo deletado'
                        else:
                            mensagem_obj['tipo'] = 'texto'
                            mensagem_obj['mensagem'] = 'Mensagem deletada'
                    elif msg['tipo'] == 'arquivo':
                        mensagem_obj.update({
                            'tipo': 'arquivo',
                            'nome_arquivo': msg['nome_arquivo'],
                            'caminho_arquivo': msg['caminho_arquivo'],
                            'tipo_arquivo': msg['tipo_arquivo']
                        })
                    else:
                        mensagem_obj.update({
                            'tipo': 'texto',
                            'mensagem': msg['conteudo']
                        })

                    sala.mensagens.append(mensagem_obj)

                self.salas[sala.id] = sala

            conexao.close()
            print(
                f"[DATABASE] Carregadas {len(self.salas)} salas do banco de dados")

        except Exception as e:
            print(f"[ERROR] Falha ao carregar salas: {e}")
            self.salas = {}

    def criar_sala(self, nome, criador, senha=None):
        """Cria nova sala e persiste no banco de dados"""
        with self._trava:
            try:
                # Gerar ID único
                id_sala = str(uuid.uuid4())[:8]
                while id_sala in self.salas:  # Garantir unicidade
                    id_sala = str(uuid.uuid4())[:8]

                sala = Sala(id_sala, nome, criador, senha=senha)

                conexao = sqlite3.connect(self.caminho_bd)
                cursor = conexao.cursor()

                cursor.execute(
                    'INSERT INTO salas (id, nome, criador, senha, criado_em, esta_ativa) VALUES (?, ?, ?, ?, ?, ?)',
                    (sala.id, sala.nome, sala.criador,
                     sala.senha, sala.criado_em, 1)
                )

                conexao.commit()
                conexao.close()

                self.salas[id_sala] = sala
                print(
                    f"[ROOM] Nova sala criada: ID={id_sala}, Nome='{nome}', Criador='{criador}'")
                return sala

            except Exception as e:
                print(f"[ERROR] Falha ao criar sala: {e}")
                raise

    def obter_sala(self, id_sala):
        return self.salas.get(id_sala)

    def obter_todas_salas(self):
        return list(self.salas.values())

    def excluir_sala(self, id_sala):
        """Remove sala permanentemente do sistema"""
        with self._trava:
            try:
                if id_sala in self.salas:
                    conexao = sqlite3.connect(self.caminho_bd)
                    cursor = conexao.cursor()

                    cursor.execute(
                        'DELETE FROM mensagens WHERE id_sala = ?', (id_sala,))
                    cursor.execute(
                        'DELETE FROM salas WHERE id = ?', (id_sala,))

                    conexao.commit()
                    conexao.close()

                    del self.salas[id_sala]
                    print(f"[ROOM] Sala excluída: ID={id_sala}")
                    return True
                return False

            except Exception as e:
                print(f"[ERROR] Falha ao excluir sala {id_sala}: {e}")
                return False

    def verificar_senha_sala(self, id_sala, senha):
        """Valida senha de acesso à sala"""
        sala = self.obter_sala(id_sala)
        if not sala:
            return False

        if not sala.senha:
            return True

        return sala.senha == senha

    def adicionar_mensagem_na_sala(self, id_sala, nome_usuario, mensagem):
        """Adiciona nova mensagem à sala e persiste no banco"""
        try:
            sala = self.obter_sala(id_sala)
            if not sala:
                return False

            horario = self.obter_horario()
            id_mensagem = str(uuid.uuid4())

            # Criar objeto de mensagem
            mensagem_obj = {
                'id': id_mensagem,
                'nome_usuario': nome_usuario,
                'mensagem': mensagem,
                'tipo': 'texto',
                'horario': horario
            }

            # Salvar no banco de dados
            conexao = sqlite3.connect(self.caminho_bd)
            cursor = conexao.cursor()

            cursor.execute(
                'INSERT INTO mensagens (id, id_sala, nome_usuario, conteudo, tipo, horario) VALUES (?, ?, ?, ?, ?, ?)',
                (id_mensagem, id_sala, nome_usuario, mensagem, 'texto', horario)
            )

            conexao.commit()
            conexao.close()

            # Adicionar à memória
            sala.adicionar_mensagem(mensagem_obj)
            return mensagem_obj

        except Exception as e:
            print(
                f"[ERROR] Falha ao adicionar mensagem na sala {id_sala}: {e}")
            return False

    def adicionar_arquivo_na_sala(self, id_sala, nome_usuario, nome_arquivo, caminho_arquivo, tipo_arquivo):
        """Adiciona novo arquivo à sala e persiste no banco"""
        conexao = None
        try:
            sala = self.obter_sala(id_sala)
            if not sala:
                # Remover arquivo se a sala não existir
                if os.path.exists(caminho_arquivo):
                    os.remove(caminho_arquivo)
                    print(
                        f"[CLEANUP] Arquivo removido - sala não encontrada: {caminho_arquivo}")
                return False

            horario = self.obter_horario()
            id_mensagem = str(uuid.uuid4())

            # Adicionar à memória primeiro
            mensagem_arquivo = {
                'id': id_mensagem,
                'nome_usuario': nome_usuario,
                'tipo': 'arquivo',
                'nome_arquivo': nome_arquivo,
                'caminho_arquivo': caminho_arquivo,
                'tipo_arquivo': tipo_arquivo,
                'horario': horario
            }

            # Tentar salvar no banco de dados
            conexao = sqlite3.connect(self.caminho_bd)
            cursor = conexao.cursor()

            cursor.execute(
                'INSERT INTO mensagens (id, id_sala, nome_usuario, conteudo, tipo, nome_arquivo, caminho_arquivo, tipo_arquivo, horario) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',

                (id_mensagem, id_sala, nome_usuario, f"Compartilhou o arquivo: {nome_arquivo}",
                 'arquivo', nome_arquivo, caminho_arquivo, tipo_arquivo, horario)
            )

            conexao.commit()

            # Só adicionar à memória se salvou no banco com sucesso
            sala.adicionar_mensagem(mensagem_arquivo)
            print(
                f"[FILE] Arquivo registrado com sucesso: {nome_arquivo} na sala {id_sala}")
            return mensagem_arquivo

        except sqlite3.Error as db_error:
            print(
                f"[ERROR] Erro de banco de dados ao adicionar arquivo na sala {id_sala}: {db_error}")
            self._cleanup_arquivo_erro(caminho_arquivo)
            return False
        except Exception as e:
            print(f"[ERROR] Falha ao adicionar arquivo na sala {id_sala}: {e}")
            self._cleanup_arquivo_erro(caminho_arquivo)
            return False
        finally:
            if conexao:
                conexao.close()

    def _cleanup_arquivo_erro(self, caminho_arquivo):
        """Remove arquivo em caso de erro durante o processamento"""
        if caminho_arquivo and os.path.exists(caminho_arquivo):
            try:
                os.remove(caminho_arquivo)
                print(
                    f"[CLEANUP] Arquivo removido após erro: {caminho_arquivo}")

                # Tentar remover pasta se estiver vazia
                pasta_pai = os.path.dirname(caminho_arquivo)
                if os.path.exists(pasta_pai):
                    try:
                        os.rmdir(pasta_pai)
                        print(f"[CLEANUP] Pasta vazia removida: {pasta_pai}")
                    except OSError:
                        pass  # Pasta não estava vazia

            except Exception as cleanup_error:
                print(f"[ERROR] Falha ao limpar arquivo: {cleanup_error}")

    def remover_mensagem_da_sala(self, id_sala, id_mensagem, nome_usuario):
        """Marca mensagem como deletada na sala e no banco de dados"""
        try:
            sala = self.obter_sala(id_sala)
            if not sala:
                return False

            # Verificar se a mensagem existe e pertence ao usuário
            mensagem_para_deletar = None
            for mensagem in sala.mensagens:
                if mensagem.get('id') == id_mensagem:
                    if mensagem.get('nome_usuario') == nome_usuario:
                        # Verificar se já foi deletada
                        if mensagem.get('deletada'):
                            return False  # Já foi deletada
                        mensagem_para_deletar = mensagem
                        break
                    else:
                        return False  # Não é o autor

            if not mensagem_para_deletar:
                return False  # Mensagem não encontrada

            # Atualizar no banco de dados primeiro
            conexao = sqlite3.connect(self.caminho_bd)
            cursor = conexao.cursor()

            if mensagem_para_deletar.get('tipo') == 'arquivo':
                novo_conteudo = 'Arquivo deletado'
                # Remover arquivo físico se existir
                caminho_arquivo = mensagem_para_deletar.get('caminho_arquivo')
                if caminho_arquivo and os.path.exists(caminho_arquivo):
                    try:
                        os.remove(caminho_arquivo)
                        print(
                            f"[DELETE] Arquivo físico removido: {caminho_arquivo}")
                    except Exception as e:
                        print(f"[ERROR] Falha ao remover arquivo físico: {e}")
            else:
                novo_conteudo = 'Mensagem deletada'

            # MARCAR COMO DELETADA NO BANCO
            cursor.execute(
                'UPDATE mensagens SET conteudo = ?, tipo = ? WHERE id = ?',
                (novo_conteudo, 'deletada', id_mensagem)
            )
            conexao.commit()
            conexao.close()

            # ATUALIZAR NA MEMÓRIA COM SOFT DELETE
            mensagem_para_deletar['deletada'] = True
            mensagem_para_deletar['conteudo_original'] = mensagem_para_deletar.get(
                'mensagem', mensagem_para_deletar.get('nome_arquivo', ''))

            if mensagem_para_deletar.get('tipo') == 'arquivo':
                mensagem_para_deletar['mensagem'] = 'Arquivo deletado'
                mensagem_para_deletar['nome_arquivo'] = 'Arquivo deletado'
                # Limpar dados do arquivo
                mensagem_para_deletar['caminho_arquivo'] = None
                mensagem_para_deletar['tipo_arquivo'] = None
            else:
                mensagem_para_deletar['mensagem'] = 'Mensagem deletada'

            print(
                f"[SOFT DELETE] Mensagem {id_mensagem} marcada como deletada na sala {id_sala}")
            return True

        except Exception as e:
            print(f"[ERROR] Falha ao deletar mensagem {id_mensagem}: {e}")
            return False

    def limpar_salas_expiradas(self, timeout_horas=24):
        """Marca salas inativas como expiradas"""
        try:
            ids_expirados = []

            for id_sala, sala in list(self.salas.items()):
                if sala.esta_expirada(timeout_horas):
                    ids_expirados.append(id_sala)

            for id_sala in ids_expirados:
                # Não exclui do banco, apenas marca como inativo
                conexao = sqlite3.connect(self.caminho_bd)
                cursor = conexao.cursor()
                cursor.execute(
                    'UPDATE salas SET esta_ativa = 0 WHERE id = ?', (id_sala,))
                conexao.commit()
                conexao.close()

                # Atualiza o objeto em memória
                self.salas[id_sala].esta_ativa = False

            return len(ids_expirados)

        except Exception as e:
            print(f"[ERROR] Falha ao limpar salas expiradas: {e}")
            return 0

    def obter_estatisticas(self):
        """Retorna estatísticas do sistema para dashboard administrativo"""
        try:
            salas_ativas = sum(
                1 for sala in self.salas.values() if sala.esta_ativa)
            usuarios_online = sum(len(sala.usuarios)
                                  for sala in self.salas.values())

            return {
                'total_salas': len(self.salas),
                'salas_ativas': salas_ativas,
                'usuarios_online': usuarios_online,
                'atividade_recente': self._obter_atividade_recente()
            }

        except Exception as e:
            print(f"[ERROR] Falha ao obter estatísticas: {e}")
            return {
                'total_salas': 0,
                'salas_ativas': 0,
                'usuarios_online': 0,
                'atividade_recente': []
            }

    def _obter_atividade_recente(self):
        """Recupera atividade recente do sistema para logs administrativos"""
        try:
            recente = []

            conexao = sqlite3.connect(self.caminho_bd)
            conexao.row_factory = sqlite3.Row
            cursor = conexao.cursor()

            cursor.execute('''
                SELECT salas.nome, mensagens.nome_usuario, mensagens.horario
                FROM mensagens JOIN salas ON mensagens.id_sala = salas.id
                ORDER BY mensagens.horario DESC LIMIT 10
            ''')

            atividades = cursor.fetchall()

            for atividade in atividades:
                recente.append({
                    'horario': atividade['horario'],
                    'texto': f"{atividade['nome_usuario']} enviou uma mensagem na sala {atividade['nome']}"
                })

            conexao.close()
            return recente

        except Exception as e:
            print(f"[ERROR] Falha ao obter atividade recente: {e}")
            return []


# Instância global do gerenciador de salas
gerenciador_salas = GerenciadorSalas()
