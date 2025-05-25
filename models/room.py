import uuid
import time
from datetime import datetime, timedelta
import sqlite3
import os
import json
import threading


class Room:
    def __init__(self, id, name, creator, created_at=None, password=None, is_active=True):
        self.id = id
        self.name = name
        self.creator = creator
        self.password = password
        self.is_active = is_active
        self.created_at = created_at or datetime.now().isoformat()
        self.messages = []
        self.users = set()
        self.last_activity = time.time()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'creator': self.creator,
            'created_at': self.created_at,
            'has_password': bool(self.password),
            'is_active': self.is_active,
            'user_count': len(self.users),
            'message_count': len(self.messages)
        }

    def add_user(self, username):
        self.users.add(username)
        self.update_activity()

    def remove_user(self, username):
        if username in self.users:
            self.users.remove(username)
        self.update_activity()

    def add_message(self, message):
        self.messages.append(message)
        self.update_activity()
        if len(self.messages) > 100:  # Limitar a 100 mensagens mais recentes
            self.messages = self.messages[-100:]

    def update_activity(self):
        self.last_activity = time.time()

    def is_expired(self, timeout_hours=24):
        # Verifica se a sala está inativa por mais do tempo definido
        elapsed = time.time() - self.last_activity
        return elapsed > (timeout_hours * 60 * 60) and not self.users


class RoomManager:
    def __init__(self, db_path='db.sqlite3'):
        self.db_path = db_path
        self.rooms = {}
        self._lock = threading.Lock()
        self.init_db()
        self.load_rooms()

    def init_db(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Criar tabela de salas se não existir
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS rooms (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                creator TEXT NOT NULL,
                password TEXT,
                created_at TEXT NOT NULL,
                is_active INTEGER DEFAULT 1
            )
            ''')

            # Criar tabela de mensagens se não existir
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_id TEXT NOT NULL,
                username TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (room_id) REFERENCES rooms (id)
            )
            ''')

            conn.commit()
            conn.close()
            print("Database initialized successfully")

        except Exception as e:
            print(f"Erro ao inicializar banco de dados: {e}")

    def load_rooms(self):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM rooms')
            rows = cursor.fetchall()

            for row in rows:
                room = Room(
                    id=row['id'],
                    name=row['name'],
                    creator=row['creator'],
                    created_at=row['created_at'],
                    password=row['password'],
                    is_active=bool(row['is_active'])
                )

                # Carregar mensagens para a sala
                cursor.execute(
                    'SELECT * FROM messages WHERE room_id = ? ORDER BY timestamp DESC LIMIT 50', (room.id,))
                messages = cursor.fetchall()

                # Reverter para manter ordem cronológica
                for msg in reversed(messages):
                    room.messages.append({
                        'username': msg['username'],
                        'message': msg['content'],
                        'timestamp': msg['timestamp']
                    })

                self.rooms[room.id] = room

            conn.close()
            print(f"Loaded {len(self.rooms)} rooms from database")

        except Exception as e:
            print(f"Erro ao carregar salas: {e}")
            self.rooms = {}

    def create_room(self, name, creator, password=None):
        with self._lock:
            try:
                # Gerar ID único
                room_id = str(uuid.uuid4())[:8]
                while room_id in self.rooms:  # Garantir unicidade
                    room_id = str(uuid.uuid4())[:8]

                room = Room(room_id, name, creator, password=password)

                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute(
                    'INSERT INTO rooms (id, name, creator, password, created_at, is_active) VALUES (?, ?, ?, ?, ?, ?)',
                    (room.id, room.name, room.creator,
                     room.password, room.created_at, 1)
                )

                conn.commit()
                conn.close()

                self.rooms[room_id] = room
                print(f"Room created: {room_id} - {name}")
                return room

            except Exception as e:
                print(f"Erro ao criar sala: {e}")
                raise

    def get_room(self, room_id):
        return self.rooms.get(room_id)

    def get_all_rooms(self):
        return list(self.rooms.values())

    def delete_room(self, room_id):
        with self._lock:
            try:
                if room_id in self.rooms:
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()

                    cursor.execute(
                        'DELETE FROM messages WHERE room_id = ?', (room_id,))
                    cursor.execute(
                        'DELETE FROM rooms WHERE id = ?', (room_id,))

                    conn.commit()
                    conn.close()

                    del self.rooms[room_id]
                    print(f"Room deleted: {room_id}")
                    return True
                return False

            except Exception as e:
                print(f"Erro ao deletar sala: {e}")
                return False

    def verify_room_password(self, room_id, password):
        room = self.get_room(room_id)
        if not room:
            return False

        if not room.password:
            return True

        return room.password == password

    def add_message_to_room(self, room_id, username, message):
        try:
            room = self.get_room(room_id)
            if not room:
                return False

            timestamp = self.get_timestamp()

            # Adicionar à memória
            room.add_message({
                'username': username,
                'message': message,
                'timestamp': timestamp
            })

            # Salvar no banco de dados
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                'INSERT INTO messages (room_id, username, content, timestamp) VALUES (?, ?, ?, ?)',
                (room_id, username, message, timestamp)
            )

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"Erro ao adicionar mensagem: {e}")
            return False

    def get_timestamp(self):
        return datetime.now().strftime('%H:%M:%S')

    def cleanup_expired_rooms(self, timeout_hours=24):
        """Remove salas inativas que expiraram"""
        try:
            expired_ids = []

            for room_id, room in list(self.rooms.items()):
                if room.is_expired(timeout_hours):
                    expired_ids.append(room_id)

            for room_id in expired_ids:
                # Não exclui do banco, apenas marca como inativo
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute(
                    'UPDATE rooms SET is_active = 0 WHERE id = ?', (room_id,))
                conn.commit()
                conn.close()

                # Atualiza o objeto em memória
                self.rooms[room_id].is_active = False

            return len(expired_ids)

        except Exception as e:
            print(f"Erro ao limpar salas expiradas: {e}")
            return 0

    def get_stats(self):
        """Retorna estatísticas para o painel de admin"""
        try:
            active_rooms = sum(
                1 for room in self.rooms.values() if room.is_active)
            online_users = sum(len(room.users) for room in self.rooms.values())

            return {
                'total_rooms': len(self.rooms),
                'active_rooms': active_rooms,
                'online_users': online_users,
                'recent_activity': self._get_recent_activity()
            }

        except Exception as e:
            print(f"Erro ao obter estatísticas: {e}")
            return {
                'total_rooms': 0,
                'active_rooms': 0,
                'online_users': 0,
                'recent_activity': []
            }

    def _get_recent_activity(self):
        """Obtém atividade recente de todas as salas"""
        try:
            recent = []

            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('''
                SELECT rooms.name, messages.username, messages.timestamp 
                FROM messages JOIN rooms ON messages.room_id = rooms.id 
                ORDER BY messages.timestamp DESC LIMIT 10
            ''')

            activities = cursor.fetchall()

            for activity in activities:
                recent.append({
                    'time': activity['timestamp'],
                    'text': f"{activity['username']} enviou uma mensagem na sala {activity['name']}"
                })

            conn.close()
            return recent

        except Exception as e:
            print(f"Erro ao obter atividade recente: {e}")
            return []


# Instância global do gerenciador de salas
room_manager = RoomManager()
