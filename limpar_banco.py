import sqlite3
import os
import shutil
from datetime import datetime


def limpar_banco_completamente():
    """Remove completamente o banco de dados e cria um novo"""
    caminho_bd = 'db.sqlite3'
    pasta_uploads = 'uploads'

    print("LIMPEZA COMPLETA DO BANCO DE DADOS E ARQUIVOS")
    print("="*60)
    print("ATENÇÃO: Esta operação REMOVE TODOS OS DADOS E ARQUIVOS!")

    if os.path.exists(caminho_bd):
        print(f"Banco atual encontrado: {caminho_bd}")
        print(f"Tamanho: {os.path.getsize(caminho_bd)} bytes")

        resposta = input(
            f"\nTem certeza que deseja EXCLUIR COMPLETAMENTE o banco '{caminho_bd}' e TODOS os arquivos? (digite 'CONFIRMAR'): ")
        if resposta != 'CONFIRMAR':
            print("Operação cancelada.")
            return

        # Fazer backup antes de excluir (opcional)
        backup = input("Deseja fazer backup antes de excluir? (s/n): ")
        if backup.lower() == 's':
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nome_backup_bd = f"backup_db_{timestamp}.sqlite3"
            nome_backup_uploads = f"backup_uploads_{timestamp}"

            # Backup do banco
            os.rename(caminho_bd, nome_backup_bd)
            print(f"Backup do banco criado: {nome_backup_bd}")

            # Backup dos uploads se existir
            if os.path.exists(pasta_uploads):
                shutil.copytree(pasta_uploads, nome_backup_uploads)
                print(f"Backup dos arquivos criado: {nome_backup_uploads}")
        else:
            os.remove(caminho_bd)
            print("Banco de dados removido.")
    else:
        print("Nenhum banco de dados encontrado.")

    # Limpar pasta de uploads
    if os.path.exists(pasta_uploads):
        try:
            shutil.rmtree(pasta_uploads)
            print("Pasta de uploads removida.")
        except Exception as e:
            print(f"Erro ao remover pasta de uploads: {e}")

    # Criar novo banco com estrutura correta
    print("Criando novo banco de dados...")
    conexao = sqlite3.connect(caminho_bd)
    cursor = conexao.cursor()

    # Criar tabelas com nomes em português e suporte a arquivos
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

    conexao.commit()
    conexao.close()

    # Recriar pasta de uploads
    os.makedirs(pasta_uploads, exist_ok=True)
    print("Pasta de uploads recriada.")

    print("Novo banco de dados criado com estrutura para arquivos!")
    print("Suporte a: PDF, JPG, JPEG, PNG (máximo 16MB)")
    print("Agora você pode executar a aplicação normalmente.")


def limpar_apenas_dados():
    """Limpa apenas os dados mas mantém a estrutura"""
    caminho_bd = 'db.sqlite3'
    pasta_uploads = 'uploads'

    if not os.path.exists(caminho_bd):
        print("Banco de dados não encontrado!")
        return

    print("LIMPEZA DE DADOS E ARQUIVOS")
    print("="*40)

    resposta = input(
        "Deseja limpar apenas os DADOS e ARQUIVOS (manter estrutura)? (s/n): ")
    if resposta.lower() != 's':
        print("Operação cancelada.")
        return

    try:
        conexao = sqlite3.connect(caminho_bd)
        cursor = conexao.cursor()

        # Contar registros antes
        cursor.execute("SELECT COUNT(*) FROM mensagens")
        msgs_antes = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM salas")
        salas_antes = cursor.fetchone()[0]

        # Contar arquivos antes
        arquivos_antes = 0
        if os.path.exists(pasta_uploads):
            for _, _, files in os.walk(pasta_uploads):
                arquivos_antes += len(files)

        # Limpar dados
        cursor.execute("DELETE FROM mensagens")
        cursor.execute("DELETE FROM salas")

        conexao.commit()
        conexao.close()

        # Limpar arquivos
        if os.path.exists(pasta_uploads):
            shutil.rmtree(pasta_uploads)
            os.makedirs(pasta_uploads, exist_ok=True)

        print(f"Limpeza concluída!")
        print(f"Salas removidas: {salas_antes}")
        print(f"Mensagens removidas: {msgs_antes}")
        print(f"Arquivos removidos: {arquivos_antes}")

    except Exception as e:
        print(f"Erro durante limpeza: {e}")


def limpar_arquivos_orfaos():
    """Remove arquivos que não têm referência no banco de dados"""
    caminho_bd = 'db.sqlite3'
    pasta_uploads = 'uploads'

    if not os.path.exists(caminho_bd):
        print("Banco de dados não encontrado!")
        return

    if not os.path.exists(pasta_uploads):
        print("Pasta de uploads não encontrada.")
        return

    print("LIMPEZA DE ARQUIVOS ÓRFÃOS")
    print("="*40)

    try:
        # Obter todos os caminhos de arquivos do banco
        conexao = sqlite3.connect(caminho_bd)
        cursor = conexao.cursor()

        cursor.execute(
            "SELECT caminho_arquivo FROM mensagens WHERE tipo = 'arquivo' AND caminho_arquivo IS NOT NULL")
        arquivos_bd = set(row[0] for row in cursor.fetchall() if row[0])
        conexao.close()

        # Obter todos os arquivos físicos
        arquivos_fisicos = set()
        for root, dirs, files in os.walk(pasta_uploads):
            for file in files:
                caminho_completo = os.path.join(root, file)
                arquivos_fisicos.add(caminho_completo)

        # Encontrar órfãos
        arquivos_orfaos = arquivos_fisicos - arquivos_bd

        if not arquivos_orfaos:
            print("Nenhum arquivo órfão encontrado.")
            return

        print(f"Encontrados {len(arquivos_orfaos)} arquivos órfãos:")
        for arquivo in list(arquivos_orfaos)[:10]:  # Mostrar até 10
            print(f"   - {arquivo}")

        if len(arquivos_orfaos) > 10:
            print(f"   ... e mais {len(arquivos_orfaos) - 10} arquivos")

        confirmar = input(
            f"\nDeseja remover {len(arquivos_orfaos)} arquivos órfãos? (s/n): ")
        if confirmar.lower() != 's':
            print("Operação cancelada.")
            return

        # Remover arquivos órfãos
        removidos = 0
        for arquivo in arquivos_orfaos:
            try:
                if os.path.exists(arquivo):
                    os.remove(arquivo)
                    removidos += 1
            except Exception as e:
                print(f"Erro ao remover {arquivo}: {e}")

        # Remover pastas vazias
        for root, dirs, files in os.walk(pasta_uploads, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    if not os.listdir(dir_path):  # Se a pasta estiver vazia
                        os.rmdir(dir_path)
                except Exception:
                    pass

        print(f"{removidos} arquivos órfãos removidos!")

    except Exception as e:
        print(f"Erro durante limpeza de órfãos: {e}")


def verificar_integridade():
    """Verifica a integridade dos arquivos referenciados no banco"""
    caminho_bd = 'db.sqlite3'

    if not os.path.exists(caminho_bd):
        print("Banco de dados não encontrado!")
        return

    print("VERIFICAÇÃO DE INTEGRIDADE")
    print("="*40)

    try:
        conexao = sqlite3.connect(caminho_bd)
        cursor = conexao.cursor()

        cursor.execute("""
            SELECT id, id_sala, nome_arquivo, caminho_arquivo 
            FROM mensagens 
            WHERE tipo = 'arquivo' AND caminho_arquivo IS NOT NULL
        """)

        registros = cursor.fetchall()
        conexao.close()

        if not registros:
            print("Nenhum arquivo encontrado no banco de dados.")
            return

        print(f"Verificando {len(registros)} arquivos...")

        arquivos_corrompidos = []
        arquivos_ausentes = []

        for id_msg, id_sala, nome_arquivo, caminho_arquivo in registros:
            if not os.path.exists(caminho_arquivo):
                arquivos_ausentes.append(
                    (id_msg, id_sala, nome_arquivo, caminho_arquivo))
            elif os.path.getsize(caminho_arquivo) == 0:
                arquivos_corrompidos.append(
                    (id_msg, id_sala, nome_arquivo, caminho_arquivo))

        # Relatório
        print(
            f"Arquivos íntegros: {len(registros) - len(arquivos_ausentes) - len(arquivos_corrompidos)}")

        if arquivos_ausentes:
            print(f"Arquivos ausentes: {len(arquivos_ausentes)}")
            for item in arquivos_ausentes[:5]:
                print(f"   - {item[2]} (Sala: {item[1]})")
            if len(arquivos_ausentes) > 5:
                print(f"   ... e mais {len(arquivos_ausentes) - 5}")

        if arquivos_corrompidos:
            print(f"Arquivos corrompidos: {len(arquivos_corrompidos)}")
            for item in arquivos_corrompidos[:5]:
                print(f"   - {item[2]} (Sala: {item[1]})")
            if len(arquivos_corrompidos) > 5:
                print(f"   ... e mais {len(arquivos_corrompidos) - 5}")

        if arquivos_ausentes or arquivos_corrompidos:
            limpar = input(
                "\nDeseja remover referências de arquivos com problemas? (s/n): ")
            if limpar.lower() == 's':
                conexao = sqlite3.connect(caminho_bd)
                cursor = conexao.cursor()

                ids_para_remover = [item[0]
                                    for item in arquivos_ausentes + arquivos_corrompidos]
                for id_msg in ids_para_remover:
                    cursor.execute(
                        "DELETE FROM mensagens WHERE id = ?", (id_msg,))

                conexao.commit()
                conexao.close()

                print(f"{len(ids_para_remover)} referências removidas do banco!")

    except Exception as e:
        print(f"Erro durante verificação: {e}")


def mostrar_menu():
    print("GERENCIADOR DE BANCO DE DADOS E ARQUIVOS")
    print("="*50)
    print("1. Limpar banco completamente (remove arquivo e uploads)")
    print("2. Limpar apenas dados (manter estrutura)")
    print("3. Limpar arquivos órfãos")
    print("4. Verificar integridade dos arquivos")
    print("5. Cancelar")
    print()

    opcao = input("Escolha uma opção (1-5): ")

    if opcao == '1':
        limpar_banco_completamente()
    elif opcao == '2':
        limpar_apenas_dados()
    elif opcao == '3':
        limpar_arquivos_orfaos()
    elif opcao == '4':
        verificar_integridade()
    elif opcao == '5':
        print("Operação cancelada.")
    else:
        print("Opção inválida!")


if __name__ == "__main__":
    mostrar_menu()
