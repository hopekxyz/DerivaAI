// Elementos do DOM
const chatForm = document.getElementById('chatForm');
const chatInput = document.getElementById('chatInput');
const messagesContainer = document.getElementById('messagesContainer');

let isTyping = false;

document.addEventListener('DOMContentLoaded', function() {
    initializeChat();
    setupEventListeners();
});

function setupEventListeners() {
    chatForm.addEventListener('submit', handleChatSubmit);
    chatInput.addEventListener('keydown', handleInputKeydown);
    chatInput.addEventListener('input', handleInputChange);
    chatInput.focus();
}

function initializeChat() {
    scrollToBottom();
    setTimeout(() => {
        const firstMessage = document.querySelector('.ai-message');
        if (firstMessage) {
            firstMessage.style.opacity = '1';
            firstMessage.style.transform = 'translateY(0)';
        }
    }, 100);
}

function handleChatSubmit(e) {
    e.preventDefault();
    const message = chatInput.value.trim();
    if (!message || isTyping) return;
    addUserMessage(message);
    chatInput.value = '';
    simulateAIResponse(message);
}

function handleInputKeydown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        chatForm.dispatchEvent(new Event('submit'));
    }
}

function handleInputChange(e) {
    const inputWrapper = document.querySelector('.input-wrapper');
    if (e.target.value.trim()) {
        inputWrapper.classList.add('has-content');
    } else {
        inputWrapper.classList.remove('has-content');
    }
}

function addUserMessage(message) {
    const messageElement = createMessageElement('user', message);
    messagesContainer.appendChild(messageElement);
    setTimeout(() => {
        messageElement.style.opacity = '1';
        messageElement.style.transform = 'translateY(0)';
    }, 10);
    scrollToBottom();
}

function addAIMessage(message) {
    const messageElement = createMessageElement('ai', message);
    messagesContainer.appendChild(messageElement);
    setTimeout(() => {
        messageElement.style.opacity = '1';
        messageElement.style.transform = 'translateY(0)';
    }, 10);
    scrollToBottom();
}

function createMessageElement(type, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    messageDiv.style.opacity = '0';
    messageDiv.style.transform = 'translateY(10px)';
    messageDiv.style.transition = 'all 0.3s ease';

    if (type === 'ai') {
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        const symbol = document.createElement('span');
        symbol.className = 'derivative-symbol';
        symbol.textContent = '∂';
        avatar.appendChild(symbol);
        messageDiv.appendChild(avatar);
    }

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    const paragraph = document.createElement('p');
    paragraph.textContent = content;
    contentDiv.appendChild(paragraph);
    messageDiv.appendChild(contentDiv);
    return messageDiv;
}

function simulateAIResponse(userMessage) {
    isTyping = true;
    showTypingIndicator();
    setTimeout(() => {
        hideTypingIndicator();
        const response = generateAIResponse(userMessage);
        addAIMessage(response);
        isTyping = false;
    }, 1500 + Math.random() * 1000);
}

function showTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message ai-message typing-indicator-message';
    typingDiv.id = 'typing-indicator';
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    const symbol = document.createElement('span');
    symbol.className = 'derivative-symbol';
    symbol.textContent = '∂';
    avatar.appendChild(symbol);
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content typing-indicator';
    for (let i = 0; i < 3; i++) {
        const dot = document.createElement('div');
        dot.className = 'typing-dot';
        contentDiv.appendChild(dot);
    }
    typingDiv.appendChild(avatar);
    typingDiv.appendChild(contentDiv);
    messagesContainer.appendChild(typingDiv);
    scrollToBottom();
}

function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

function generateAIResponse(userMessage) {
    const responses = [
        "Entendo sua pergunta sobre cálculo. Vou te ajudar a entender esse conceito de forma clara e simples.",
        "Excelente pergunta! Vamos analisar isso passo a passo para que você compreenda completamente.",
        "Essa é uma dúvida muito comum em cálculo. Deixe-me explicar de uma forma que você vai entender facilmente.",
        "Perfeito! Vou te mostrar como resolver isso usando uma abordagem intuitiva e prática.",
        "Ótima questão! Isso envolve conceitos fundamentais de cálculo que vou explicar de forma didática."
    ];
    const lowerMessage = userMessage.toLowerCase();
    if (lowerMessage.includes('derivada') || lowerMessage.includes('derivar')) {
        return "Para calcular a derivada, precisamos entender a taxa de variação da função. Vou te mostrar o processo passo a passo.";
    } else if (lowerMessage.includes('integral') || lowerMessage.includes('integrar')) {
        return "A integral é o processo inverso da derivada. Vamos ver como encontrar a área sob a curva.";
    } else if (lowerMessage.includes('limite') || lowerMessage.includes('lim')) {
        return "Limites são fundamentais no cálculo. Vamos analisar o comportamento da função quando x se aproxima de um valor.";
    } else if (lowerMessage.includes('regra') || lowerMessage.includes('regras')) {
        return "As regras de derivação e integração são essenciais. Vou te mostrar as principais e como aplicá-las.";
    } else {
        return responses[Math.floor(Math.random() * responses.length)];
    }
}

function scrollToBottom() {
    setTimeout(() => {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }, 100);
} 