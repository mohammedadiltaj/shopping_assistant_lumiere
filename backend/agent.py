import os
import json
import random
from typing import List, Dict, Any, Optional
from groq import Groq
from openai import AzureOpenAI
from catalog import ProductCatalog

class ShopperAgent:
    def __init__(self):
        self.catalog = ProductCatalog()
        self.cart = []
        
        # Default to Groq
        self.provider = "groq" 
        self.client = None
        self.model = "llama-3.1-8b-instant"
        
        self._setup_client()

    def _setup_client(self):
        # Check environment variables for Azure preference
        # In a real app, this might be dynamic per request or user config
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        azure_key = os.getenv("AZURE_OPENAI_API_KEY")
        
        if os.getenv("USE_AZURE_OPENAI") == "true" and azure_endpoint and azure_key:
            self.provider = "azure"
            self.client = AzureOpenAI(
                azure_endpoint=azure_endpoint,
                api_key=azure_key,
                api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
            )
            self.model = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
            print(f"Agent initialized with Azure OpenAI: {self.model}")
        else:
            self.provider = "groq"
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                print("Warning: GROQ_API_KEY not set. Switching to MOCK mode.")
                self.provider = "mock"
                self.client =  MockClient()
            else:
                self.client = Groq(api_key=api_key)
                print(f"Agent initialized with Groq: {self.model}")



    def get_system_prompt(self) -> str:
        return """You are a sophisticated, friendly, and expert Personal Shopper AI.
Your goal is to help customers find the perfect outfits and items.
You allow for vague requests and interpret them intelligently (e.g., "chilly outdoor wedding" -> suggests shawls, heavier fabrics).

You have access to a Product Catalog. You MUST use the `search_products` tool to find items.
When searching, be creative with tags.

You can also:
- Create "Lookbooks" (collections of items) using retrieval.
- Add items to the cart using `add_to_cart`.
- Checkout using `checkout`.

Output Format:
When you recommend products, you should provide a clear list.
If you simply want to chat, do so naturally.
If you are presenting a "Lookbook", explicitly mention it.

Keep responses concise but helpful. ask clarifying questions if the user request is too broad.
"""

    def tools_schema(self):
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_products",
                    "description": "Search the product catalog for items based on keywords, category, or tags.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Free text search query (e.g., 'red dress', 'steamer')"},
                            "category": {"type": "string", "description": "Category filter (e.g., 'Clothing', 'Accessories')"},
                            "tags": {"type": "array", "items": {"type": "string"}, "description": "List of tags to filter by"}
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "add_to_cart",
                    "description": "Add a specific product to the user's shopping cart.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "product_id": {"type": "string", "description": "The ID of the product to add"}
                        },
                        "required": ["product_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "checkout",
                    "description": "Process the checkout for the current cart.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_cart",
                    "description": "Get the current items in the cart.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
        ]

    def chat(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        # Append system prompt if not present
        if not messages or messages[0]["role"] != "system":
            messages.insert(0, {"role": "system", "content": self.get_system_prompt()})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools_schema(),
                tool_choice="auto",
                max_tokens=1024
            )

            assistant_msg = response.choices[0].message
            return {
                "content": assistant_msg.content,
                "tool_calls": assistant_msg.tool_calls,
                "role": "assistant"
            }
        except Exception as e:
            return {
                "content": f"I apologize, but I encountered an error: {str(e)}",
                "role": "assistant"
            }

    def execute_tool(self, tool_call) -> str:
        name = tool_call.function.name
        try:
            args = json.loads(tool_call.function.arguments)
        except:
            args = {}
            
        print(f"Executing tool: {name} with args: {args}")

        if name == "search_products":
            results = self.catalog.search_products(
                query=args.get("query", ""),
                category=args.get("category", ""),
                tags=args.get("tags", [])
            )
            return json.dumps(results)
            
        elif name == "add_to_cart":
            p_id = args.get("product_id")
            product = self.catalog.get_product_by_id(p_id)
            if product:
                self.cart.append(product)
                return json.dumps({"status": "success", "message": f"Added {product['name']} to cart.", "cart_size": len(self.cart)})
            else:
                return json.dumps({"status": "error", "message": "Product not found."})
                
        elif name == "checkout":
            if not self.cart:
                 return json.dumps({"status": "error", "message": "Cart is empty."})
            
            # Mock checkout
            order_id = f"ORD-{random.randint(1000, 9999)}"
            total = sum(p["price"] for p in self.cart)
            items = [p["name"] for p in self.cart]
            self.cart = [] # Clear cart
            return json.dumps({
                "status": "success", 
                "order_id": order_id, 
                "total": total, 
                "message": f"Order {order_id} placed successfully for {', '.join(items)}."
            })

        elif name == "get_cart":
             return json.dumps(self.cart)

        return json.dumps({"error": "Unknown tool"})

class MockClient:
    def __init__(self):
        self.catalog = ProductCatalog()

    class chat:
        def __init__(self, parent):
            self.parent = parent
        
        class completions:
            def __init__(self, parent):
                self.parent = parent.parent

            def create(self, messages, **kwargs):
                # Analyze history to decide what to do
                last_msg_obj = messages[-1]
                last_role = last_msg_obj["role"]
                last_content = str(last_msg_obj.get("content", "")).lower()

                # If last message was a tool output (role=tool), we should return a final response
                if last_role == "tool":
                    # The content is the JSON result from the tool
                    # checking if it has items
                    try:
                        data = json.loads(last_msg_obj["content"])
                        if isinstance(data, list) and len(data) > 0:
                            # Return the JSON list of products as the content
                            return MockResponse(content=last_msg_obj["content"])
                        elif isinstance(data, dict) and "message" in data:
                            # Return the success message
                            return MockResponse(content=data["message"])
                        else:
                            return MockResponse(content="I couldn't find any specific items matching that, but I can help with other requests!")
                    except:
                        return MockResponse(content="I found some items for you.")

                # Multi-Agent Simulation Logic
                
                # Agent 1: Intent Classifier
                # Determines if the user wants to Buy/Find (Search), Checkout, or just Chat.
                intent = "CHAT"
                
                # Check for checkout
                if "checkout" in last_content or ("buy" in last_content and "cart" in last_content):
                    intent = "CHECKOUT"
                # Check for Add to Cart
                elif "add" in last_content and ("cart" in last_content or "bag" in last_content):
                    intent = "ADD_TO_CART"
                # Check for View Cart
                elif "cart" in last_content or "bag" in last_content or "basket" in last_content:
                     intent = "VIEW_CART"
                # Check for search intent
                elif any(x in last_content for x in ["find", "need", "looking", "want", "show", "search", "recommend", "suggest", "buy", "shop", "where"]):
                    intent = "SEARCH"
                # Check for direct product mentions (implicit search)
                elif any(x in last_content for x in ["dress", "suit", "shoes", "jacket", "shirt", "pant", "bag", "skirt", "heels", "boots", "sneakers", "sunglasses", "glasses", "eyewear", "tuxedo", " gown"]):
                    intent = "SEARCH"

                if intent == "CHECKOUT":
                    return MockResponse(content=None, tool_calls=[MockToolCall("checkout", '{}')])
                
                if intent == "ADD_TO_CART":
                    # Try to extract ID (simple regex for gen_X)
                    import re
                    match = re.search(r'gen_\d+', last_content)
                    if match:
                        p_id = match.group(0)
                        return MockResponse(content=None, tool_calls=[MockToolCall("add_to_cart", json.dumps({"product_id": p_id}))])
                    
                    # Context Awareness Logic:
                    # If no specific ID, scanned history for recently shown products
                    # and try to match keywords from user content (e.g. "silver", "tuxedo")
                    
                    # 1. Gather recently shown products
                    context_products = []
                    # iterate reversed, skipping current user msg
                    for m in reversed(messages[:-1]): 
                        if m.get("role") == "assistant" or m.get("role") == "tool":
                            content = str(m.get("content", ""))
                            # Check if it looks like JSON list
                            if content.strip().startswith("[") and content.strip().endswith("]"):
                                try:
                                    data = json.loads(content)
                                    if isinstance(data, list):
                                        context_products.extend(data)
                                        # Only look at the most recent set of results for now to avoid ambiguity
                                        break 
                                except:
                                    continue

                    # 2. Match user keywords to products
                    user_words = set(last_content.lower().split())
                    best_match = None
                    max_overlap = 0
                    
                    for p in context_products:
                        # Create a set of keywords for the product
                        # tags is already a list from catalog.py
                        tags_list = p["tags"] if isinstance(p["tags"], list) else json.loads(p["tags"])
                        p_keywords = set(p["name"].lower().split()) | set(tags_list)
                        # Calculate overlap
                        overlap = len(user_words.intersection(p_keywords))
                        if overlap > max_overlap:
                            max_overlap = overlap
                            best_match = p
                    
                    if best_match and max_overlap > 0:
                         return MockResponse(content=None, tool_calls=[MockToolCall("add_to_cart", json.dumps({"product_id": best_match["id"]}))])
                    
                    else:
                        return MockResponse(content="Please specify which item you'd like to add (e.g., 'Add gen_123 to cart'), or describe it more uniquely.")

                if intent == "VIEW_CART":
                    return MockResponse(content=None, tool_calls=[MockToolCall("get_cart", '{}')])

                if intent == "SEARCH":
                    # Agent 2: The Stylist (Query Builder)
                    # Extracts structured information from the unstructured text
                    
                    # 2a. Demographic Extraction
                    tags = []
                    if any(x in last_content for x in ["boy", "boys", "kid", "kids"]): tags.append("boy")
                    elif any(x in last_content for x in ["girl", "girls"]): tags.append("girl")
                    elif any(x in last_content for x in ["men", "man", "male", "husband", "father"]): tags.append("men")
                    elif any(x in last_content for x in ["women", "woman", "female", "wife", "mother", "lady"]): tags.append("women")
                    
                    # 2b. Category Extraction
                    categories = {
                        "dress": "Clothing", "gown": "Clothing", "skirt": "Clothing",
                        "shirt": "Clothing", "top": "Clothing", "blouse": "Clothing", "hoodie": "Clothing",
                        "pant": "Clothing", "jeans": "Clothing", "trouser": "Clothing", "chino": "Clothing",
                        "jacket": "Clothing", "coat": "Clothing", "blazer": "Clothing", "suit": "Clothing", "tuxedo": "Clothing",
                        "shoes": "Shoes", "boot": "Shoes", "heel": "Shoes", "sneaker": "Shoes", "loafer": "Shoes", "flat": "Shoes",
                        "bag": "Accessories", "tote": "Accessories", "clutch": "Accessories", "backpack": "Accessories",
                        "jewelry": "Accessories", "earring": "Accessories", "necklace": "Accessories", "bracelet": "Accessories",
                        "scarf": "Accessories", "glass": "Accessories"
                    }
                    
                    # 2c. Attribute/Style Extraction
                    styles = [
                        "wedding", "formal", "casual", "summer", "winter", "beach", "party", "office", "work", 
                        "floral", "strip", "check", "red", "blue", "green", "black", "white", "gold", "silver", "pink",
                        "beige", "navy", "vintage", "modern", "bohemian", "chic", "streetwear", "elegant"
                    ]
                    
                    found_styles = [s for s in styles if s in last_content]
                    
                    # Construct Query
                    # We combine detected style keywords and the core object from user text
                    # Identify the core object by stripping known filler words 
                    
                    # Simple heuristic: Use the found styles + detected category keywords as the query
                    # This ensures "Summer Wedding" becomes "summer wedding" query
                    
                    query_parts = found_styles.copy()
                    
                    # Add explicit category keywords found in text to query logic
                    for keyword in categories.keys():
                        if keyword in last_content:
                            query_parts.append(keyword)
                            
                    query = " ".join(query_parts)
                    if not query:
                        query = last_content # Fallback to full text if parsing fails
                        
                    return MockResponse(
                        content=None,
                        tool_calls=[MockToolCall("search_products", json.dumps({"query": query, "tags": tags}))]
                    )

                return MockResponse(content="I am your Personal Stylist. I can help you find specific items like 'Summer Floral Dress for Women' or 'Boys Navy Suit'. What are you looking for?")

    def __init__(self):
        self.catalog = ProductCatalog()
        self.chat = self.chat(self)
        self.chat.completions = self.chat.completions(self.chat)

class MockResponse:
    def __init__(self, content, tool_calls=None):
        self.choices = [MockChoice(content, tool_calls)]

class MockChoice:
    def __init__(self, content, tool_calls):
        self.message = MockMessage(content, tool_calls)

class MockMessage:
    def __init__(self, content, tool_calls):
        self.content = content
        self.tool_calls = tool_calls

class MockToolCall:
    def __init__(self, name, arguments):
        self.id = "call_" + str(random.randint(1000,9999))
        self.function = MockFunction(name, arguments)
        self.type = "function"

class MockFunction:
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

