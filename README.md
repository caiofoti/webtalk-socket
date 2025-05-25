# WebTalk Socket

Este projeto foi desenvolvido como parte da disciplina de Fundamentos de Redes de Computadores e Sistemas Distribuídos, com o objetivo de implementar um sistema de comunicação em tempo real utilizando WebSockets para troca de mensagens entre usuários.

## Sobre o Projeto

O WebTalk Socket é uma aplicação web que demonstra os conceitos fundamentais de comunicação em rede através da implementação de um chat em tempo real. O projeto utiliza a tecnologia WebSocket para estabelecer conexões bidirecionais entre cliente e servidor, permitindo que múltiplos usuários se comuniquem instantaneamente através de salas de chat.

A aplicação foi construída com Flask e Socket.IO, oferecendo uma interface web intuitiva onde os usuários podem criar salas, participar de conversas e trocar mensagens em tempo real. O sistema inclui funcionalidades de administração para gerenciamento de salas e usuários, demonstrando conceitos importantes de sistemas distribuídos como gerenciamento de estado, sincronização entre clientes e comunicação assíncrona.

## Estrutura do Projeto

O projeto está organizado seguindo o padrão MVC (Model-View-Controller) para Flask:

- **[app.py](app.py)**: Arquivo principal da aplicação Flask
- **[config.py](config.py)**: Configurações da aplicação
- **[models/](models/)**: Modelos de dados (salas de chat)
- **[routes/](routes/)**: Rotas HTTP da aplicação
- **[socketio_handlers/](socketio_handlers/)**: Manipuladores de eventos WebSocket
- **[templates/](templates/)**: Templates HTML da interface
- **[static/](static/)**: Arquivos estáticos (CSS, JavaScript, imagens)
- **[db.sqlite3](db.sqlite3)**: Banco de dados SQLite

## Funcionalidades

- Criação e gerenciamento de salas de chat
- Comunicação em tempo real via WebSockets
- Interface web responsiva
- Sistema de administração
- Persistência de dados em SQLite
- Suporte a múltiplos usuários simultâneos

## Tecnologias Utilizadas

- **Flask**: Framework web Python
- **Socket.IO**: Biblioteca para comunicação WebSocket
- **SQLite**: Banco de dados para persistência
- **HTML/CSS/JavaScript**: Frontend da aplicação

## Instalação e Execução

1. Clone o repositório
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Execute a aplicação:
   ```bash
   python app.py
   ```

## Objetivos Acadêmicos

Este projeto demonstra conceitos fundamentais estudados na disciplina:
- Protocolos de comunicação em rede
- Arquitetura cliente-servidor
- Comunicação assíncrona
- Gerenciamento de conexões simultâneas
- Sincronização de dados em sistemas distribuídos

## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Autor

Desenvolvido por Caio Foti Pontes como projeto acadêmico para a disciplina de Fundamentos de Redes de Computadores e Sistemas Distribuídos.