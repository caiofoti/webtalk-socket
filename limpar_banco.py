import sqlite3
import os
from datetime import datetime


def limpar_banco_completamente():
    """Remove completamente o banco de dados e cria um novo"""
    caminho_bd = 'db.sqlite3'

    print("🗑️  LIMPEZA COMPLETA DO BANCO DE DADOS")
    print("=" * 50)
    print("⚠️  ATENÇÃO: Esta operação REMOVE TODOS OS DADOS!")

    if os.path.exists(caminho_bd):
        print(f"📁 Banco atual encontrado: {caminho_bd}")
        print(f"📏 Tamanho: {os.path.getsize(caminho_bd)} bytes")

        resposta = input(
            f"\n❓ Tem certeza que deseja EXCLUIR COMPLETAMENTE o banco '{caminho_bd}'? (digite 'CONFIRMAR'): ")
        if resposta != 'CONFIRMAR':
            print("❌ Operação cancelada.")
            return

        # Fazer backup antes de excluir (opcional)
        backup = input("💾 Deseja fazer backup antes de excluir? (s/n): ")
        if backup.lower() == 's':
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nome_backup = f"backup_db_{timestamp}.sqlite3"
            os.rename(caminho_bd, nome_backup)
            print(f"✅ Backup criado: {nome_backup}")
        else:
            os.remove(caminho_bd)
            print("✅ Banco de dados removido.")
    else:
        print("ℹ️  Nenhum banco de dados encontrado.")

    # Criar novo banco com estrutura correta
    print("🔧 Criando novo banco de dados...")
    conexao = sqlite3.connect(caminho_bd)
    cursor = conexao.cursor()

    # Criar tabelas com nomes em português
    cursor.execute('''
    CREATE TABLE salas (
        id TEXT PRIMARY KEY,
        nome TEXT NOT NULL,
        criador TEXT NOT NULL,
        senha TEXT,
        criado_em TEXT NOT NULL,
        esta_ativa INTEGER DEFAULT 1
    )
    ''')

    cursor.execute('''
    CREATE TABLE mensagens (
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

    print("✅ Novo banco de dados criado com estrutura limpa!")
    print("🚀 Agora você pode executar a aplicação normalmente.")


def limpar_apenas_dados():
    """Limpa apenas os dados mas mantém a estrutura"""
    caminho_bd = 'db.sqlite3'

    if not os.path.exists(caminho_bd):
        print("❌ Banco de dados não encontrado!")
        return

    print("🧹 LIMPEZA DE DADOS")
    print("=" * 30)

    resposta = input(
        "❓ Deseja limpar apenas os DADOS (manter estrutura)? (s/n): ")
    if resposta.lower() != 's':
        print("❌ Operação cancelada.")
        return

    try:
        conexao = sqlite3.connect(caminho_bd)
        cursor = conexao.cursor()

        # Contar registros antes
        cursor.execute("SELECT COUNT(*) FROM mensagens")
        msgs_antes = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM salas")
        salas_antes = cursor.fetchone()[0]

        # Limpar dados
        cursor.execute("DELETE FROM mensagens")
        cursor.execute("DELETE FROM salas")

        conexao.commit()
        conexao.close()

        print(f"✅ Limpeza concluída!")
        print(f"📊 Salas removidas: {salas_antes}")
        print(f"📊 Mensagens removidas: {msgs_antes}")

    except Exception as e:
        print(f"❌ Erro durante limpeza: {e}")


def mostrar_menu():
    print("🔧 GERENCIADOR DE BANCO DE DADOS")
    print("=" * 40)
    print("1. Limpar banco completamente (remove arquivo)")
    print("2. Limpar apenas dados (manter estrutura)")
    print("3. Cancelar")
    print()

    opcao = input("Escolha uma opção (1-3): ")

    if opcao == '1':
        limpar_banco_completamente()
    elif opcao == '2':
        limpar_apenas_dados()
    elif opcao == '3':
        print("❌ Operação cancelada.")
    else:
        print("❌ Opção inválida!")


if __name__ == "__main__":
    mostrar_menu()
