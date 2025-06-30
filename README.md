# WebTalk Socket - Sistema de Comunicação Distribuída

Sistema de comunicação em tempo real baseado em WebSockets desenvolvido para a disciplina de Fundamentos de Redes e Sistemas Distribuídos do curso de Informática Biomédica da UFCSPA.

## Visão Geral

Aplicação web que implementa chat em tempo real, compartilhamento de arquivos e gerenciamento administrativo, demonstrando conceitos fundamentais de arquitetura cliente-servidor distribuída, comunicação bidirecional em tempo real via WebSocket, APIs RESTful, persistência de dados e gerenciamento de estado distribuído.

## Funcionalidades

### Sistema de Salas
- Criação dinâmica de salas públicas e protegidas por senha
- Sistema de IDs únicos de 8 caracteres
- Controle de acesso baseado em autenticação por sala
- Gerenciamento automático de usuários online
- Persistência de histórico de mensagens

### Chat em Tempo Real
- Comunicação instantânea via WebSocket
- Mensagens de texto com limite de 500 caracteres
- Sistema de soft delete para mensagens próprias
- Notificações de entrada/saída de usuários
- Histórico das últimas 50 mensagens por sala
- Contador de caracteres em tempo real

### Compartilhamento de Arquivos
- Upload seguro de arquivos (PDF, JPG, JPEG, PNG)
- Limite de 16MB por arquivo
- Validação de tipo MIME e assinatura binária
- Preview inline para imagens com suporte a transparência
- Modal expandido para visualização de imagens
- Download direto de arquivos
- Soft delete para arquivos compartilhados
- Progress bar durante upload

### Segurança e Validação
- Validação rigorosa de entrada e sanitização de HTML
- Verificação de conteúdo vs. extensão de arquivo
- Controle de acesso baseado em proprietário de mensagem
- Cleanup automático de arquivos órfãos
- Prevenção de upload de arquivos maliciosos
- Validação de caracteres especiais em nomes de arquivo

### Painel Administrativo
- Dashboard com estatísticas em tempo real
- Monitoramento de salas ativas e usuários online
- Gerenciamento completo de salas
- Visualização de atividade recente
- Controle de configurações do sistema
- Exclusão administrativa de salas

### Interface Responsiva
- Design adaptável para desktop e mobile
- Layout compacto para melhor aproveitamento
- Acessibilidade com ARIA labels
- Feedback visual para todas as ações
- Alertas contextuais e informativos

## Arquitetura e Tecnologias

### Backend
- **Python 3.8+** - Linguagem principal
- **Flask** - Framework web e APIs REST
- **Flask-SocketIO** - Comunicação WebSocket bidirecional
- **SQLite3** - Banco de dados relacional embarcado
- **Werkzeug** - Utilitários para upload e segurança

### Frontend
- **HTML5** - Estrutura semântica moderna
- **CSS3** - Estilização avançada com Flexbox/Grid
- **JavaScript ES6+** - Lógica cliente e manipulação DOM
- **Bootstrap 5** - Framework CSS responsivo
- **Font Awesome** - Biblioteca de ícones vetoriais
- **Socket.IO Client** - Cliente WebSocket

### Protocolos e Padrões
- **HTTP/HTTPS** - Protocolo base para APIs REST
- **WebSocket** - Comunicação full-duplex em tempo real
- **JSON** - Formato de troca de dados estruturados
- **CORS** - Cross-Origin Resource Sharing
- **REST** - Architectural style para APIs

## Estrutura do Projeto

```
webtalk-socker/
├── app.py                      # Aplicação principal com middleware de logging
├── config.py                   # Configurações centralizadas
├── limpar_banco.py            # Utilitário para manutenção do banco
├── models/
│   └── room.py                # Modelo completo de salas e gerenciamento
├── routes/
│   ├── __init__.py
│   ├── main.py                # Rotas principais e APIs
│   └── admin.py               # Rotas administrativas
├── socketio_handlers/
│   ├── __init__.py
│   └── events.py              # Manipuladores de eventos WebSocket
├── static/
│   ├── css/
│   │   ├── styles.css         # Estilos base compartilhados
│   │   ├── index.css          # Estilos específicos da página inicial
│   │   ├── chat.css           # Estilos do chat e mensagens
│   │   └── admin.css          # Estilos do painel administrativo
│   ├── js/
│   │   └── main.js            # JavaScript da página inicial
│   └── images/
│       └── ufcspa-logo.png    # Logo da universidade
├── templates/
│   ├── base.html              # Template base com modal sobre
│   ├── index.html             # Página inicial com lista de salas
│   ├── chat.html              # Interface de chat completa
│   └── admin.html             # Painel administrativo
├── uploads/                   # Diretório para arquivos compartilhados
├── db.sqlite3                 # Banco de dados SQLite
└── README.md                  # Documentação
```

## Instalação e Execução

### Pré-requisitos
- Python 3.8+
- pip (gerenciador de pacotes Python)

### Setup

1. **Clone o repositório**
```bash
git clone <repository-url>
cd webtalk-socker
```

2. **Instale as dependências**
```bash
pip install flask flask-socketio
```

3. **Execute a aplicação**
```bash
python app.py
```

4. **Acesse o sistema**
- Interface principal: http://localhost:5000
- Painel administrativo: http://localhost:5000/admin
- Senha admin padrão: `admin123`

### Configuração

Edite `config.py` para personalizar:

```python
class Config:
    HOST = '0.0.0.0'              # Host do servidor
    PORT = 5000                   # Porta do servidor
    DEBUG = True                  # Modo debug
    SECRET_KEY = 'your-secret'    # Chave secreta
    ADMIN_PASSWORD = 'admin123'   # Senha administrativa
```

## APIs e Endpoints

### Gerenciamento de Salas
```http
GET    /api/salas                    # Lista todas as salas ativas
POST   /api/salas                    # Criar nova sala
POST   /api/salas/{id}/entrar        # Validar acesso à sala
```

### Gerenciamento de Arquivos
```http
POST   /api/salas/{id}/upload       # Upload de arquivo
GET    /api/salas/{id}/download/{file} # Download de arquivo
DELETE /api/salas/{id}/mensagens/{msg_id} # Deletar mensagem/arquivo
```

### Administração
```http
GET    /api/admin/estatisticas      # Estatísticas do sistema
DELETE /api/admin/salas/{id}        # Excluir sala administrativamente
POST   /api/admin/configuracoes     # Atualizar configurações
POST   /api/admin/limpeza           # Limpar salas expiradas
```

## Eventos WebSocket

### Cliente → Servidor
| Evento | Payload | Descrição |
|--------|---------|-----------|
| `entrar` | `{id_sala, nome_usuario}` | Entrar em sala |
| `sair` | `{id_sala, nome_usuario}` | Sair da sala |
| `mensagem_chat` | `{id_sala, nome_usuario, mensagem}` | Enviar mensagem |
| `deletar_mensagem` | `{id_sala, id_mensagem, nome_usuario}` | Deletar mensagem própria |
| `arquivo_compartilhado` | `{id_sala, nome_usuario, nome_arquivo, tipo_arquivo}` | Notificar upload |

### Servidor → Cliente
| Evento | Payload | Descrição |
|--------|---------|-----------|
| `usuario_entrou` | `{nome_usuario}` | Notificar entrada |
| `usuario_saiu` | `{nome_usuario}` | Notificar saída |
| `mensagem_chat` | `{id, nome_usuario, mensagem, horario}` | Distribuir mensagem |
| `arquivo_compartilhado` | `{id, nome_usuario, nome_arquivo, tipo_arquivo}` | Notificar arquivo |
| `mensagem_removida` | `{id_mensagem, nome_usuario}` | Notificar remoção |
| `erro` | `{mensagem}` | Notificar erro |

## Utilitários de Manutenção

### Script de Limpeza do Banco
```bash
python limpar_banco.py
```

**Opções disponíveis:**
1. **Limpeza completa** - Remove banco e recria estrutura
2. **Limpeza de dados** - Mantém estrutura, remove dados
3. **Limpeza de órfãos** - Remove arquivos sem referência no banco
4. **Verificação de integridade** - Valida consistência dos dados

### Logging do Sistema

O sistema inclui logging compacto para monitoramento de operações HTTP e WebSocket:

```
[HH:MM:SS] HTTP_METHOD /path - IP: xxx.xxx.xxx.xxx
  Data: {dados_sanitizados}
  Response: STATUS_CODE OK (tempo_ms)

[HH:MM:SS] WS Connect: session_id
[HH:MM:SS] User Join: usuario -> Room sala_id
[HH:MM:SS] Chat Message: usuario in sala_id (tamanho chars)
```

## Conceitos de Redes Demonstrados

### Arquitetura Cliente-Servidor
- Servidor centralizado gerenciando múltiplos clientes
- Distribuição de mensagens para todos os participantes
- Gerenciamento de estado distribuído

### Protocolos de Comunicação
- **HTTP/REST** para operações CRUD (Create, Read, Update, Delete)
- **WebSocket** para comunicação bidirecional em tempo real
- **JSON** como formato de dados estruturados

### Concorrência e Threading
- Processamento simultâneo de múltiplas conexões
- Gerenciamento de salas com usuários concorrentes
- Threading para operações assíncronas

### Persistência e Consistência
- Banco de dados SQLite para persistência
- Sincronização entre memória e disco
- Transações para garantir consistência

### Segurança e Validação
- Validação de entrada para prevenir ataques
- Controle de acesso baseado em sessão
- Sanitização de dados para prevenção de XSS

## Recursos Técnicos Avançados

### Sistema de Soft Delete
- Mensagens deletadas permanecem visíveis como "deletada"
- Preserva integridade do histórico da conversa
- Remove arquivos físicos mas mantém registro no banco

### Upload Robusto
- Validação de conteúdo vs. extensão de arquivo
- Cleanup automático em caso de erro
- Progress feedback em tempo real
- Suporte a arquivos grandes (até 16MB)

### Interface Inteligente
- Preview de imagens com fundo escuro para transparência
- Layout responsivo para todas as telas
- Feedback visual para todas as ações
- Acessibilidade completa com ARIA labels

### Monitoramento Administrativo
- Estatísticas em tempo real do sistema
- Log de atividade recente
- Controle completo de salas ativas
- Configurações dinâmicas do servidor

## Equipe de Desenvolvimento

**Universidade Federal de Ciências da Saúde de Porto Alegre (UFCSPA)**  
**Curso:** Bacharelado em Informática Biomédica  
**Disciplina:** Fundamentos de Redes e Sistemas Distribuídos  
**Professor:** João Vicente Ferreira Lima

**Desenvolvedores:**
- [Bruno Costa E Silva Giuliani Lopes](https://www.linkedin.com/in/bruno-costa-e-silva-giuliani-lopes-955828282/)
- [Caio Foti Pontes](https://www.linkedin.com/in/caiofoti/)
- [Tainá Machado Selayaran](https://www.linkedin.com/in/taina-selayaran/)

## Objetivos Acadêmicos

Este projeto demonstra na prática os fundamentos de redes e sistemas distribuídos através de:

1. **Implementação de protocolos de rede** - HTTP e WebSocket
2. **Arquitetura cliente-servidor** com estado compartilhado
3. **Engenharia de software** com separação de responsabilidades
4. **Segurança de aplicações web** com validação e sanitização
5. **Otimizações para múltiplos usuários** simultâneos
6. **Interface de usuário** intuitiva e acessível

## Estatísticas do Projeto

- **Linguagens:** Python, HTML, CSS, JavaScript
- **Linhas de código:** ~3.500+
- **Arquivos:** 20+ arquivos organizados em módulos
- **APIs:** 10+ endpoints REST funcionais
- **Eventos WebSocket:** 8+ eventos bidirecionais
- **Funcionalidades:** 25+ features implementadas

---

**WebTalk Socket** - Sistema acadêmico para demonstração de conceitos de redes e sistemas distribuídos.