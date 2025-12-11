# Lumière - Technical Deep Dive & Q&A
> *Internal documentation for Demo/Hackathon Q&A Preparation.*

## 1. High-Level Architecture
**Pattern**: Monolithic Backend API + SPA Frontend.
- **Frontend**: React 18 (Vite) + TailwindCSS v4.
- **Backend**: FastAPI (Python 3.11).
- **Database**: SQLite (file-based).
- **AI Engine**: Hybrid approaches (Rule-based heuristics + Groq/Llama 3).

### Why this stack?
- **FastAPI**: Native support for async/await (crucial for LLM streaming/concurrency) and Pydantic validation.
- **SQLite**: Zero-config persistence, perfect for hackathons/demos without docker overhead.
- **Groq**: Lowest latency interference for Llama 3 models, essential for "chat-like" responsiveness.

---

## 2. The AI Agent ("The Brain")
Located in `backend/agent.py`.

### How does it know what to do? (Intent Classification)
The agent doesn't just "talk". It parses every user message to classify it into one of 4 intents:
1.  **SEARCH**: User is looking for items (e.g., "Silver dress").
2.  **ADD_TO_CART**: User wants to buy something.
3.  **VIEW_CART**: User wants to manage their bag.
4.  **CHAT**: General conversation.

### How does "Context Add" work?
*Q: "If I say 'add the silver one', how does it know which product?"*
**A**:
1.  The backend maintains a short-term history of the conversation.
2.  When `ADD_TO_CART` intent is detected without a specific ID, the agent scans the **last few assistant messages**.
3.  It looks for **JSON product data** that was recently displayed.
4.  It performs a **keyword intersection** between your request ("silver") and the recent products' tags/titles.
5.  The best match is automatically resolved to a Product ID (`gen_8`) and added.

### Tool Calling
We use the **OpenAI Tool Calling Standard** (even with Groq).
- The System Prompt defines available functions: `search_products`, `add_to_cart`.
- The LLM outputs a structured JSON "tool call" instead of text.
- The Backend intercept this, runs the Python function (e.g., querying SQLite), and feeds the result back to the LLM.

---

## 3. Database & Data Model
Located in `backend/seed.py` and `backend/catalog.py`.
**Schema**: Single `products` table.
- `id`: Text (e.g., `gen_1` or UUID).
- `tags`: JSON string (Searchable keywords).
- `embedding`: (Prepared for future Vector Search).

*Q: "Is the search semantic or keyword-based?"*
**A**: Currently, it is **Keyword/Tag-based** with intelligent expansion. The Agent expands queries (e.g., "Winter Wedding" -> tags: `formal`, `winter`, `gown`) to find relevant items even without vector embeddings.

---

## 4. Frontend Architecture
Located in `frontend/src/App.tsx`.
- **State Management**: React `useState` + Polling.
- **Cart Sync**: The frontend polls `/cart` every 2 seconds to ensure the UI matches the Agent's internal state. This handles the "Agent added item" scenario seamlessly.
- **Optimistic Updates**: UI buttons update the visible number immediately for perceived speed, then reconcile with the backend.

---

## 5. Potential "Gotcha" Questions & Answers

**Q: What happens if the LLM hallucinates a product?**
> A: The `add_to_cart` tool performs a mandatory DB validation check. If the ID doesn't exist in SQLite, the backend rejects it and returns an error to the Agent, which then apologizes to the user.

**Q: How do you handle latency?**
> A: We use **Groq**, which provides ~500 tokens/sec inference. This makes the tool-calling loop (User -> LLM -> Tool -> LLM -> Response) feel almost instantaneous (< 1.5s).

**Q: Is this secure?**
> A: For a hackathon, we use simple state management. In production, we would add JWT Authentication and Redis for session storage instead of global variables.

**Q: How scalable is the search?**
> A: Currently O(N) on SQL LIKE queries. For scale, we would migrate SQLite to PostgreSQL (pgvector) and use Cosine Similarity for semantic search.
