import React, { useState, useRef, useEffect } from 'react';
import type { Message, Product } from '../types';
import { MessageBubble } from './MessageBubble';
import { Send, ShoppingBag } from 'lucide-react';
import { sendChat } from '../api';

interface ChatInterfaceProps {
    messages: Message[];
    setMessages: React.Dispatch<React.SetStateAction<Message[]>>;
    onAddToCart: (product: Product) => void;
    onToggleSave: (product: Product) => void;
    checkIsSaved: (id: string) => boolean;
    onChatUpdate: () => void;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({ messages, setMessages, onAddToCart, onToggleSave, checkIsSaved, onChatUpdate }) => {
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim() || isLoading) return;

        const userMsg: Message = { role: 'user', content: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setIsLoading(true);

        try {
            // Exclude system message from API call as backend adds it
            const history = messages.filter(m => m.role !== 'system');

            // Call API
            const response = await sendChat(input, history);

            // Backend returns { role, content, tool_calls }
            // If the content is empty but tool_calls exist, we might want to show something?
            // But my backend loop handles tools and returns FINAL response.

            const agentMsg: Message = {
                role: 'assistant',
                content: response.content
            };

            setMessages(prev => [...prev, agentMsg]);

            // Trigger cart update (wait a bit to ensure backend tool exec is done - though await sendChat usually implies it)
            setTimeout(() => onChatUpdate(), 100);

        } catch (error) {
            console.error(error);
            setMessages(prev => [...prev, { role: 'assistant', content: "I'm sorry, I'm having trouble connecting to the store right now." }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-full bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-100">
            {/* Header */}
            <div className="bg-white p-4 border-b border-gray-100 flex items-center justify-between">
                <div>
                    <h2 className="font-semibold text-gray-900">Personal Shopper</h2>
                    <p className="text-xs text-gray-500">Always here to help you look your best.</p>
                </div>
                <div className="w-2 h-2 rounded-full bg-green-500"></div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 bg-prime-50">
                {messages.map((m, i) => (
                    <MessageBubble
                        key={i}
                        message={m}
                        onAddToCart={onAddToCart}
                        onToggleSave={onToggleSave}
                        checkIsSaved={checkIsSaved}
                    />
                ))}
                {isLoading && (
                    <div className="flex gap-4 mb-6">
                        <div className="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center">
                            <div className="w-2 h-2 bg-purple-600 rounded-full animate-bounce"></div>
                        </div>
                        <div className="text-gray-400 text-sm py-2">Browsing catalog...</div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="p-4 bg-white border-t border-gray-100">
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                        placeholder="I need an outfit for a summer wedding..."
                        className="flex-1 bg-gray-50 border-none rounded-xl px-4 py-3 focus:ring-2 focus:ring-purple-100 outline-none text-gray-800 placeholder-gray-400 font-light"
                        disabled={isLoading}
                    />
                    <button
                        onClick={handleSend}
                        disabled={isLoading}
                        className="bg-gray-900 text-white p-3 rounded-xl hover:bg-gray-800 transition-colors disabled:opacity-50"
                    >
                        <Send size={20} />
                    </button>
                </div>
            </div>
        </div>
    );
};
