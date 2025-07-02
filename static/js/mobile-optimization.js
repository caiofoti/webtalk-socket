// Mobile-specific optimizations and PWA functionality

document.addEventListener('DOMContentLoaded', function() {
    // Detect mobile device com mais precisão
    const isMobile = window.innerWidth <= 768;
    const userAgent = navigator.userAgent.toLowerCase();
    const isMobileUA = /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(userAgent);
    
    console.log(`[MOBILE DEBUG] Width: ${window.innerWidth}, isMobile: ${isMobile}, UserAgent Mobile: ${isMobileUA}`);
    
    if (isMobile) {
        // Add mobile class to body
        document.body.classList.add('mobile-device');
        
        // Debug visual para confirmar modo mobile
        if (window.location.search.includes('debug=mobile')) {
            document.body.classList.add('debug-mobile');
        }
        
        // Optimize touch interactions
        document.body.addEventListener('touchstart', function() {}, {passive: true});
        
        // Prevent zoom on double tap
        let lastTouchEnd = 0;
        document.addEventListener('touchend', function (event) {
            const now = (new Date()).getTime();
            if (now - lastTouchEnd <= 300) {
                event.preventDefault();
            }
            lastTouchEnd = now;
        }, false);
        
        // Set viewport height for mobile browsers
        const setVH = () => {
            let vh = window.innerHeight * 0.01;
            document.documentElement.style.setProperty('--vh', `${vh}px`);
        };
        setVH();
        window.addEventListener('resize', setVH);
        window.addEventListener('orientationchange', setVH);
        
        // Debug log para mobile
        console.log('[MOBILE] Optimizations applied');
        
        // Verificar se existem elementos mobile após carregamento das salas
        setTimeout(() => {
            const mobileContainer = document.querySelector('.mobile-rooms-container');
            const table = document.querySelector('.rooms-table');
            
            console.log(`[MOBILE DEBUG] Mobile container exists: ${!!mobileContainer}`);
            console.log(`[MOBILE DEBUG] Table display: ${table ? table.style.display : 'not found'}`);
            
            if (mobileContainer) {
                console.log(`[MOBILE DEBUG] Mobile container children: ${mobileContainer.children.length}`);
            }
        }, 2000);
    }
    
    // PWA installation
    initializePWA();
    
    // Accessibility improvements
    initializeAccessibility();
});

// PWA Installation functionality
function initializePWA() {
    let deferredPrompt;
    
    // Listen for the beforeinstallprompt event
    window.addEventListener('beforeinstallprompt', (e) => {
        // Prevent the mini-infobar from appearing on mobile
        e.preventDefault();
        // Stash the event so it can be triggered later
        deferredPrompt = e;
        // Show install button
        showInstallButton();
    });
    
    // Show install button
    function showInstallButton() {
        const installButton = document.createElement('button');
        installButton.className = 'pwa-install-button';
        installButton.innerHTML = '<i class="fas fa-download me-2"></i>Instalar App';
        installButton.setAttribute('aria-label', 'Instalar aplicativo');
        installButton.title = 'Instalar WebTalk Socket como aplicativo';
        
        installButton.addEventListener('click', async () => {
            if (deferredPrompt) {
                // Show the install prompt
                deferredPrompt.prompt();
                // Wait for the user to respond to the prompt
                const { outcome } = await deferredPrompt.userChoice;
                console.log(`PWA install prompt outcome: ${outcome}`);
                // Clear the deferredPrompt variable
                deferredPrompt = null;
                // Hide the install button
                installButton.remove();
            }
        });
        
        document.body.appendChild(installButton);
        
        // Show with animation
        setTimeout(() => {
            installButton.classList.add('show');
        }, 1000);
        
        // Auto-hide after 10 seconds
        setTimeout(() => {
            if (installButton.parentNode) {
                installButton.classList.remove('show');
                setTimeout(() => {
                    if (installButton.parentNode) {
                        installButton.remove();
                    }
                }, 300);
            }
        }, 10000);
    }
    
    // Listen for app installed event
    window.addEventListener('appinstalled', (evt) => {
        console.log('PWA was installed successfully');
        // Hide install button if still visible
        const installButton = document.querySelector('.pwa-install-button');
        if (installButton) {
            installButton.remove();
        }
    });
    
    // Check if app is already installed
    if (window.matchMedia('(display-mode: standalone)').matches) {
        console.log('PWA is running in standalone mode');
        document.body.classList.add('pwa-installed');
    }
}

// Accessibility improvements
function initializeAccessibility() {
    // Add skip to content link
    const skipLink = document.createElement('a');
    skipLink.href = '#main-content';
    skipLink.className = 'sr-only sr-only-focusable';
    skipLink.textContent = 'Pular para conteúdo principal';
    skipLink.style.cssText = `
        position: absolute;
        top: -40px;
        left: 6px;
        z-index: 9999;
        color: white;
        background: var(--primary-color);
        padding: 8px 16px;
        text-decoration: none;
        border-radius: 4px;
        transition: top 0.3s;
    `;
    
    skipLink.addEventListener('focus', function() {
        this.style.top = '6px';
    });
    
    skipLink.addEventListener('blur', function() {
        this.style.top = '-40px';
    });
    
    document.body.insertBefore(skipLink, document.body.firstChild);
    
    // Add main content ID for skip link
    const mainContent = document.querySelector('main');
    if (mainContent && !mainContent.id) {
        mainContent.id = 'main-content';
    }
    
    // Improve keyboard navigation
    document.addEventListener('keydown', function(e) {
        // Escape key to close modals
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal.show');
            if (openModal) {
                const modal = bootstrap.Modal.getInstance(openModal);
                if (modal) {
                    modal.hide();
                }
            }
        }
    });
    
    // Focus trap for modals
    document.addEventListener('shown.bs.modal', function(e) {
        const modal = e.target;
        const focusableElements = modal.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        
        if (focusableElements.length > 0) {
            focusableElements[0].focus();
        }
    });
}

// Network status monitoring
function initializeNetworkMonitoring() {
    function updateNetworkStatus() {
        const isOnline = navigator.onLine;
        document.body.classList.toggle('offline', !isOnline);
        
        if (!isOnline) {
            showNetworkAlert('Você está offline. Algumas funcionalidades podem não estar disponíveis.', 'warning');
        } else {
            showNetworkAlert('Conexão restabelecida!', 'success');
        }
    }
    
    window.addEventListener('online', updateNetworkStatus);
    window.addEventListener('offline', updateNetworkStatus);
    
    // Initial check
    updateNetworkStatus();
}

// Show network status alerts
function showNetworkAlert(message, type) {
    // Remove existing network alerts
    const existingAlerts = document.querySelectorAll('.network-alert');
    existingAlerts.forEach(alert => alert.remove());
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible network-alert position-fixed`;
    alert.style.cssText = 'top: 20px; left: 20px; right: 20px; z-index: 9999; max-width: 500px; margin: 0 auto;';
    alert.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas fa-${type === 'warning' ? 'wifi' : 'check-circle'} me-2"></i>
            <div>${message}</div>
        </div>
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Fechar"></button>
    `;
    
    document.body.appendChild(alert);
    
    // Auto-remove after 3 seconds for success messages
    if (type === 'success') {
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 3000);
    }
}

// Initialize network monitoring
initializeNetworkMonitoring();

// Performance monitoring
if ('performance' in window) {
    window.addEventListener('load', function() {
        setTimeout(function() {
            const perfData = performance.getEntriesByType('navigation')[0];
            if (perfData) {
                console.log(`Page load time: ${perfData.loadEventEnd - perfData.loadEventStart}ms`);
                console.log(`DOM content loaded: ${perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart}ms`);
            }
        }, 0);
    });
}
