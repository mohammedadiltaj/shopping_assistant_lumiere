import type { Message } from './types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const sendChat = async (message: string, history: Message[]) => {
    // Filter history to only send role and content
    const minimalHistory = history.map(h => ({ role: h.role, content: h.content }));

    const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message, history: minimalHistory }),
    });

    if (!response.ok) {
        throw new Error('Network response was not ok');
    }

    return response.json();
};

export const getCart = async () => {
    const response = await fetch(`${API_URL}/cart`);
    return response.json();
};
