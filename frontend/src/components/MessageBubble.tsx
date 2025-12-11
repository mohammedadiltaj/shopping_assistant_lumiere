import React, { useMemo } from 'react';
import type { Message, Product } from '../types';
import { User, Sparkles } from 'lucide-react';
import { ProductCard } from './ProductCard';
import clsx from 'clsx';

interface MessageBubbleProps {
    message: Message;
    onAddToCart: (product: Product) => void;
    onToggleSave: (product: Product) => void;
    checkIsSaved: (id: string) => boolean;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message, onAddToCart, onToggleSave, checkIsSaved }) => {
    const isUser = message.role === 'user';

    // Attempt to parse JSON products if they appear in content (from tool output)
    // Or if the content is raw JSON array
    const parsedProducts = useMemo(() => {
        try {
            // Check if content is a JSON array of products (from search_products tool)
            if (message.role === 'assistant' || message.role === 'tool') {
                // Try to find a JSON block or just parse the whole string
                // Usually the agent might output text + JSON, or just text.
                // For now, let's assume if it LOOKS like JSON, we try to parse it.
                if (message.content.trim().startsWith('[') && message.content.trim().endsWith(']')) {
                    return JSON.parse(message.content) as Product[];
                }
            }
        } catch (e) {
            return null;
        }
        return null;
    }, [message.content, message.role]);

    return (
        <div className={clsx("flex gap-4 mb-6", isUser ? "flex-row-reverse" : "flex-row")}>
            <div className={clsx(
                "w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0",
                isUser ? "bg-gray-900 text-white" : "bg-purple-100 text-purple-600"
            )}>
                {isUser ? <User size={16} /> : <Sparkles size={16} />}
            </div>

            <div className={clsx("max-w-[80%]", isUser ? "items-end flex flex-col" : "items-start")}>
                <div className={clsx(
                    "p-4 rounded-2xl text-sm leading-relaxed",
                    isUser ? "bg-gray-900 text-white rounded-tr-none" : "bg-white border border-gray-100 shadow-sm rounded-tl-none text-gray-800"
                )}>
                    {/* If it's pure JSON product list, don't show raw text, show lookbook */}
                    {parsedProducts && parsedProducts.length > 0 ? (
                        <p className="mb-2">I found these items for you:</p>
                    ) : (
                        <div className="whitespace-pre-wrap">{message.content}</div>
                    )}
                </div>

                {/* Render Products if any */}
                {parsedProducts && parsedProducts.length > 0 && (
                    <div className="mt-4 flex gap-4 overflow-x-auto pb-4 w-full no-scrollbar px-1">
                        {parsedProducts.map((p: Product) => (
                            <ProductCard
                                key={p.id}
                                product={p}
                                onAddToCart={onAddToCart}
                                onToggleSave={onToggleSave}
                                isSaved={checkIsSaved(p.id)}
                            />
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};
