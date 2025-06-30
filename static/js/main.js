let salasData = [];
let salasFiltradas = [];
let paginaAtual = 1;
const itensPorPagina = 10;
let carregandoSalas = false;

document.addEventListener('DOMContentLoaded', function() {
    // Event listeners for modal forms
    document.getElementById('formularioCriarSala').addEventListener('submit', function(e) {
        e.preventDefault();
        criarSala();
    });
    
    document.getElementById('formularioEntrarSala').addEventListener('submit', function(e) {
        e.preventDefault();
        entrarNaSala();
    });
    
    // Search and filter event listeners
    document.getElementById('searchInput').addEventListener('input', filtrarSalas);
    document.getElementById('filterStatus').addEventListener('change', filtrarSalas);
    
    // Carregar salas inicialmente
    carregarSalas();
});

function carregarSalas() {
    if (carregandoSalas) return;
    
    carregandoSalas = true;
    const tableBody = document.getElementById('roomsTableBody');
    
    tableBody.innerHTML = `
        <tr>
            <td colspan="6" class="text-center" style="padding: 2rem;">
                <div class="loading"></div>
                <div style="margin-top: 0.5rem;">Carregando salas...</div>
            </td>
        </tr>
    `;
    
    fetch('/api/salas')
        .then(resposta => resposta.json())
        .then(salas => {
            salasData = salas;
            filtrarSalas();
            carregandoSalas = false;
        })
        .catch(erro => {
            console.error('Erro ao carregar salas:', erro);
            tableBody.innerHTML = `
                <tr>
                    <td colspan="6" class="text-center" style="padding: 2rem;">
                        <div style="color: #e74c3c;">
                            <i class="fas fa-exclamation-triangle"></i>
                            Erro ao carregar salas
                        </div>
                        <button class="btn-control small" onclick="carregarSalas()" style="margin-top: 0.5rem;">
                            <i class="fas fa-sync-alt"></i> Tentar Novamente
                        </button>
                    </td>
                </tr>
            `;
            carregandoSalas = false;
        });
}

function filtrarSalas() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const statusFilter = document.getElementById('filterStatus').value;
    
    salasFiltradas = salasData.filter(sala => {
        const matchesSearch = sala.nome.toLowerCase().includes(searchTerm) || 
                            sala.criador.toLowerCase().includes(searchTerm);
        
        const matchesStatus = statusFilter === 'all' || 
                            (statusFilter === 'public' && !sala.tem_senha) ||
                            (statusFilter === 'protected' && sala.tem_senha);
        
        return matchesSearch && matchesStatus;
    });
    
    paginaAtual = 1;
    exibirSalas();
    atualizarPaginacao();
}

function exibirSalas() {
    const tableBody = document.getElementById('roomsTableBody');
    
    if (salasFiltradas.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center" style="padding: 3rem;">
                    <div class="empty-state">
                        <h5>Nenhuma sala encontrada</h5>
                        <p>Não há salas que correspondam aos critérios de busca</p>
                        <button class="btn-control" data-bs-toggle="modal" data-bs-target="#criarSalaModal">
                            <i class="fas fa-plus"></i> Criar Nova Sala
                        </button>
                    </div>
                </td>
            </tr>
        `;
        return;
    }
    
    const inicio = (paginaAtual - 1) * itensPorPagina;
    const fim = inicio + itensPorPagina;
    const salasExibidas = salasFiltradas.slice(inicio, fim);
    
    tableBody.innerHTML = salasExibidas.map(sala => `
        <tr onclick="entrarNaSalaClique('${sala.id}', '${sala.nome}', ${sala.tem_senha})">
            <td>
                <div class="room-name">${sala.nome}</div>
                <div class="room-creator">Por ${sala.criador}</div>
            </td>
            <td>
                <span class="room-badge">${sala.id}</span>
            </td>
            <td>
                <span class="status-badge ${sala.tem_senha ? 'protected' : 'public'}">
                    <i class="fas fa-${sala.tem_senha ? 'lock' : 'globe'}"></i>
                    ${sala.tem_senha ? 'Protegida' : 'Pública'}
                </span>
            </td>
            <td>
                <div class="room-stats">
                    <span><i class="fas fa-users"></i> ${sala.contador_usuarios || 0}</span>
                    <span><i class="fas fa-comments"></i> ${sala.contador_mensagens || 0}</span>
                </div>
            </td>
            <td>
                <small>${formatarData(sala.criado_em)}</small>
            </td>
            <td>
                <div class="room-actions">
                    <button class="btn-join" onclick="event.stopPropagation(); entrarNaSalaClique('${sala.id}', '${sala.nome}', ${sala.tem_senha})" title="Entrar na sala">
                        <i class="fas fa-sign-in-alt"></i> Entrar
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

function atualizarPaginacao() {
    const totalPaginas = Math.ceil(salasFiltradas.length / itensPorPagina);
    const inicio = (paginaAtual - 1) * itensPorPagina + 1;
    const fim = Math.min(paginaAtual * itensPorPagina, salasFiltradas.length);
    
    document.getElementById('paginationInfo').textContent = 
        `Mostrando ${inicio}-${fim} de ${salasFiltradas.length} salas`;
    
    document.getElementById('prevBtn').disabled = paginaAtual <= 1;
    document.getElementById('nextBtn').disabled = paginaAtual >= totalPaginas;
    
    // Atualizar números das páginas
    const pageNumbers = document.getElementById('pageNumbers');
    pageNumbers.innerHTML = '';
    
    const maxPages = 5;
    let startPage = Math.max(1, paginaAtual - Math.floor(maxPages / 2));
    let endPage = Math.min(totalPaginas, startPage + maxPages - 1);
    
    if (endPage - startPage + 1 < maxPages) {
        startPage = Math.max(1, endPage - maxPages + 1);
    }
    
    for (let i = startPage; i <= endPage; i++) {
        const btn = document.createElement('button');
        btn.className = `page-btn ${i === paginaAtual ? 'active' : ''}`;
        btn.textContent = i;
        btn.title = `Ir para página ${i}`;
        btn.setAttribute('aria-label', `Ir para página ${i}`);
        btn.onclick = () => irParaPagina(i);
        pageNumbers.appendChild(btn);
    }
}

function mudarPagina(direcao) {
    const totalPaginas = Math.ceil(salasFiltradas.length / itensPorPagina);
    const novaPagina = paginaAtual + direcao;
    
    if (novaPagina >= 1 && novaPagina <= totalPaginas) {
        paginaAtual = novaPagina;
        exibirSalas();
        atualizarPaginacao();
    }
}

function irParaPagina(pagina) {
    paginaAtual = pagina;
    exibirSalas();
    atualizarPaginacao();
}

function criarSala() {
    const nome = document.getElementById('nomeSala').value.trim();
    const criador = document.getElementById('nomeCriador').value.trim();
    const senha = document.getElementById('senhaSala').value.trim();
    
    if (!nome || !criador) {
        mostrarAlerta('Por favor, preencha nome da sala e seu nome', 'warning');
        return;
    }
    
    const botaoEnviar = document.querySelector('#criarSalaModal .btn-primary');
    const textoOriginal = botaoEnviar.innerHTML;
    botaoEnviar.disabled = true;
    botaoEnviar.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Criando...';
    
    fetch('/api/salas', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            nome: nome,
            criador: criador,
            senha: senha || null
        })
    })
    .then(resposta => resposta.json())
    .then(dados => {
        if (dados.erro) {
            mostrarAlerta(dados.erro, 'danger');
        } else {
            mostrarAlerta(`Sala criada! Código: ${dados.id_sala}`, 'success');
            document.getElementById('formularioCriarSala').reset();
            carregarSalas();
            
            const modal = bootstrap.Modal.getInstance(document.getElementById('criarSalaModal'));
            modal.hide();
            
            if (confirm('Sala criada com sucesso! Deseja entrar agora?')) {
                window.location.href = `/chat/${dados.id_sala}?username=${encodeURIComponent(criador)}`;
            }
        }
    })
    .catch(erro => {
        mostrarAlerta('Erro ao criar sala', 'danger');
        console.error('Erro:', erro);
    })
    .finally(() => {
        botaoEnviar.disabled = false;
        botaoEnviar.innerHTML = textoOriginal;
    });
}

function entrarNaSala() {
    const idSala = document.getElementById('idSalaEntrar').value.trim();
    const nomeUsuario = document.getElementById('nomeUsuarioEntrar').value.trim();
    const senha = document.getElementById('senhaEntrar').value.trim();
    
    if (!idSala || !nomeUsuario) {
        mostrarAlerta('Por favor, preencha código da sala e seu nome', 'warning');
        return;
    }
    
    const botaoEnviar = document.querySelector('#entrarSalaModal .btn-primary');
    const textoOriginal = botaoEnviar.innerHTML;
    botaoEnviar.disabled = true;
    botaoEnviar.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Entrando...';
    
    fetch(`/api/salas/${idSala}/entrar`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            senha: senha
        })
    })
    .then(resposta => resposta.json())
    .then(dados => {
        if (dados.erro) {
            mostrarAlerta(dados.erro, 'danger');
        } else {
            window.location.href = `/chat/${idSala}?username=${encodeURIComponent(nomeUsuario)}`;
        }
    })
    .catch(erro => {
        mostrarAlerta('Erro ao entrar na sala', 'danger');
        console.error('Erro:', erro);
    })
    .finally(() => {
        botaoEnviar.disabled = false;
        botaoEnviar.innerHTML = textoOriginal;
    });
}

function entrarNaSalaClique(idSala, nomeSala, temSenha) {
    const nomeUsuario = prompt(`Digite seu nome para entrar na sala "${nomeSala}":`);
    if (!nomeUsuario || nomeUsuario.trim() === '') return;
    
    if (temSenha) {
        document.getElementById('idSalaModal').value = idSala;
        document.getElementById('nomeUsuarioModal').value = nomeUsuario.trim();
        document.getElementById('senhaModal').value = '';
        new bootstrap.Modal(document.getElementById('modalSenha')).show();
    } else {
        window.location.href = `/chat/${idSala}?username=${encodeURIComponent(nomeUsuario.trim())}`;
    }
}

function enviarSenha() {
    const idSala = document.getElementById('idSalaModal').value;
    const nomeUsuario = document.getElementById('nomeUsuarioModal').value;
    const senha = document.getElementById('senhaModal').value;
    
    fetch(`/api/salas/${idSala}/entrar`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            senha: senha
        })
    })
    .then(resposta => resposta.json())
    .then(dados => {
        const modal = bootstrap.Modal.getInstance(document.getElementById('modalSenha'));
        if (dados.erro) {
            mostrarAlerta(dados.erro, 'danger');
            document.getElementById('senhaModal').focus();
        } else {
            modal.hide();
            window.location.href = `/chat/${idSala}?username=${encodeURIComponent(nomeUsuario)}`;
        }
    })
    .catch(erro => {
        mostrarAlerta('Erro ao verificar senha', 'danger');
        console.error('Erro:', erro);
    });
}

function formatarData(stringData) {
    if (!stringData) return 'Agora';
    try {
        const data = new Date(stringData);
        const agora = new Date();
        const diferencaMs = agora - data;
        const diferencaMinutos = Math.floor(diferencaMs / 60000);
        const diferencaHoras = Math.floor(diferencaMinutos / 60);
        const diferencaDias = Math.floor(diferencaHoras / 24);
        
        if (diferencaMinutos < 1) return 'Agora';
        if (diferencaMinutos < 60) return `${diferencaMinutos}min`;
        if (diferencaHoras < 24) return `${diferencaHoras}h`;
        if (diferencaDias < 7) return `${diferencaDias}d`;
        
        return data.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' });
    } catch {
        return 'N/A';
    }
}

function mostrarAlerta(mensagem, tipo) {
    const alertasExistentes = document.querySelectorAll('.alerta-customizado');
    alertasExistentes.forEach(alerta => alerta.remove());
    
    const divAlerta = document.createElement('div');
    divAlerta.className = `alert alert-${tipo} alert-dismissible fade show alerta-customizado position-fixed`;
    divAlerta.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px; max-width: 400px;';
    divAlerta.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas fa-${obterIconeAlerta(tipo)} me-2"></i>
            <div>${mensagem}</div>
        </div>
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(divAlerta);
    
    setTimeout(() => {
        if (divAlerta.parentNode) {
            divAlerta.remove();
        }
    }, 5000);
}

function obterIconeAlerta(tipo) {
    const icones = {
        'success': 'check-circle',
        'danger': 'exclamation-triangle',
        'warning': 'exclamation-circle',
        'info': 'info-circle'
    };
    return icones[tipo] || 'info-circle';
}