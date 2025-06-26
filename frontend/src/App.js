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
                            <h3>👋 Welcome to the Multi-Agent System!</h3>
                            <p>This system uses:</p>
                            <ul>
                                <li><strong>Orchestrator Agent:</strong> Coordinates and manages requests</li>
                                <li><strong>QnA Agent:</strong> Answers questions and provides information</li>
                            </ul>
                            <p>Ask me anything to get started!</p>
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
                        <input
                            type="text"
                            value={inputMessage}
                            onChange={(e) => setInputMessage(e.target.value)}
                            placeholder="Type your message here..."
                            disabled={isLoading}
                            className="message-input"
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
