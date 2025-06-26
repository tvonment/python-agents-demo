import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
    const [messages, setMessages] = useState([]);
    const [inputMessage, setInputMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [threadId, setThreadId] = useState(null);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const sendMessage = async (e) => {
        e.preventDefault();

        if (!inputMessage.trim() || isLoading) return;

        const userMessage = inputMessage.trim();
        setInputMessage('');

        // Add user message to chat
        setMessages(prev => [...prev, { type: 'user', content: userMessage }]);
        setIsLoading(true);

        try {
            const response = await axios.post('/chat', {
                message: userMessage,
                thread_id: threadId
            });

            // Add agent response to chat
            setMessages(prev => [...prev, {
                type: 'agent',
                content: response.data.response
            }]);

            // Update thread ID for conversation continuity
            setThreadId(response.data.thread_id);

        } catch (error) {
            console.error('Error sending message:', error);
            setMessages(prev => [...prev, {
                type: 'error',
                content: 'Sorry, there was an error processing your message. Please try again.'
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    const clearChat = () => {
        setMessages([]);
        setThreadId(null);
    };

    return (
        <div className="App">
            <header className="App-header">
                <h1>🤖 Multi-Agent System</h1>
                <p>Powered by Semantic Kernel & Azure AI</p>
            </header>

            <main className="chat-container">
                <div className="chat-header">
                    <h2>Chat with AI Agents</h2>
                    <button onClick={clearChat} className="clear-btn">Clear Chat</button>
                </div>

                <div className="messages-container">
                    {messages.length === 0 && (
                        <div className="welcome-message">
                            <h3>🤖 Welcome to the Multi-Agent System!</h3>
                            <p>This intelligent system coordinates multiple specialized AI agents to provide comprehensive assistance:</p>
                            <div className="agents-grid">
                                <div className="agent-card">
                                    <span className="agent-icon">📧</span>
                                    <strong>Support Email Agent</strong>
                                    <p>Professional email responses for customer support</p>
                                </div>
                                <div className="agent-card">
                                    <span className="agent-icon">🌤️</span>
                                    <strong>Weather Agent</strong>
                                    <p>Real-time weather information for any location</p>
                                </div>
                                <div className="agent-card">
                                    <span className="agent-icon">🧠</span>
                                    <strong>AI Ethics Agent</strong>
                                    <p>AI ethics, bias, and human-AI relationships</p>
                                </div>
                                <div className="agent-card">
                                    <span className="agent-icon">💬</span>
                                    <strong>QnA Agent</strong>
                                    <p>Customer support and general information</p>
                                </div>
                                <div className="agent-card">
                                    <span className="agent-icon">🎯</span>
                                    <strong>Orchestrator</strong>
                                    <p>Intelligent routing and casual conversation</p>
                                </div>
                            </div>
                            <div className="prompt-library">
                                <h4>🚀 Try these example prompts:</h4>
                                <div className="prompt-buttons">
                                    <button className="prompt-btn" onClick={() => setInputMessage("Hello! How are you doing today?")}>
                                        👋 Casual Chat
                                    </button>
                                    <button className="prompt-btn" onClick={() => setInputMessage("How do I reset my password?")}>
                                        💬 Password Reset Help
                                    </button>
                                    <button className="prompt-btn" onClick={() => setInputMessage("From: john@company.com\nTo: support@example.com\nSubject: Billing Issue\n\nHi, I'm having trouble with my recent invoice. Can you help me understand the charges?")}>
                                        📧 Support Email
                                    </button>
                                    <button className="prompt-btn" onClick={() => setInputMessage("What are the ethical implications of AI dependency in healthcare?")}>
                                        🧠 AI Ethics in Healthcare
                                    </button>
                                    <button className="prompt-btn" onClick={() => setInputMessage("What's the weather like in Stockholm?")}>
                                        🌤️ Weather in Stockholm
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}

                    {messages.map((message, index) => (
                        <div key={index} className={`message ${message.type}`}>
                            <div className="message-header">
                                {message.type === 'user' && '👤 You'}
                                {message.type === 'agent' && '🤖 AI Assistant'}
                                {message.type === 'error' && '⚠️ Error'}
                            </div>
                            <div className="message-content">
                                {message.content}
                            </div>
                        </div>
                    ))}

                    {isLoading && (
                        <div className="message agent">
                            <div className="message-header">🤖 AI Assistant</div>
                            <div className="message-content loading">
                                <div className="typing-indicator">
                                    <span></span>
                                    <span></span>
                                    <span></span>
                                </div>
                                Thinking...
                            </div>
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>

                <form onSubmit={sendMessage} className="input-form">
                    <div className="input-container">
                        <textarea
                            value={inputMessage}
                            onChange={(e) => setInputMessage(e.target.value)}
                            placeholder="Type your message here... You can write longer messages, ask complex questions, or try the example prompts above!"
                            disabled={isLoading}
                            className="message-input"
                            rows="3"
                            onKeyDown={(e) => {
                                if (e.key === 'Enter' && !e.shiftKey) {
                                    e.preventDefault();
                                    sendMessage(e);
                                }
                            }}
                        />
                        <button
                            type="submit"
                            disabled={isLoading || !inputMessage.trim()}
                            className="send-btn"
                        >
                            {isLoading ? '⏳' : '📤'}
                        </button>
                    </div>
                </form>
            </main>
        </div>
    );
}

export default App;
