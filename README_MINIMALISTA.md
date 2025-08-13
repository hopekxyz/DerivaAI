# DerivaAI - Interface Minimalista

## 🎨 Design Minimalista Dark Mode

Uma interface de chat AI ultra-limpa e moderna, inspirada no ChatGPT mas com design mais monocrômico e silencioso.

### 🎯 Características Principais

#### **Paleta de Cores**
- **Preto Profundo**: `#000000` - Fundo principal
- **Azul Marinho**: `#0A192F` - Elementos secundários
- **Azul Elétrico**: `#0074E0` - Destaques e interações
- **Azul Escuro**: `#162A47` - Bolhas de mensagem AI
- **Azul Mais Claro**: `#1E3A8A` - Bolhas de mensagem usuário
- **Azul Input**: `#001F3F` - Barra de entrada

#### **Layout**
1. **Sidebar Esquerda**: Painel vertical fino em preto fosco
   - Avatar do AI com símbolo de derivada parcial (∂)
   - Ícones sutis em azul (usuário, histórico, configurações)
   - Navegação minimalista

2. **Área Principal do Chat**: Fundo preto
   - Header com identidade do AI
   - Área de mensagens com scroll suave
   - Barra de input na parte inferior

3. **Identidade do AI**: 
   - Avatar minimalista com símbolo ∂
   - Nome "DerivaAI" no canto superior esquerdo
   - Glow azul sutil quando responde

4. **Barra de Input**: 
   - Alinhada na parte inferior
   - Fundo azul escuro com texto branco
   - Borda azul elétrica no foco
   - Botão de envio com hover effects

#### **Micro-interações**
- **Estados Quase Invisíveis**: Mudanças sutis de estado
- **Pulse no Input**: Efeito sutil ao enviar nova mensagem
- **Glow no Hover**: Brilho azul sutil nos elementos interativos
- **Animações Suaves**: Transições fluidas entre estados

### 🚀 Como Usar

1. **Abrir a Interface**:
   ```bash
   # Abra o arquivo no navegador
   chat_minimalista.html
   ```

2. **Funcionalidades**:
   - Digite suas perguntas sobre cálculo no campo de entrada
   - Pressione Enter ou clique no botão de envio
   - Veja as respostas do AI com animações suaves
   - Navegue pelas seções usando a sidebar

3. **Responsividade**:
   - Interface adaptável para dispositivos móveis
   - Sidebar colapsa em telas menores
   - Layout otimizado para diferentes tamanhos de tela

### 🎨 Estilo Visual

#### **Design Flat**
- Sem skeuomorfismo
- Gradientes apenas para estados interativos
- Bordas suaves e sombras sutis

#### **Tipografia**
- Fonte: Roboto (com fallbacks para SF Pro Display)
- Texto branco fino e legível
- Hierarquia visual clara

#### **Interações**
- Hover effects sutis
- Focus states com bordas azuis
- Animações de entrada para mensagens
- Indicador de digitação animado

### 📱 Responsividade

- **Desktop**: Layout completo com sidebar
- **Tablet**: Sidebar compacta
- **Mobile**: Sidebar oculta, layout otimizado

### 🔧 Personalização

As cores e estilos podem ser facilmente modificados no arquivo `chat_minimalista.css` através das variáveis CSS:

```css
:root {
    --deep-black: #000000;
    --navy-blue: #0A192F;
    --electric-blue: #0074E0;
    /* ... outras variáveis */
}
```

### 🎯 Inspiração

- **ChatGPT**: Base conceitual
- **Design Systems Modernos**: Flat design, minimalismo
- **UX Silenciosa**: Micro-interações sutis
- **Dark Mode Premium**: Paleta monocromática elegante

### 📄 Arquivos

- `chat_minimalista.html` - Estrutura HTML
- `chat_minimalista.css` - Estilos CSS
- `chat_minimalista.js` - Funcionalidades JavaScript

### 🎨 Resultado Final

Uma interface de chat AI que combina:
- **Simplicidade**: Design limpo e focado
- **Elegância**: Paleta de cores sofisticada
- **Funcionalidade**: UX intuitiva e responsiva
- **Performance**: Animações suaves e otimizadas

A interface oferece uma experiência de chat AI moderna e profissional, mantendo o foco no conteúdo e na interação com o DerivaAI. 