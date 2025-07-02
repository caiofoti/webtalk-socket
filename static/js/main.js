let salasData = [];
let salasFiltradas = [];
let paginaAtual = 1;
// RESPONSIVE ITEMS PER PAGE
let itensPorPagina = window.innerWidth <= 768 ? 3 : 5;
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
    
    // PAGINATION EVENT LISTENERS - FIX
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    
    if (prevBtn) {
        prevBtn.addEventListener('click', function(e) {
            e.preventDefault();
            mudarPagina(-1);
        });
    }
    
    if (nextBtn) {
        nextBtn.addEventListener('click', function(e) {
            e.preventDefault();
            mudarPagina(1);
        });
    }
    
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

function atualizarPaginacao() {
    // UPDATE ITEMS PER PAGE BASED ON CURRENT SCREEN SIZE
    const novoItensPorPagina = window.innerWidth <= 768 ? 3 : 5;
    
    // Se mudou o número de itens por página, recalcular página atual
    if (novoItensPorPagina !== itensPorPagina) {
        const itemAtual = (paginaAtual - 1) * itensPorPagina;
        itensPorPagina = novoItensPorPagina;
        paginaAtual = Math.floor(itemAtual / itensPorPagina) + 1;
        console.log(`[PAGINATION] Items per page changed to ${itensPorPagina}, adjusted to page ${paginaAtual}`);
    }
    
    const totalPaginas = Math.ceil(salasFiltradas.length / itensPorPagina);
    const inicio = (paginaAtual - 1) * itensPorPagina + 1;
    const fim = Math.min(paginaAtual * itensPorPagina, salasFiltradas.length);
    
    // Update pagination info
    const paginationInfo = document.getElementById('paginationInfo');
    if (paginationInfo) {
        if (salasFiltradas.length === 0) {
            paginationInfo.textContent = 'Nenhuma sala encontrada';
        } else {
            const isMobile = window.innerWidth <= 768;
            const deviceText = isMobile ? 'móvel' : 'desktop';
            paginationInfo.textContent = `${inicio}-${fim} de ${salasFiltradas.length} salas (${itensPorPagina}/página - ${deviceText})`;
        }
    }
    
    // Update navigation buttons
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    
    if (prevBtn) {
        prevBtn.disabled = paginaAtual <= 1;
        prevBtn.classList.toggle('disabled', paginaAtual <= 1);
    }
    
    if (nextBtn) {
        nextBtn.disabled = paginaAtual >= totalPaginas || totalPaginas === 0;
        nextBtn.classList.toggle('disabled', paginaAtual >= totalPaginas || totalPaginas === 0);
    }
    
    // Update page numbers with optimized display for 5 items
    const pageNumbers = document.getElementById('pageNumbers');
    if (pageNumbers) {
        pageNumbers.innerHTML = '';
        
        if (totalPaginas > 0) {
            const isMobile = window.innerWidth <= 768;
            const maxPages = isMobile ? 3 : 7; // More page numbers on desktop for 5-item pagination
            
            let startPage = Math.max(1, paginaAtual - Math.floor(maxPages / 2));
            let endPage = Math.min(totalPaginas, startPage + maxPages - 1);
            
            // Adjust start page if we're near the end
            if (endPage - startPage + 1 < maxPages) {
                startPage = Math.max(1, endPage - maxPages + 1);
            }
            
            // Add "First" button if needed (only on desktop)
            if (!isMobile && startPage > 1) {
                const firstBtn = document.createElement('button');
                firstBtn.className = 'page-btn';
                firstBtn.textContent = '1';
                firstBtn.title = 'Ir para primeira página';
                firstBtn.onclick = () => irParaPagina(1);
                pageNumbers.appendChild(firstBtn);
                
                if (startPage > 2) {
                    const ellipsis = document.createElement('span');
                    ellipsis.className = 'page-ellipsis';
                    ellipsis.textContent = '...';
                    pageNumbers.appendChild(ellipsis);
                }
            }
            
            // Add page number buttons
            for (let i = startPage; i <= endPage; i++) {
                const btn = document.createElement('button');
                btn.className = `page-btn ${i === paginaAtual ? 'active' : ''}`;
                btn.textContent = i;
                btn.title = `Ir para página ${i}`;
                btn.setAttribute('aria-label', `Ir para página ${i}`);
                btn.onclick = () => irParaPagina(i);
                pageNumbers.appendChild(btn);
            }
            
            // Add "Last" button if needed (only on desktop)
            if (!isMobile && endPage < totalPaginas) {
                if (endPage < totalPaginas - 1) {
                    const ellipsis = document.createElement('span');
                    ellipsis.className = 'page-ellipsis';
                    ellipsis.textContent = '...';
                    pageNumbers.appendChild(ellipsis);
                }
                
                const lastBtn = document.createElement('button');
                lastBtn.className = 'page-btn';
                lastBtn.textContent = totalPaginas;
                lastBtn.title = 'Ir para última página';
                lastBtn.onclick = () => irParaPagina(totalPaginas);
                pageNumbers.appendChild(lastBtn);
            }
        }
    }
    
    console.log(`[PAGINATION] Página ${paginaAtual} de ${totalPaginas} (${salasFiltradas.length} salas, ${itensPorPagina} por página)`);
}

function mudarPagina(direcao) {
    const totalPaginas = Math.ceil(salasFiltradas.length / itensPorPagina);
    const novaPagina = paginaAtual + direcao;
    
    console.log(`[PAGINATION] Tentando mudar da página ${paginaAtual} para ${novaPagina}`);
    
    if (novaPagina >= 1 && novaPagina <= totalPaginas) {
        paginaAtual = novaPagina;
        exibirSalas();
        atualizarPaginacao();
        
        // Scroll to top of rooms section
        const roomsSection = document.querySelector('.rooms-section');
        if (roomsSection) {
            roomsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
        
        console.log(`[PAGINATION] Mudou para página ${paginaAtual}`);
    } else {
        console.log(`[PAGINATION] Página ${novaPagina} inválida (total: ${totalPaginas})`);
    }
}

function irParaPagina(pagina) {
    const totalPaginas = Math.ceil(salasFiltradas.length / itensPorPagina);
    
    console.log(`[PAGINATION] Indo diretamente para página ${pagina}`);
    
    if (pagina >= 1 && pagina <= totalPaginas) {
        paginaAtual = pagina;
        exibirSalas();
        atualizarPaginacao();
        
        // Scroll to top of rooms section
        const roomsSection = document.querySelector('.rooms-section');
        if (roomsSection) {
            roomsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
        
        console.log(`[PAGINATION] Foi para página ${paginaAtual}`);
    } else {
        console.log(`[PAGINATION] Página ${pagina} inválida (total: ${totalPaginas})`);
    }
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

// Mobile-specific optimizations
document.addEventListener('DOMContentLoaded', function() {
    // Handle mobile file inputs with better UX
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file && window.innerWidth <= 768) {
                // Mobile file validation with user feedback
                const maxSize = 16 * 1024 * 1024; // 16MB
                if (file.size > maxSize) {
                    mostrarAlerta('Arquivo muito grande! Máximo: 16MB', 'warning');
                    this.value = '';
                    return;
                }
                
                // Show file selected feedback on mobile
                const fileName = file.name.length > 20 ? 
                    file.name.substring(0, 20) + '...' : file.name;
                mostrarAlerta(`Arquivo selecionado: ${fileName}`, 'info');
            }
        });
    });
    
    let resizeTimer;
    let currentViewMode = window.innerWidth <= 768 ? 'mobile' : 'desktop';
    let currentItemsPerPage = window.innerWidth <= 768 ? 3 : 5; // Fixed values
    
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            const newViewMode = window.innerWidth <= 768 ? 'mobile' : 'desktop';
            const newItemsPerPage = window.innerWidth <= 768 ? 3 : 5; // Fixed values
            
            const viewModeChanged = newViewMode !== currentViewMode;
            const itemsPerPageChanged = newItemsPerPage !== currentItemsPerPage;
            
            if (viewModeChanged || itemsPerPageChanged) {
                currentViewMode = newViewMode;
                currentItemsPerPage = newItemsPerPage;
                
                console.log(`[RESPONSIVE] Changed to ${currentViewMode} mode (${currentItemsPerPage} items per page)`);
                
                if (typeof exibirSalas === 'function' && salasData.length > 0) {
                    itensPorPagina = currentItemsPerPage;
                    filtrarSalas();
                }
            }
        }, 250);
    });
    
    // Forçar re-renderização inicial para mobile
    setTimeout(() => {
        if (window.innerWidth <= 768 && salasData.length > 0) {
            console.log('[MOBILE] Forçando re-renderização inicial');
            exibirSalas();
        }
    }, 500);
});

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
    
    // RESET PAGINATION TO FIRST PAGE WHEN FILTERING
    paginaAtual = 1;
    exibirSalas();
    atualizarPaginacao();
    
    console.log(`[FILTER] Filtradas ${salasFiltradas.length} salas de ${salasData.length} total`);
}


function exibirSalas() {
    const tableBody = document.getElementById('roomsTableBody');
    const isMobile = window.innerWidth <= 768;
    
    if (salasFiltradas.length === 0) {
        if (isMobile) {
            // Mobile empty state
            const tableContainer = tableBody.closest('.rooms-table-container');
            if (tableContainer) {
                // Hide table and show mobile container
                const table = tableContainer.querySelector('.rooms-table');
                if (table) {
                    table.style.display = 'none';
                }
                
                let mobileContainer = tableContainer.querySelector('.mobile-rooms-container');
                if (!mobileContainer) {
                    mobileContainer = document.createElement('div');
                    mobileContainer.className = 'mobile-rooms-container';
                    tableContainer.appendChild(mobileContainer);
                }
                
                mobileContainer.style.display = 'grid';
                mobileContainer.innerHTML = `
                    <div class="empty-state">
                        <h5>Nenhuma sala encontrada</h5>
                        <p>Não há salas que correspondam aos critérios de busca</p>
                        <button class="btn-control" data-bs-toggle="modal" data-bs-target="#criarSalaModal">
                            <i class="fas fa-plus"></i> Criar Nova Sala
                        </button>
                    </div>
                `;
            }
        } else {
            // Desktop empty state
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
        }
        return;
    }
    
    const inicio = (paginaAtual - 1) * itensPorPagina;
    const fim = inicio + itensPorPagina;
    const salasExibidas = salasFiltradas.slice(inicio, fim);
    
    if (isMobile) {
        // Mobile card layout
        const tableContainer = tableBody.closest('.rooms-table-container');
        const table = tableContainer.querySelector('.rooms-table');
        
        // Hide table on mobile
        if (table) {
            table.style.display = 'none';
        }
        
        // Find or create mobile container
        let mobileContainer = tableContainer.querySelector('.mobile-rooms-container');
        if (!mobileContainer) {
            mobileContainer = document.createElement('div');
            mobileContainer.className = 'mobile-rooms-container';
            tableContainer.appendChild(mobileContainer);
        }
        
        // Show mobile container
        mobileContainer.style.display = 'grid';
        
        // Render mobile cards
        mobileContainer.innerHTML = salasExibidas.map(sala => `
            <div class="mobile-room-card" onclick="entrarNaSalaClique('${sala.id}', '${escaparHtml(sala.nome)}', ${sala.tem_senha})">
                <div class="mobile-room-header">
                    <div class="mobile-room-info">
                        <h3 class="mobile-room-name">${escaparHtml(sala.nome)}</h3>
                        <p class="mobile-room-creator">Por ${escaparHtml(sala.criador)}</p>
                    </div>
                    <span class="mobile-room-badge">${sala.id}</span>
                </div>
                <div class="mobile-room-body">
                    <div class="mobile-room-meta">
                        <div class="mobile-room-status">
                            <span class="mobile-status-badge ${sala.tem_senha ? 'protected' : 'public'}">
                                <i class="fas fa-${sala.tem_senha ? 'lock' : 'globe'}"></i>
                                ${sala.tem_senha ? 'Protegida' : 'Pública'}
                            </span>
                            <div class="mobile-room-stats">
                                <span><i class="fas fa-users"></i> ${sala.contador_usuarios || 0}</span>
                                <span><i class="fas fa-comments"></i> ${sala.contador_mensagens || 0}</span>
                            </div>
                        </div>
                    </div>
                    <div class="mobile-room-footer">
                        <div class="mobile-room-date">${formatarData(sala.criado_em)}</div>
                        <button class="mobile-join-btn" onclick="event.stopPropagation(); entrarNaSalaClique('${sala.id}', '${escaparHtml(sala.nome)}', ${sala.tem_senha})" title="Entrar na sala">
                            <i class="fas fa-sign-in-alt"></i> Entrar
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
        
        console.log(`[MOBILE] Rendered ${salasExibidas.length} rooms in cards`);
        
    } else {
        // Desktop table layout
        const tableContainer = tableBody.closest('.rooms-table-container');
        const table = tableContainer.querySelector('.rooms-table');
        const mobileContainer = tableContainer.querySelector('.mobile-rooms-container');
        
        // Show table on desktop
        if (table) {
            table.style.display = 'table';
        }
        
        // Hide mobile container on desktop
        if (mobileContainer) {
            mobileContainer.style.display = 'none';
        }
        
        // Render desktop table
        tableBody.innerHTML = salasExibidas.map(sala => `
            <tr onclick="entrarNaSalaClique('${sala.id}', '${escaparHtml(sala.nome)}', ${sala.tem_senha})">
                <td>
                    <div class="room-name">${escaparHtml(sala.nome)}</div>
                    <div class="room-creator">Por ${escaparHtml(sala.criador)}</div>
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
                        <button class="btn-join" onclick="event.stopPropagation(); entrarNaSalaClique('${sala.id}', '${escaparHtml(sala.nome)}', ${sala.tem_senha})" title="Entrar na sala">
                            <i class="fas fa-sign-in-alt"></i> Entrar
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
        
        console.log(`[DESKTOP] Rendered ${salasExibidas.length} rooms in table`);
    }
}

// Adicionar função para escapar HTML
function escaparHtml(texto) {
    if (typeof texto !== 'string') return texto;
    const div = document.createElement('div');
    div.textContent = texto;
    return div.innerHTML;
}