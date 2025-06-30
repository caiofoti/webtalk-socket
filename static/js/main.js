document.addEventListener('DOMContentLoaded', function() {
    carregarSalas();
    
    // Form para criar sala
    const formCriarSala = document.getElementById('formularioCriarSala');
    if (formCriarSala) {
        formCriarSala.addEventListener('submit', function(e) {
            e.preventDefault();
            criarSala();
        });
    }
    
    // Form para entrar na sala
    const formEntrarSala = document.getElementById('formularioEntrarSala');
    if (formEntrarSala) {
        formEntrarSala.addEventListener('submit', function(e) {
            e.preventDefault();
            entrarNaSala();
        });
    }
    
    // Recarregar salas a cada 30 segundos
    setInterval(carregarSalas, 30000);
});

function criarSala() {
    const nome = document.getElementById('nomeSala').value.trim();
    const criador = document.getElementById('nomeCriador').value.trim();
    const senha = document.getElementById('senhaSala').value.trim();
    
    if (!nome || !criador) {
        mostrarAlerta('Por favor, preencha nome da sala e seu nome!', 'warning');
        return;
    }
    
    // Desabilitar botão durante o envio
    const botaoEnviar = document.querySelector('#formularioCriarSala button[type="submit"]');
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
            mostrarAlerta(`Sala criada com sucesso! Código: ${dados.id_sala}`, 'success');
            document.getElementById('formularioCriarSala').reset();
            carregarSalas();
            
            // Redirecionar para a sala criada
            if (confirm('Deseja entrar na sala agora?')) {
                window.location.href = `/chat/${dados.id_sala}?username=${encodeURIComponent(criador)}`;
            }
        }
    })
    .catch(erro => {
        mostrarAlerta('Erro ao criar sala!', 'danger');
        console.error('Erro:', erro);
    })
    .finally(() => {
        botaoEnviar.disabled = false;
        botaoEnviar.innerHTML = textoOriginal;
    });
}

function carregarSalas() {
    fetch('/api/salas')
        .then(resposta => resposta.json())
        .then(salas => {
            exibirSalas(salas);
        })
        .catch(erro => {
            console.error('Erro ao carregar salas:', erro);
            const listaSalas = document.getElementById('listaSalas');
            if (listaSalas) {
                listaSalas.innerHTML = 
                    '<div class="alert alert-danger m-3">Erro ao carregar salas</div>';
            }
        });
}

function exibirSalas(salas) {
    const listaSalas = document.getElementById('listaSalas');
    
    if (!listaSalas) return;
    
    if (salas.length === 0) {
        listaSalas.innerHTML = `
            <div class="text-center p-4">
                <i class="fas fa-inbox fa-3x text-muted mb-3"></i>
                <p class="text-muted">Nenhuma sala ativa no momento</p>
                <small class="text-muted">Crie uma nova sala para começar!</small>
            </div>
        `;
        return;
    }
    
    let html = '';
    salas.forEach(sala => {
        const iconeChave = sala.tem_senha ? '<i class="fas fa-lock text-warning ms-1"></i>' : '';
        const classeStatus = sala.esta_ativa ? 'success' : 'secondary';
        const contadorUsuarios = sala.contador_usuarios || 0;
        const contadorMensagens = sala.contador_mensagens || 0;
        
        html += `
            <div class="card room-item mb-2" onclick="entrarNaSalaClique('${sala.id}', '${sala.nome}', ${sala.tem_senha})" style="cursor: pointer;">
                <div class="card-body p-3">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1">
                            <h6 class="card-title mb-1 d-flex align-items-center">
                                <i class="fas fa-comments text-primary me-2"></i>
                                ${sala.nome} ${iconeChave}
                            </h6>
                            <p class="card-text mb-2">
                                <small class="text-muted">
                                    <i class="fas fa-user me-1"></i>Por: ${sala.criador}
                                </small>
                            </p>
                            <div class="d-flex align-items-center">
                                <span class="badge bg-${classeStatus} me-2">${sala.id}</span>
                                <small class="text-muted">
                                    ${formatarData(sala.criado_em)}
                                </small>
                            </div>
                        </div>
                        <div class="text-end">
                            <div class="mb-1">
                                <small class="text-muted">
                                    <i class="fas fa-users text-info"></i> ${contadorUsuarios}
                                </small>
                            </div>
                            <div>
                                <small class="text-muted">
                                    <i class="fas fa-comments text-success"></i> ${contadorMensagens}
                                </small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    
    listaSalas.innerHTML = html;
}

function entrarNaSala() {
    const idSala = document.getElementById('idSalaEntrar').value.trim();
    const nomeUsuario = document.getElementById('nomeUsuarioEntrar').value.trim();
    const senha = document.getElementById('senhaEntrar').value.trim();
    
    if (!idSala || !nomeUsuario) {
        mostrarAlerta('Por favor, preencha código da sala e seu nome!', 'warning');
        return;
    }
    
    // Desabilitar botão durante o envio
    const botaoEnviar = document.querySelector('#formularioEntrarSala button[type="submit"]');
    const textoOriginal = botaoEnviar.innerHTML;
    botaoEnviar.disabled = true;
    botaoEnviar.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Entrando...';
    
    // Verificar se a sala existe e se a senha está correta
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
            // Redirecionar para a sala
            window.location.href = `/chat/${idSala}?username=${encodeURIComponent(nomeUsuario)}`;
        }
    })
    .catch(erro => {
        mostrarAlerta('Erro ao entrar na sala!', 'danger');
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
        // Mostrar modal para senha
        document.getElementById('idSalaModal').value = idSala;
        document.getElementById('nomeUsuarioModal').value = nomeUsuario.trim();
        document.getElementById('senhaModal').value = '';
        new bootstrap.Modal(document.getElementById('modalSenha')).show();
    } else {
        // Entrar diretamente
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
        mostrarAlerta('Erro ao verificar senha!', 'danger');
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
        if (diferencaMinutos < 60) return `${diferencaMinutos}min atrás`;
        if (diferencaHoras < 24) return `${diferencaHoras}h atrás`;
        if (diferencaDias < 7) return `${diferencaDias}d atrás`;
        
        return data.toLocaleDateString('pt-BR');
    } catch {
        return stringData;
    }
}

function mostrarAlerta(mensagem, tipo) {
    // Remover alertas existentes
    const alertasExistentes = document.querySelectorAll('.alerta-customizado');
    alertasExistentes.forEach(alerta => alerta.remove());
    
    // Criar novo alerta
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
    
    // Remover automaticamente após 5 segundos
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