// Funções de navegação e interação
document.addEventListener('DOMContentLoaded', function() {
    // Navegação suave
    setupSmoothNavigation();
    
    // Menu mobile
    setupMobileMenu();
    
    // Chat interativo
    setupChat();
    
    // Formulário de contato
    setupContactForm();
    
    // Animações de scroll
    setupScrollAnimations();
    
    // Header com scroll
    setupHeaderScroll();
});

// Navegação suave
function setupSmoothNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            
            if (targetSection) {
                const headerHeight = document.querySelector('.header').offsetHeight;
                const targetPosition = targetSection.offsetTop - headerHeight;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// Função global para scroll
function scrollToSection(sectionId) {
    const targetSection = document.querySelector(`#${sectionId}`);
    if (targetSection) {
        const headerHeight = document.querySelector('.header').offsetHeight;
        const targetPosition = targetSection.offsetTop - headerHeight;
        
        window.scrollTo({
            top: targetPosition,
            behavior: 'smooth'
        });
    }
}

// Menu mobile
function setupMobileMenu() {
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu = document.querySelector('.nav-menu');
    
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            navToggle.classList.toggle('active');
        });
        
        // Fechar menu ao clicar em um link
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                navMenu.classList.remove('active');
                navToggle.classList.remove('active');
            });
        });
    }
}

// Chat interativo
function setupChat() {
    const chatForm = document.getElementById('chatForm');
    const chatInput = document.getElementById('chatInput');
    const chatMessages = document.getElementById('chatMessages');
    
    if (chatForm && chatInput && chatMessages) {
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const userMessage = chatInput.value.trim();
            if (!userMessage) return;
            
            // Adicionar mensagem do usuário
            addMessage(userMessage, 'user');
            
            // Limpar input
            chatInput.value = '';
            
            // Simular resposta do bot
            setTimeout(() => {
                const botResponse = generateBotResponse(userMessage);
                addMessage(botResponse, 'bot');
            }, 1000);
        });
        
        // Permitir envio com Enter
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                chatForm.dispatchEvent(new Event('submit'));
            }
        });
    }
}

// Adicionar mensagem ao chat
function addMessage(content, sender) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    
    const icon = document.createElement('i');
    icon.className = sender === 'bot' ? 'fas fa-robot' : 'fas fa-user';
    avatar.appendChild(icon);
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    // Formatar conteúdo com fórmulas matemáticas
    const formattedContent = formatMathContent(content);
    messageContent.innerHTML = formattedContent;
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(messageContent);
    
    chatMessages.appendChild(messageDiv);
    
    // Scroll para a última mensagem
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Formatar conteúdo matemático
function formatMathContent(content) {
    // Substituir símbolos matemáticos básicos
    let formatted = content
        .replace(/\*/g, '×')
        .replace(/\//g, '÷')
        .replace(/\^/g, '<sup>')
        .replace(/(\d+)/g, '<span class="math-number">$1</span>')
        .replace(/dx/g, '<span class="math-symbol">dx</span>')
        .replace(/dy/g, '<span class="math-symbol">dy</span>')
        .replace(/dz/g, '<span class="math-symbol">dz</span>')
        .replace(/∫/g, '<span class="math-symbol">∫</span>')
        .replace(/∂/g, '<span class="math-symbol">∂</span>')
        .replace(/∞/g, '<span class="math-symbol">∞</span>')
        .replace(/π/g, '<span class="math-symbol">π</span>')
        .replace(/θ/g, '<span class="math-symbol">θ</span>')
        .replace(/α/g, '<span class="math-symbol">α</span>')
        .replace(/β/g, '<span class="math-symbol">β</span>')
        .replace(/γ/g, '<span class="math-symbol">γ</span>')
        .replace(/δ/g, '<span class="math-symbol">δ</span>')
        .replace(/ε/g, '<span class="math-symbol">ε</span>')
        .replace(/lim/g, '<span class="math-function">lim</span>')
        .replace(/sin/g, '<span class="math-function">sin</span>')
        .replace(/cos/g, '<span class="math-function">cos</span>')
        .replace(/tan/g, '<span class="math-function">tan</span>')
        .replace(/log/g, '<span class="math-function">log</span>')
        .replace(/ln/g, '<span class="math-function">ln</span>');
    
    return formatted;
}

// Gerar resposta do bot
function generateBotResponse(userMessage) {
    const message = userMessage.toLowerCase();
    
    // Respostas baseadas em palavras-chave
    if (message.includes('derivada') || message.includes('derivar')) {
        return `Ótima pergunta! A derivada é uma das ferramentas mais importantes do cálculo. Ela mede a taxa de variação instantânea de uma função. Por exemplo, se f(x) = x², então f'(x) = 2x. Quer que eu explique mais sobre derivadas? 📈`;
    }
    
    if (message.includes('integral') || message.includes('integrar')) {
        return `A integral é o processo inverso da derivada! Ela calcula a área sob uma curva. Por exemplo, ∫x dx = x²/2 + C. É como "desfazer" a derivada. Quer ver mais exemplos? 📊`;
    }
    
    if (message.includes('limite') || message.includes('lim')) {
        return `Limites são fundamentais no cálculo! Eles nos ajudam a entender o comportamento de uma função quando x se aproxima de um valor específico. Por exemplo, lim(x→0) sin(x)/x = 1. Fascinante, não é? 🔍`;
    }
    
    if (message.includes('regra da cadeia') || message.includes('chain rule')) {
        return `A regra da cadeia é essencial! Se f(x) = g(h(x)), então f'(x) = g'(h(x)) × h'(x). É como desmontar uma função composta. Quer um exemplo prático? 🔗`;
    }
    
    if (message.includes('teorema fundamental') || message.includes('fundamental')) {
        return `O Teorema Fundamental do Cálculo conecta derivadas e integrais! Ele diz que ∫[a,b] f'(x) dx = f(b) - f(a). É a ponte entre os dois conceitos principais. Incrível, né? 🌉`;
    }
    
    if (message.includes('ajuda') || message.includes('help')) {
        return `Claro! Posso te ajudar com: derivadas, integrais, limites, regras de derivação, aplicações do cálculo, e muito mais. Só me pergunte! 🤓`;
    }
    
    if (message.includes('olá') || message.includes('oi') || message.includes('hello')) {
        return `Olá! 👋 Que bom ter você aqui! Sou o DerivaAI, seu tutor de cálculo. Como posso te ajudar hoje? Pode me perguntar sobre qualquer conceito de cálculo! 📚`;
    }
    
    // Resposta padrão
    const defaultResponses = [
        `Interessante! Vou te ajudar com isso. Pode me dar mais detalhes sobre o que você quer saber? 🤔`,
        `Ótima pergunta! Deixe-me explicar isso de forma simples... 📝`,
        `Essa é uma dúvida muito comum! Vou te ajudar a entender melhor. 💡`,
        `Perfeito! Vou te explicar isso passo a passo. 🎯`,
        `Que pergunta interessante! Deixe-me quebrar isso em partes menores para você entender melhor. 🔍`
    ];
    
    return defaultResponses[Math.floor(Math.random() * defaultResponses.length)];
}

// Formulário de contato
function setupContactForm() {
    const contactForm = document.getElementById('contactForm');
    
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Simular envio do formulário
            const formData = new FormData(this);
            const data = Object.fromEntries(formData);
            
            // Mostrar mensagem de sucesso
            showNotification('Mensagem enviada com sucesso! Entraremos em contato em breve.', 'success');
            
            // Limpar formulário
            this.reset();
        });
    }
}

// Mostrar notificação
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Estilos da notificação
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 10000;
        animation: slideIn 0.3s ease;
        max-width: 400px;
    `;
    
    if (type === 'success') {
        notification.style.background = '#10b981';
    } else if (type === 'error') {
        notification.style.background = '#ef4444';
    } else {
        notification.style.background = '#3b82f6';
    }
    
    document.body.appendChild(notification);
    
    // Remover notificação após 5 segundos
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 5000);
}

// Animações de scroll
function setupScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Observar elementos para animação
    const animateElements = document.querySelectorAll('.feature-card, .about-feature, .stat');
    animateElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
}

// Header com scroll
function setupHeaderScroll() {
    let lastScrollTop = 0;
    const header = document.querySelector('.header');
    
    window.addEventListener('scroll', function() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        if (scrollTop > 100) {
            header.style.background = 'rgba(255, 255, 255, 0.98)';
            header.style.boxShadow = '0 2px 20px rgba(0, 0, 0, 0.1)';
        } else {
            header.style.background = 'rgba(255, 255, 255, 0.95)';
            header.style.boxShadow = 'none';
        }
        
        lastScrollTop = scrollTop;
    });
}

// Adicionar estilos CSS para animações
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    .math-number {
        color: #2563eb;
        font-weight: 600;
    }
    
    .math-symbol {
        color: #7c3aed;
        font-weight: 600;
    }
    
    .math-function {
        color: #059669;
        font-weight: 600;
        font-style: italic;
    }
    
    @media (max-width: 768px) {
        .nav-menu.active {
            display: flex;
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            flex-direction: column;
            padding: 1rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            border-top: 1px solid #e2e8f0;
        }
        
        .nav-toggle.active span:nth-child(1) {
            transform: rotate(45deg) translate(5px, 5px);
        }
        
        .nav-toggle.active span:nth-child(2) {
            opacity: 0;
        }
        
        .nav-toggle.active span:nth-child(3) {
            transform: rotate(-45deg) translate(7px, -6px);
        }
    }
`;

document.head.appendChild(style); 