// OS:Belgrade Chat Widget - Production Version with Markdown Support
// This version calls your deployed backend API

(function() {
    // ============ CONFIGURATION ============
    const CONFIG = {
        API_ENDPOINT: 'https://web-production-f8ee2.up.railway.app/api/chat',
    };

    // ============ STYLES ============
    const styles = `
        #doc-chat-widget { position: fixed; bottom: 20px; right: 20px; z-index: 9999; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; }
        #chat-button { width: 60px; height: 48px; border-radius: 12px; background: #ff4b33; border: none; cursor: pointer; box-shadow: 0 4px 12px rgba(255, 75, 51, 0.3); display: flex; align-items: center; justify-content: center; transition: transform 0.3s ease, box-shadow 0.3s ease; }
        #chat-button:hover { transform: scale(1.05); box-shadow: 0 6px 16px rgba(255, 75, 51, 0.4); }
        #chat-button svg { width: 30px; height: 30px; fill: white; }
        #chat-window { display: none; position: fixed; bottom: 90px; right: 20px; width: 380px; height: 550px; background: white; border-radius: 12px; box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2); flex-direction: column; overflow: hidden; }
        #chat-window.open { display: flex; }
        #chat-header { background: #ff4b33; color: white; padding: 16px 20px; display: flex; justify-content: space-between; align-items: center; }
        #chat-header h3 { margin: 0; font-size: 16px; font-weight: 600; }
        #close-chat { background: none; border: none; color: white; font-size: 24px; cursor: pointer; padding: 0; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; }
        #chat-messages { flex: 1; overflow-y: auto; padding: 20px; background: #f7f7f8; }
        .chat-message { margin-bottom: 16px; display: flex; gap: 10px; }
        .chat-message.user { flex-direction: row-reverse; }
        .message-content { max-width: 75%; padding: 12px 16px; border-radius: 12px; line-height: 1.5; font-size: 14px; }
        .message-content strong { font-weight: 600; }
        .message-content h2 { font-size: 16px; font-weight: 600; margin: 12px 0 8px 0; }
        .message-content h3 { font-size: 14px; font-weight: 600; margin: 10px 0 6px 0; }
        .message-content ul, .message-content ol { margin: 8px 0; padding-left: 20px; }
        .message-content li { margin: 4px 0; }
        .message-content code { background: #f0f0f0; padding: 2px 6px; border-radius: 3px; font-family: monospace; font-size: 13px; }
        .chat-message.assistant .message-content { background: white; color: #333; border-bottom-left-radius: 4px; }
        .chat-message.user .message-content { background: #ff4b33; color: white; border-bottom-right-radius: 4px; }
        #chat-input-container { padding: 16px; background: white; border-top: 1px solid #e5e5e5; }
        #chat-input-form { display: flex; gap: 8px; }
        #chat-input { flex: 1; padding: 12px; border: 1px solid #e5e5e5; border-radius: 8px; font-size: 14px; font-family: inherit; outline: none; }
        #chat-input:focus { border-color: #ff4b33; }
        #send-button { padding: 12px 20px; background: #ff4b33; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; font-size: 14px; transition: opacity 0.3s ease; }
        #send-button:hover:not(:disabled) { opacity: 0.9; }
        #send-button:disabled { opacity: 0.6; cursor: not-allowed; }
        .typing-indicator { display: flex; gap: 4px; padding: 12px 16px; background: white; border-radius: 12px; width: fit-content; }
        .typing-indicator span { width: 8px; height: 8px; background: #ff4b33; border-radius: 50%; animation: typing 1.4s infinite; }
        .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
        .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes typing { 0%, 60%, 100% { transform: translateY(0); opacity: 0.7; } 30% { transform: translateY(-10px); opacity: 1; } }
        @media (max-width: 480px) { #chat-window { width: calc(100vw - 40px); height: calc(100vh - 120px); } }
    `;

    // ============ HTML STRUCTURE ============
    const widgetHTML = `
        <div id="doc-chat-widget">
            <button id="chat-button" aria-label="Open chat">
                <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/>
                </svg>
            </button>
            <div id="chat-window">
                <div id="chat-header">
                    <h3>OS:Belgrade Assistant</h3>
                    <button id="close-chat" aria-label="Close chat">&times;</button>
                </div>
                <div id="chat-messages">
                    <div class="chat-message assistant">
                        <div class="message-content">Hi! I'm your OS:Belgrade documentation assistant. I can help you with:

• Project setup and structure
• Technical documentation
• UI customization
• API generation
• Troubleshooting

What would you like to know?</div>
                    </div>
                </div>
                <div id="chat-input-container">
                    <form id="chat-input-form">
                        <input type="text" id="chat-input" placeholder="Ask about the docs..." autocomplete="off"/>
                        <button type="submit" id="send-button">Send</button>
                    </form>
                </div>
            </div>
        </div>
    `;

    // ============ MARKDOWN PARSER ============
    function parseMarkdown(text) {
        // Convert markdown to HTML
        let html = text;
        
        // Headers
        html = html.replace(/^## (.*$)/gm, '<h2>$1</h2>');
        html = html.replace(/^### (.*$)/gm, '<h3>$1</h3>');
        
        // Bold
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Lists
        html = html.replace(/^\- (.*$)/gm, '<li>$1</li>');
        html = html.replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>');
        
        // Line breaks
        html = html.replace(/\n\n/g, '<br><br>');
        
        return html;
    }

    // ============ INITIALIZATION ============
    function init() {
        const styleEl = document.createElement('style');
        styleEl.textContent = styles;
        document.head.appendChild(styleEl);

        const widgetContainer = document.createElement('div');
        widgetContainer.innerHTML = widgetHTML;
        document.body.appendChild(widgetContainer);

        setupEventListeners();
    }

    // ============ CONVERSATION STATE ============
    let conversationHistory = [];

    // ============ EVENT LISTENERS ============
    function setupEventListeners() {
        const chatButton = document.getElementById('chat-button');
        const chatWindow = document.getElementById('chat-window');
        const closeChat = document.getElementById('close-chat');
        const chatForm = document.getElementById('chat-input-form');
        const chatInput = document.getElementById('chat-input');

        chatButton.addEventListener('click', () => {
            chatWindow.classList.add('open');
            chatInput.focus();
        });

        closeChat.addEventListener('click', () => {
            chatWindow.classList.remove('open');
        });

        chatForm.addEventListener('submit', handleSubmit);
    }

    // ============ MESSAGE HANDLING ============
    async function handleSubmit(e) {
        e.preventDefault();
        
        const chatInput = document.getElementById('chat-input');
        const sendButton = document.getElementById('send-button');
        const message = chatInput.value.trim();
        
        if (!message) return;

        addMessage('user', message);
        chatInput.value = '';
        
        const typingIndicator = addTypingIndicator();
        chatInput.disabled = true;
        sendButton.disabled = true;

        try {
            const response = await fetch(CONFIG.API_ENDPOINT, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    conversationHistory: conversationHistory
                })
            });

            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }

            const data = await response.json();
            typingIndicator.remove();
            
            if (data.content && data.content[0]) {
                addMessage('assistant', data.content[0].text);
            } else if (data.error) {
                addMessage('assistant', 'Sorry, I encountered an error. Please try again.');
            }
        } catch (error) {
            typingIndicator.remove();
            addMessage('assistant', 'Sorry, I encountered an error connecting to the server.');
            console.error('Chat error:', error);
        } finally {
            chatInput.disabled = false;
            sendButton.disabled = false;
            chatInput.focus();
        }
    }

    function addMessage(role, content) {
        const chatMessages = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${role}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // Parse markdown for assistant messages
        if (role === 'assistant') {
            contentDiv.innerHTML = parseMarkdown(content);
        } else {
            contentDiv.textContent = content;
        }
        
        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        conversationHistory.push({ role, content });
    }

    function addTypingIndicator() {
        const chatMessages = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chat-message assistant';
        
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        typingDiv.innerHTML = '<span></span><span></span><span></span>';
        
        messageDiv.appendChild(typingDiv);
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        return messageDiv;
    }

    // ============ START ============
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
