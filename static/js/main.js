document.addEventListener('DOMContentLoaded', function() {
    loadRooms();
    
    // Form para criar sala
    document.getElementById('createRoomForm').addEventListener('submit', function(e) {
        e.preventDefault();
        createRoom();
    });
    
    // Recarregar salas a cada 30 segundos
    setInterval(loadRooms, 30000);
});

function createRoom() {
    const name = document.getElementById('roomName').value.trim();
    const creator = document.getElementById('creatorName').value.trim();
    const password = document.getElementById('roomPassword').value.trim();
    
    if (!name || !creator) {
        showAlert('Por favor, preencha nome da sala e seu nome!', 'warning');
        return;
    }
    
    // Desabilitar botão durante o envio
    const submitBtn = document.querySelector('#createRoomForm button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Criando...';
    
    fetch('/api/rooms', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            name: name,
            creator: creator,
            password: password || null
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showAlert(data.error, 'danger');
        } else {
            showAlert(`Sala criada com sucesso! Código: ${data.room_id}`, 'success');
            document.getElementById('createRoomForm').reset();
            loadRooms();
            
            // Redirecionar para a sala criada
            if (confirm('Deseja entrar na sala agora?')) {
                window.location.href = `/chat/${data.room_id}?username=${encodeURIComponent(creator)}`;
            }
        }
    })
    .catch(error => {
        showAlert('Erro ao criar sala!', 'danger');
        console.error('Erro:', error);
    })
    .finally(() => {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
    });
}

function loadRooms() {
    fetch('/api/rooms')
        .then(response => response.json())
        .then(rooms => {
            displayRooms(rooms);
        })
        .catch(error => {
            console.error('Erro ao carregar salas:', error);
            document.getElementById('roomsList').innerHTML = 
                '<div class="alert alert-danger m-3">Erro ao carregar salas</div>';
        });
}

function displayRooms(rooms) {
    const roomsList = document.getElementById('roomsList');
    
    if (rooms.length === 0) {
        roomsList.innerHTML = `
            <div class="text-center p-4">
                <i class="fas fa-inbox fa-3x text-muted mb-3"></i>
                <p class="text-muted">Nenhuma sala ativa no momento</p>
                <small class="text-muted">Crie uma nova sala para começar!</small>
            </div>
        `;
        return;
    }
    
    let html = '';
    rooms.forEach(room => {
        const lockIcon = room.has_password ? '<i class="fas fa-lock text-warning ms-1"></i>' : '';
        const statusClass = room.is_active ? 'success' : 'secondary';
        const userCount = room.user_count || 0;
        const messageCount = room.message_count || 0;
        
        html += `
            <div class="card room-item mb-2" onclick="enterRoom('${room.id}', '${room.name}', ${room.has_password})" style="cursor: pointer;">
                <div class="card-body p-3">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1">
                            <h6 class="card-title mb-1 d-flex align-items-center">
                                <i class="fas fa-comments text-primary me-2"></i>
                                ${room.name} ${lockIcon}
                            </h6>
                            <p class="card-text mb-2">
                                <small class="text-muted">
                                    <i class="fas fa-user me-1"></i>Por: ${room.creator}
                                </small>
                            </p>
                            <div class="d-flex align-items-center">
                                <span class="badge bg-${statusClass} me-2">${room.id}</span>
                                <small class="text-muted">
                                    ${formatDate(room.created_at)}
                                </small>
                            </div>
                        </div>
                        <div class="text-end">
                            <div class="mb-1">
                                <small class="text-muted">
                                    <i class="fas fa-users text-info"></i> ${userCount}
                                </small>
                            </div>
                            <div>
                                <small class="text-muted">
                                    <i class="fas fa-comments text-success"></i> ${messageCount}
                                </small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    
    roomsList.innerHTML = html;
}

function joinRoom() {
    const roomId = document.getElementById('joinRoomId').value.trim();
    const username = document.getElementById('joinUsername').value.trim();
    const password = document.getElementById('joinPassword').value.trim();
    
    if (!roomId || !username) {
        showAlert('Por favor, preencha código da sala e seu nome!', 'warning');
        return;
    }
    
    // Desabilitar botão durante o envio
    const submitBtn = document.querySelector('#joinRoomForm button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Entrando...';
    
    // Verificar se a sala existe e se a senha está correta
    fetch(`/api/rooms/${roomId}/join`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            password: password
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showAlert(data.error, 'danger');
        } else {
            // Redirecionar para a sala
            window.location.href = `/chat/${roomId}?username=${encodeURIComponent(username)}`;
        }
    })
    .catch(error => {
        showAlert('Erro ao entrar na sala!', 'danger');
        console.error('Erro:', error);
    })
    .finally(() => {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
    });
}

function enterRoom(roomId, roomName, hasPassword) {
    const username = prompt(`Digite seu nome para entrar na sala "${roomName}":`);
    if (!username || username.trim() === '') return;
    
    if (hasPassword) {
        // Mostrar modal para senha
        document.getElementById('modalRoomId').value = roomId;
        document.getElementById('modalUsername').value = username.trim();
        document.getElementById('modalPassword').value = '';
        new bootstrap.Modal(document.getElementById('passwordModal')).show();
    } else {
        // Entrar diretamente
        window.location.href = `/chat/${roomId}?username=${encodeURIComponent(username.trim())}`;
    }
}

function submitPassword() {
    const roomId = document.getElementById('modalRoomId').value;
    const username = document.getElementById('modalUsername').value;
    const password = document.getElementById('modalPassword').value;
    
    fetch(`/api/rooms/${roomId}/join`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            password: password
        })
    })
    .then(response => response.json())
    .then(data => {
        const modal = bootstrap.Modal.getInstance(document.getElementById('passwordModal'));
        if (data.error) {
            showAlert(data.error, 'danger');
            document.getElementById('modalPassword').focus();
        } else {
            modal.hide();
            window.location.href = `/chat/${roomId}?username=${encodeURIComponent(username)}`;
        }
    })
    .catch(error => {
        showAlert('Erro ao verificar senha!', 'danger');
        console.error('Erro:', error);
    });
}

function formatDate(dateString) {
    if (!dateString) return 'Agora';
    try {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMins / 60);
        const diffDays = Math.floor(diffHours / 24);
        
        if (diffMins < 1) return 'Agora';
        if (diffMins < 60) return `${diffMins}min atrás`;
        if (diffHours < 24) return `${diffHours}h atrás`;
        if (diffDays < 7) return `${diffDays}d atrás`;
        
        return date.toLocaleDateString('pt-BR');
    } catch {
        return dateString;
    }
}

function showAlert(message, type) {
    // Remover alertas existentes
    const existingAlerts = document.querySelectorAll('.custom-alert');
    existingAlerts.forEach(alert => alert.remove());
    
    // Criar novo alerta
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show custom-alert position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px; max-width: 400px;';
    alertDiv.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas fa-${getAlertIcon(type)} me-2"></i>
            <div>${message}</div>
        </div>
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Remover automaticamente após 5 segundos
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

function getAlertIcon(type) {
    const icons = {
        'success': 'check-circle',
        'danger': 'exclamation-triangle',
        'warning': 'exclamation-circle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}