from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from fastapi.middleware.cors import CORSMiddleware
from agent import ShopperAgent
import os
from dotenv import load_dotenv
from database import init_db

load_dotenv()
init_db()

app = FastAPI(title="AI Personal Shopper API")

# Debug Exception Handler
from fastapi.responses import JSONResponse
from fastapi.requests import Request
import traceback

@app.exception_handler(Exception)
async def debug_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error", "detail": str(exc), "traceback": traceback.format_exc()},
    )

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Agent Instance (for simple statefulness in this demo)
# In a real production app, we'd use a database/Redis for session management
agent = ShopperAgent()

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Dict[str, str]]] = []

class ChatResponse(BaseModel):
    role: str
    content: Optional[str] = None
    tool_calls: Optional[List[Any]] = None

@app.get("/")
def read_root():
    return {"status": "Shopper Agent API is running"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    # Construct message history
    messages = request.history
    messages.append({"role": "user", "content": request.message})
    
    # Get agent response
    response = agent.chat(messages)
    
    # Check if tool calls exist
    if response.get("tool_calls"):
        # We need to execute them and feed back to the model?
        # Or does the frontend handle the display?
        # For a simple agent loop, let's handle tool execution server-side 
        # But wait, looking at agent.py, it returns tool_calls.
        # Usually we want the LLM to see the tool outputs to formulate a final answer.
        
        # Let's do a simple ReAct loop here (limit 1 turn of tools for speed)
        tool_calls = response["tool_calls"]
        messages.append(response) # Add assistant's tool_call message
        
        for tool_call in tool_calls:
            # Execute tool
            tool_result = agent.execute_tool(tool_call)
            
            # Append tool result to history
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": tool_result
            })
            
        # Get final response after tool outputs
        final_response = agent.chat(messages)
        return final_response

    return response

@app.get("/cart")
def get_cart():
    return agent.cart

@app.post("/cart/items")
def add_to_cart(item: Dict[str, Any]):
    # Expects {"product_id": "gen_123"}
    product_id = item.get("product_id")
    if not product_id:
        raise HTTPException(status_code=400, detail="product_id is required")
    
    # Use agent's tool logic to add to cart
    # We can reuse the tool function directly or just call execute_tool logic
    # But since agent state is global, we can just access it.
    
    # Ideally we'd use the agent's internal method, but it is private/tool-based.
    # Let's direct call the tool method on the agent wrapper if possible or duplicate logic.
    # Looking at agent.py, it uses self.cart
    
    # Find product by ID first
    from catalog import ProductCatalog
    catalog = ProductCatalog()
    product = catalog.get_product_by_id(product_id)
    
    if product:
        agent.cart.append(product)
        return {"status": "success", "cart_count": len(agent.cart), "message": f"Added {product['name']} to cart"}
    else:
        raise HTTPException(status_code=404, detail="Product not found")

@app.delete("/cart/items/{item_id}")
def remove_from_cart(item_id: str):
    # Search for item index
    idx = -1
    for i, p in enumerate(agent.cart):
        if p["id"] == item_id:
            idx = i
            break
            
    if idx != -1:
        removed = agent.cart.pop(idx)
        return {"status": "success", "cart_count": len(agent.cart), "message": f"Removed {removed['name']} from cart"}
    else:
        raise HTTPException(status_code=404, detail="Item not found in cart")

@app.post("/reset")
def reset_agent():
    global agent
    agent = ShopperAgent()
    return {"status": "Agent reset"}
