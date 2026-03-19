// Chatbot JavaScript - AI Campaign Detection System

class ChatbotManager {
    constructor() {
        this.messagesContainer = null;
        this.inputElement = null;
        this.sendButton = null;
        this.typingIndicator = null;
        this.isTyping = false;
        this.messageHistory = [];
        this.init();
    }

    init() {
        this.setupElements();
        this.setupEventListeners();
        this.loadChatHistory();
    }

    setupElements() {
        this.messagesContainer = document.getElementById('chatMessages');
        this.inputElement = document.getElementById('chatInput');
        this.sendButton = document.getElementById('sendButton');
        this.typingIndicator = document.getElementById('typingIndicator');
    }

    setupEventListeners() {
        // Send button click
        if (this.sendButton) {
            this.sendButton.addEventListener('click', () => this.sendMessage());
        }

        // Enter key to send message
        if (this.inputElement) {
            this.inputElement.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });

            // Auto-resize textarea and typing indicator
            this.inputElement.addEventListener('input', () => {
                this.adjustInputHeight();
            });
        }

        // Clear chat button
        const clearBtn = document.getElementById('clearChat');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearChat());
        }

        // Export chat button
        const exportBtn = document.getElementById('exportChat');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportChat());
        }
    }

    async sendMessage() {
        const message = this.inputElement?.value.trim();
        if (!message || this.isTyping) return;

        // Add user message to chat
        this.addMessage(message, 'user');
        this.inputElement.value = '';
        this.adjustInputHeight();

        // Show typing indicator
        this.showTyping();

        try {
            // Send message to backend
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message })
            });

            if (!response.ok) throw new Error('Failed to get response');

            const data = await response.json();
            
            // Simulate typing delay for better UX
            await this.sleep(1000 + Math.random() * 2000);
            
            this.hideTyping();
            this.addMessage(data.response || 'Sorry, I couldn\'t process that request.', 'bot');
            
        } catch (error) {
            console.error('Chat error:', error);
            this.hideTyping();
            this.addMessage('Sorry, I\'m having trouble responding right now. Please try again later.', 'bot');
        }
    }

    addMessage(content, sender = 'bot', timestamp = new Date()) {
        if (!this.messagesContainer) return;

        const messageElement = document.createElement('div');
        messageElement.className = `message ${sender}-message`;
        
        const timeStr = this.formatTime(timestamp);
        
        messageElement.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-${sender === 'user' ? 'user' : 'robot'}"></i>
            </div>
            <div class="message-content">
                <div class="message-bubble">
                    ${this.formatMessageContent(content)}
                </div>
                <div class="message-time">${timeStr}</div>
            </div>
        `;

        // Add message with animation
        messageElement.style.opacity = '0';
        messageElement.style.transform = 'translateY(20px)';
        this.messagesContainer.appendChild(messageElement);

        // Trigger animation
        requestAnimationFrame(() => {
            messageElement.style.transition = 'all 0.3s ease-out';
            messageElement.style.opacity = '1';
            messageElement.style.transform = 'translateY(0)';
        });

        // Store in history
        this.messageHistory.push({
            content,
            sender,
            timestamp: timestamp.toISOString()
        });

        // Auto-scroll to bottom
        this.scrollToBottom();
        
        // Save to localStorage
        this.saveChatHistory();
    }

    formatMessageContent(content) {
        // Convert line breaks to HTML
        content = content.replace(/\n/g, '<br>');
        
        // Format lists
        content = content.replace(/^\* (.+)$/gm, '<li>$1</li>');
        content = content.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
        
        // Format bold text
        content = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Format code blocks
        content = content.replace(/`([^`]+)`/g, '<code>$1</code>');
        
        return content;
    }

    formatTime(date) {
        const now = new Date();
        const diff = now.getTime() - date.getTime();
        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);

        if (days > 0) return `${days}d ago`;
        if (hours > 0) return `${hours}h ago`;
        if (minutes > 0) return `${minutes}m ago`;
        return 'Just now';
    }

    showTyping() {
        this.isTyping = true;
        if (this.typingIndicator) {
            this.typingIndicator.style.display = 'flex';
        }
        this.scrollToBottom();
    }

    hideTyping() {
        this.isTyping = false;
        if (this.typingIndicator) {
            this.typingIndicator.style.display = 'none';
        }
    }

    scrollToBottom() {
        if (this.messagesContainer) {
            setTimeout(() => {
                this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
            }, 100);
        }
    }

    adjustInputHeight() {
        if (!this.inputElement) return;
        
        this.inputElement.style.height = 'auto';
        this.inputElement.style.height = Math.min(this.inputElement.scrollHeight, 120) + 'px';
    }

    clearChat() {
        if (confirm('Are you sure you want to clear the chat history?')) {
            if (this.messagesContainer) {
                // Keep only the welcome message
                const welcomeMessage = this.messagesContainer.querySelector('.bot-message');
                this.messagesContainer.innerHTML = '';
                if (welcomeMessage) {
                    this.messagesContainer.appendChild(welcomeMessage);
                }
            }
            
            this.messageHistory = [];
            this.saveChatHistory();
            this.showAlert('Chat history cleared', 'info');
        }
    }

    exportChat() {
        if (this.messageHistory.length === 0) {
            this.showAlert('No chat history to export', 'warning');
            return;
        }

        try {
            const chatData = {
                exported_at: new Date().toISOString(),
                messages: this.messageHistory
            };

            const dataStr = JSON.stringify(chatData, null, 2);
            const dataBlob = new Blob([dataStr], { type: 'application/json' });
            
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `chat-history-${new Date().toISOString().split('T')[0]}.json`;
            
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            URL.revokeObjectURL(url);
            this.showAlert('Chat history exported successfully!', 'success');
        } catch (error) {
            console.error('Export error:', error);
            this.showAlert('Failed to export chat history', 'error');
        }
    }

    saveChatHistory() {
        try {
            localStorage.setItem('chat_history', JSON.stringify(this.messageHistory));
        } catch (error) {
            console.error('Failed to save chat history:', error);
        }
    }

    loadChatHistory() {
        try {
            const saved = localStorage.getItem('chat_history');
            if (saved) {
                this.messageHistory = JSON.parse(saved);
                
                // Restore messages (skip welcome message)
                this.messageHistory.forEach(msg => {
                    if (msg.sender !== 'welcome') {
                        this.addMessageWithoutSaving(msg.content, msg.sender, new Date(msg.timestamp));
                    }
                });
            }
        } catch (error) {
            console.error('Failed to load chat history:', error);
        }
    }

    addMessageWithoutSaving(content, sender, timestamp) {
        if (!this.messagesContainer) return;

        const messageElement = document.createElement('div');
        messageElement.className = `message ${sender}-message`;
        
        const timeStr = this.formatTime(timestamp);
        
        messageElement.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-${sender === 'user' ? 'user' : 'robot'}"></i>
            </div>
            <div class="message-content">
                <div class="message-bubble">
                    ${this.formatMessageContent(content)}
                </div>
                <div class="message-time">${timeStr}</div>
            </div>
        `;

        this.messagesContainer.appendChild(messageElement);
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    showAlert(message, type = 'info') {
        // Use the global alert function from base.html
        if (typeof showAlert === 'function') {
            showAlert(message, type);
        } else {
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }
}

// Quick action functions
window.sendQuickMessage = function(message) {
    const chatbot = window.chatbotManager;
    if (chatbot && chatbot.inputElement) {
        chatbot.inputElement.value = message;
        chatbot.sendMessage();
    }
};

window.useSuggestion = function(suggestion) {
    const chatbot = window.chatbotManager;
    if (chatbot && chatbot.inputElement) {
        chatbot.inputElement.value = suggestion;
        chatbot.inputElement.focus();
        chatbot.adjustInputHeight();
    }
};

// Predefined responses for better UX
const quickResponses = {
    'summarize propaganda activity': 'Based on recent analysis, I\'ve detected several propaganda patterns including coordinated messaging, emotional manipulation, and false narratives targeting India\'s democratic institutions.',
    'threat level': 'Current threat level is MEDIUM. Detected coordinated activities across 3 platforms with similar messaging patterns. Recommend continued monitoring and fact-checking initiatives.',
    'sentiment trends': 'Current sentiment analysis shows 45% negative, 30% positive, and 25% neutral posts in the analyzed content. There\'s a notable increase in negative sentiment during coordinated campaigns.',
    '24 hours': 'In the last 24 hours: Analyzed 150 posts across platforms, detected 23% propaganda content, identified 34 suspicious posts with coordinated messaging patterns.',
    'platform performance': 'Platform analysis shows Twitter with highest activity (156 posts), Reddit with moderate engagement (89 posts), and News sources with 34 articles. Twitter shows highest coordination patterns.'
};

// Enhanced message processing
function getQuickResponse(message) {
    const lowerMessage = message.toLowerCase();
    
    for (const [key, response] of Object.entries(quickResponses)) {
        if (lowerMessage.includes(key)) {
            return response;
        }
    }
    
    return null;
}

// Initialize chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.chatbotManager = new ChatbotManager();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.chatbotManager) {
        window.chatbotManager.saveChatHistory();
    }
});

// Export for module usage (if needed)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChatbotManager;
}