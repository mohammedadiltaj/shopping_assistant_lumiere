export interface Product {
    id: string;
    name: string;
    category: string;
    price: number;
    description: string;
    tags: string[];
    image: string;
}

export interface Message {
    role: 'user' | 'assistant' | 'system' | 'tool';
    content: string;
    tool_calls?: any[];
    tool_call_id?: string;
    products?: Product[]; // Optional embedded products for rich display
}
