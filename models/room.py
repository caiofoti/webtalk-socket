import uuid
import time
from datetime import datetime, timedelta
import sqlite3
import os
import json
import threading


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
        self.usuarios.add(nome_usuario)
        self.atualizar_atividade()

    def remover_usuario(self, nome_usuario):
        if nome_usuario in self.usuarios:
            self.usuarios.remove(nome_usuario)
        self.atualizar_atividade()

    def adicionar_mensagem(self, mensagem):
        self.mensagens.append(mensagem)
        self.atualizar_atividade()
        if len(self.mensagens) > 100:  # Limitar a 100 mensagens mais recentes
            self.mensagens = self.mensagens[-100:]

    def atualizar_atividade(self):
        self.ultima_atividade = time.time()

    def esta_expirada(self, timeout_horas=24):
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

    def inicializar_bd(self):
        try:
            conexao = sqlite3.connect(self.caminho_bd)
            cursor = conexao.cursor()

            # Criar tabela de salas se não existir (versão nova com nomes em português)
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

            # Criar tabela de mensagens se não existir (versão nova com nomes em português)
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS mensagens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_sala TEXT NOT NULL,
                nome_usuario TEXT NOT NULL,
                conteudo TEXT NOT NULL,
                horario TEXT NOT NULL,
                FOREIGN KEY (id_sala) REFERENCES salas (id)
            )
            ''')

            conexao.commit()
            conexao.close()
            print("Banco de dados inicializado com sucesso")

        except Exception as e:
            print(f"Erro ao inicializar banco de dados: {e}")

    def carregar_salas(self):
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

                cursor.execute(
                    'SELECT * FROM mensagens WHERE id_sala = ? ORDER BY horario DESC LIMIT 50',
                    (sala.id,))
                mensagens = cursor.fetchall()

                for msg in reversed(mensagens):
                    sala.mensagens.append({
                        'nome_usuario': msg['nome_usuario'],
                        'mensagem': msg['conteudo'],
                        'horario': msg['horario']
                    })

                self.salas[sala.id] = sala

            conexao.close()
            print(f"Carregadas {len(self.salas)} salas do banco de dados")

        except Exception as e:
            print(f"Erro ao carregar salas: {e}")
            self.salas = {}

    def criar_sala(self, nome, criador, senha=None):
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
                print(f"Sala criada: {id_sala} - {nome}")
                return sala

            except Exception as e:
                print(f"Erro ao criar sala: {e}")
                raise

    def obter_sala(self, id_sala):
        return self.salas.get(id_sala)

    def obter_todas_salas(self):
        return list(self.salas.values())

    def excluir_sala(self, id_sala):
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
                    print(f"Sala excluída: {id_sala}")
                    return True
                return False

            except Exception as e:
                print(f"Erro ao excluir sala: {e}")
                return False

    def verificar_senha_sala(self, id_sala, senha):
        sala = self.obter_sala(id_sala)
        if not sala:
            return False

        if not sala.senha:
            return True

        return sala.senha == senha

    def adicionar_mensagem_na_sala(self, id_sala, nome_usuario, mensagem):
        try:
            sala = self.obter_sala(id_sala)
            if not sala:
                return False

            horario = self.obter_horario()

            # Adicionar à memória
            sala.adicionar_mensagem({
                'nome_usuario': nome_usuario,
                'mensagem': mensagem,
                'horario': horario
            })

            # Salvar no banco de dados
            conexao = sqlite3.connect(self.caminho_bd)
            cursor = conexao.cursor()

            cursor.execute(
                'INSERT INTO mensagens (id_sala, nome_usuario, conteudo, horario) VALUES (?, ?, ?, ?)',
                (id_sala, nome_usuario, mensagem, horario)
            )

            conexao.commit()
            conexao.close()
            return True

        except Exception as e:
            print(f"Erro ao adicionar mensagem: {e}")
            return False

    def obter_horario(self):
        return datetime.now().strftime('%H:%M:%S')

    def limpar_salas_expiradas(self, timeout_horas=24):
        """Remove salas inativas que expiraram"""
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
            print(f"Erro ao limpar salas expiradas: {e}")
            return 0

    def obter_estatisticas(self):
        """Retorna estatísticas para o painel de admin"""
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
            print(f"Erro ao obter estatísticas: {e}")
            return {
                'total_salas': 0,
                'salas_ativas': 0,
                'usuarios_online': 0,
                'atividade_recente': []
            }

    def _obter_atividade_recente(self):
        """Obtém atividade recente de todas as salas"""
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
            print(f"Erro ao obter atividade recente: {e}")
            return []


# Instância global do gerenciador de salas
gerenciador_salas = GerenciadorSalas()
