import React from 'react';
import type { Product } from '../types';
import { Plus, Heart } from 'lucide-react';

interface ProductCardProps {
    product: Product;
    onAddToCart: (product: Product) => void;
    onToggleSave: (product: Product) => void;
    isSaved: boolean;
}

export const ProductCard: React.FC<ProductCardProps> = ({ product, onAddToCart, onToggleSave, isSaved }) => {
    return (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-shadow duration-300 w-64 flex-shrink-0">
            <div className="h-48 overflow-hidden relative group">
                <img
                    src={product.image}
                    alt={product.name}
                    className="w-full h-full object-cover transform group-hover:scale-105 transition-transform duration-500"
                />
                <button
                    onClick={() => onAddToCart(product)}
                    className="absolute bottom-2 right-2 bg-white/90 p-2 rounded-full shadow-sm hover:bg-black hover:text-white transition-colors"
                    title="Add to Cart"
                >
                    <Plus size={18} />
                </button>
                <button
                    onClick={() => onToggleSave(product)}
                    className={`absolute top-2 right-2 p-2 rounded-full shadow-sm transition-colors ${isSaved ? 'bg-red-500 text-white' : 'bg-white/90 text-gray-400 hover:text-red-500'}`}
                    title={isSaved ? "Remove from Saved" : "Save Look"}
                >
                    <Heart size={18} fill={isSaved ? "currentColor" : "none"} />
                </button>
            </div>
            <div className="p-4">
                <div className="text-xs text-gray-500 uppercase tracking-wider mb-1">{product.category}</div>
                <h3 className="font-medium text-gray-900 truncate mb-1">{product.name}</h3>
                <p className="text-gray-900 font-semibold">${product.price.toFixed(2)}</p>
            </div>
        </div>
    );
};
