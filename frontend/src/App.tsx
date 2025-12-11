import { useState, useEffect } from 'react';
import { ChatInterface } from './components/ChatInterface';
import { ProductCard } from './components/ProductCard';
import type { Product, Message } from './types';
import { ShoppingBag, Sparkles, X, Trash2 } from 'lucide-react';
// Simple API util (inline for now or import from api.ts if exists)
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [cartCount, setCartCount] = useState(0);
  const [cartItems, setCartItems] = useState<Product[]>([]);
  const [isCartOpen, setIsCartOpen] = useState(false);

  const [activeTab, setActiveTab] = useState<'chat' | 'collections' | 'saved'>('chat');
  const [savedItems, setSavedItems] = useState<Product[]>([]);
  const [showCheckoutToast, setShowCheckoutToast] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    { role: 'system', content: 'Welcome! I am your personal shopper. How can I help you today?' }
  ]);

  const fetchCart = async () => {
    try {
      const res = await fetch(`${API_URL}/cart`);
      const data = await res.json();
      if (Array.isArray(data)) {
        setCartItems(data);
        setCartCount(data.length);
      }
    } catch (e) {
      console.error("Failed to fetch cart", e);
    }
  };

  useEffect(() => {
    fetchCart();
  }, []);

  // Poll for cart updates every few seconds to keep sync if chat updates it
  useEffect(() => {
    const interval = setInterval(fetchCart, 2000); // Polling is simple for this demo
    return () => clearInterval(interval);
  }, []);

  const handleAddToCart = async (product: Product) => {
    // Optimistic update
    setCartCount(prev => prev + 1);

    // Call backend to add
    try {
      await fetch(`${API_URL}/cart/items`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_id: product.id })
      });
      // Fetch cart again to be sure of sync
      fetchCart();
    } catch (e) {
      console.error("Failed to add to cart backend", e);
      // Revert optimistic update if needed, but for now let's keep it simple
    }
  };

  const handleToggleSave = (product: Product) => {
    setSavedItems(prev => {
      const isSaved = prev.some(p => p.id === product.id);
      if (isSaved) {
        return prev.filter(p => p.id !== product.id);
      } else {
        return [...prev, product];
      }
    });
  };

  const checkIsSaved = (id: string) => {
    return savedItems.some(p => p.id === id);
  };

  const handleCheckout = async () => {
    if (cartCount === 0) return;

    // Call backend checkout tool/endpoint via chat acts?
    // Or just clear locally and backend.
    // Let's reset backend agent for now or add a clear endpoint.
    // For now, visual feedback:
    setCartCount(0);
    setCartItems([]);
    setShowCheckoutToast(true);
    setIsCartOpen(false);

    // Ideally call backend to clear
    try {
      await fetch(`${API_URL}/reset`, { method: 'POST' });
      setMessages([{ role: 'system', content: 'Welcome! I am your personal shopper. How can I help you today?' }]); // Reset chat too as agent is reset
    } catch (e) { }

    setTimeout(() => setShowCheckoutToast(false), 3000);
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'chat':
        return <ChatInterface messages={messages} setMessages={setMessages} onAddToCart={handleAddToCart} onToggleSave={handleToggleSave} checkIsSaved={checkIsSaved} onChatUpdate={fetchCart} />;
      case 'collections':
        return (
          <div className="bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-100 h-full p-8 overflow-y-auto">
            <h2 className="text-2xl font-bold mb-6">Curated Collections</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="h-48 bg-gray-100 rounded-xl flex items-center justify-center cursor-pointer hover:bg-gray-200 transition-colors group relative overflow-hidden">
                <img src="https://images.unsplash.com/photo-1515934751635-c81c6bc9a2d8?q=80&w=1000&auto=format&fit=crop" className="absolute inset-0 w-full h-full object-cover opacity-80 group-hover:scale-105 transition-transform duration-500" />
                <span className="relative z-10 font-bold text-white text-xl bg-black/30 px-4 py-2 rounded-lg backdrop-blur-sm">Summer Wedding</span>
              </div>
              <div className="h-48 bg-gray-100 rounded-xl flex items-center justify-center cursor-pointer hover:bg-gray-200 transition-colors group relative overflow-hidden">
                <img src="https://images.unsplash.com/photo-1483985988355-763728e1935b?q=80&w=1000&auto=format&fit=crop" className="absolute inset-0 w-full h-full object-cover opacity-80 group-hover:scale-105 transition-transform duration-500" />
                <span className="relative z-10 font-bold text-white text-xl bg-black/30 px-4 py-2 rounded-lg backdrop-blur-sm">Winter Formal</span>
              </div>
              <div className="h-48 bg-gray-100 rounded-xl flex items-center justify-center cursor-pointer hover:bg-gray-200 transition-colors group relative overflow-hidden">
                <img src="https://images.unsplash.com/photo-1543163521-1bf539c55dd2?q=80&w=1000&auto=format&fit=crop" className="absolute inset-0 w-full h-full object-cover opacity-80 group-hover:scale-105 transition-transform duration-500" />
                <span className="relative z-10 font-bold text-white text-xl bg-black/30 px-4 py-2 rounded-lg backdrop-blur-sm">Accessories</span>
              </div>
              <div className="h-48 bg-gray-100 rounded-xl flex items-center justify-center cursor-pointer hover:bg-gray-200 transition-colors group relative overflow-hidden">
                <img src="https://images.unsplash.com/photo-1490481651871-ab68de25d43d?q=80&w=1000&auto=format&fit=crop" className="absolute inset-0 w-full h-full object-cover opacity-80 group-hover:scale-105 transition-transform duration-500" />
                <span className="relative z-10 font-bold text-white text-xl bg-black/30 px-4 py-2 rounded-lg backdrop-blur-sm">Casual Chic</span>
              </div>
            </div>
          </div>
        );
      case 'saved':
        return (
          <div className="bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-100 h-full p-8 overflow-y-auto">
            <h2 className="text-2xl font-bold mb-6">Saved Looks ({savedItems.length})</h2>
            {savedItems.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-64 text-gray-400">
                <Sparkles size={48} className="mb-4 opacity-50" />
                <p>No saved looks yet. Heart items in the chat to save them!</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {savedItems.map(p => (
                  <div key={p.id} className="transform scale-90 origin-top-left">
                    <ProductCard
                      product={p}
                      onAddToCart={handleAddToCart}
                      onToggleSave={handleToggleSave}
                      isSaved={true}
                    />
                  </div>
                ))}
              </div>
            )}
          </div>
        );
    }
  };

  return (
    <div className="h-screen w-full bg-prime-50 flex font-sans overflow-hidden">
      {/* Sidebar / Branding */}
      <div className="w-64 bg-white hidden md:flex flex-col justify-between p-6 border-r border-gray-100 flex-shrink-0">
        <div>
          <div className="flex items-center gap-2 mb-10">
            <div className="w-8 h-8 bg-gray-900 text-white rounded-lg flex items-center justify-center shadow-md">
              <Sparkles size={18} />
            </div>
            <span className="font-bold text-xl tracking-tight text-gray-900">LUMIERE</span>
          </div>

          <nav className="space-y-2">
            <button
              onClick={() => setActiveTab('chat')}
              className={`w-full text-left px-4 py-3 rounded-xl transition-all font-medium flex items-center gap-3 ${activeTab === 'chat' ? 'bg-gray-900 text-white shadow-md' : 'text-gray-500 hover:text-gray-900 hover:bg-gray-50'}`}
            >
              <span>Personal Shopper</span>
            </button>
            <button
              onClick={() => setActiveTab('collections')}
              className={`w-full text-left px-4 py-3 rounded-xl transition-all font-medium flex items-center gap-3 ${activeTab === 'collections' ? 'bg-gray-900 text-white shadow-md' : 'text-gray-500 hover:text-gray-900 hover:bg-gray-50'}`}
            >
              <span>Collections</span>
            </button>
            <button
              onClick={() => setActiveTab('saved')}
              className={`w-full text-left px-4 py-3 rounded-xl transition-all font-medium flex items-center gap-3 ${activeTab === 'saved' ? 'bg-gray-900 text-white shadow-md' : 'text-gray-500 hover:text-gray-900 hover:bg-gray-50'}`}
            >
              <span>Saved Looks</span>
            </button>
          </nav>
        </div>

        <div className="bg-gray-50 p-4 rounded-2xl border border-gray-100">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-500">Shopping Bag</span>
            <ShoppingBag size={16} className="text-gray-900" />
          </div>
          <div className="text-3xl font-bold text-gray-900 mb-1">{cartCount}</div>
          <div className="text-xs text-gray-400 mb-3">items selected</div>

          <div className="flex gap-2">
            <button
              onClick={() => setIsCartOpen(true)}
              className="flex-1 bg-white border border-gray-200 text-gray-900 text-sm py-2.5 rounded-xl hover:bg-gray-50 transition-colors font-medium shadow-sm"
            >
              View
            </button>
            <button
              onClick={handleCheckout}
              disabled={cartCount === 0}
              className="flex-[2] bg-gray-900 text-white text-sm py-2.5 rounded-xl hover:bg-gray-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-sm font-medium"
            >
              Checkout
            </button>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 h-full relative overflow-hidden bg-prime-50 p-4 md:p-6">
        {renderContent()}

        {/* Checkout Toast */}
        {showCheckoutToast && (
          <div className="absolute top-6 left-1/2 transform -translate-x-1/2 bg-gray-900 text-white px-6 py-3 rounded-full shadow-lg flex items-center gap-3 animate-fade-in-up z-50">
            <div className="w-5 h-5 bg-green-500 rounded-full flex items-center justify-center text-xs">✓</div>
            <span className="font-medium">Order placed successfully!</span>
          </div>
        )}
      </div>

      {/* Cart Modal Overlay */}
      {isCartOpen && (
        <div className="absolute inset-0 z-50 flex items-end justify-end pointer-events-none p-4 md:p-6">
          <div className="absolute inset-0 bg-black/20 backdrop-blur-sm pointer-events-auto" onClick={() => setIsCartOpen(false)}></div>
          <div className="bg-white w-full max-w-md h-full md:h-[90%] rounded-2xl shadow-2xl flex flex-col pointer-events-auto z-50 overflow-hidden transform transition-all animate-slide-in-right">
            <div className="p-6 border-b border-gray-100 flex items-center justify-between bg-gray-50/50">
              <div className="flex items-center gap-3">
                <ShoppingBag className="text-gray-900" size={20} />
                <h3 className="font-bold text-xl text-gray-900">Your Bag</h3>
                <span className="bg-gray-900 text-white text-xs px-2 py-0.5 rounded-full">{cartCount}</span>
              </div>
              <button onClick={() => setIsCartOpen(false)} className="p-2 hover:bg-gray-100 rounded-full transition-colors text-gray-500">
                <X size={20} />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {cartItems.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-gray-400">
                  <ShoppingBag size={48} className="mb-4 opacity-20" />
                  <p>Your bag is empty.</p>
                  <button onClick={() => setIsCartOpen(false)} className="mt-4 text-purple-600 font-medium hover:underline">Start Shopping</button>
                </div>
              ) : (
                cartItems.map((item, idx) => (
                  <div key={`${item.id}-${idx}`} className="flex gap-4 p-4 bg-white border border-gray-100 rounded-xl shadow-sm hover:shadow-md transition-shadow group">
                    <img src={item.image || "https://images.unsplash.com/photo-1595777457583-95e059d581b8?q=80&w=200"} className="w-20 h-20 object-cover rounded-lg bg-gray-100" />
                    <div className="flex-1 min-w-0">
                      <h4 className="font-bold text-gray-900 truncate">{item.name}</h4>
                      <p className="text-sm text-gray-500 capitalize">{item.category}</p>
                      <div className="flex items-center justify-between mt-2">
                        <span className="font-medium text-gray-900">${item.price}</span>
                        <button
                          onClick={async () => {
                            try {
                              await fetch(`${API_URL}/cart/items/${item.id}`, { method: 'DELETE' });
                              fetchCart();
                            } catch (e) { console.error(e) }
                          }}
                          className="p-2 text-gray-400 hover:text-red-500 transition-colors opacity-0 group-hover:opacity-100"
                          title="Remove item"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>

            <div className="p-6 border-t border-gray-100 bg-gray-50/50 space-y-4">
              <div className="flex justify-between items-center text-gray-600">
                <span>Subtotal</span>
                <span className="font-medium text-gray-900">${cartItems.reduce((acc, curr) => acc + curr.price, 0).toFixed(2)}</span>
              </div>
              <button
                onClick={handleCheckout}
                disabled={cartCount === 0}
                className="w-full bg-gray-900 text-white py-3.5 rounded-xl font-bold hover:bg-gray-800 transition-colors shadow-lg disabled:opacity-50 disabled:shadow-none"
              >
                Proceed to Checkout
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}


export default App;
