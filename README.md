# AI Shopping Assistant

A full-stack AI-powered shopping assistant application with a Python FastAPI backend and Next.js frontend. Features multi-turn conversation understanding, real-time product search, shopping cart management, and product comparison capabilities.

## Architecture

### Backend (Python)
- **Framework**: FastAPI with Uvicorn
- **Database**: SQLite with SQLAlchemy ORM
- **AI Agent**: LangChain with Google Gemini (ChatGoogleGenerativeAI)
- **External API**: Fake Store API for product data
- **Streaming**: Server-Sent Events (SSE)
- **Conversation State**: Session-based state management for multi-turn references

### Frontend (Next.js 14)
- **Framework**: Next.js 14 with TypeScript
- **Styling**: TailwindCSS + shadcn/ui
- **State Management**: React hooks
- **Session Management**: Browser sessionStorage
- **API Communication**: Fetch API with streaming support

## Setup

### Backend Setup

1. **Install dependencies**:
   ```bash
   poetry install
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your Google Gemini API key:
   ```
   GOOGLE_API_KEY=your_google_gemini_api_key_here
   ```
   **Note**: Ensure the Google Generative Language API is enabled in your Google Cloud project.

3. **Run the server**:
   ```bash
   poetry run uvicorn main:app --host 0.0.0.0 --port 8000
   ```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Install dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Run the development server**:
   ```bash
   npm run dev
   ```

The frontend will be available at `http://localhost:3000`

## Features

### Conversation
- Real-time streaming chat interface
- Message history per session
- Session-based (no authentication required)
- **Multi-turn reference resolution**: Understand context across multiple messages

### Shopping
- **Search Products**: Search by query, category, and price range
- **Product Details**: View detailed product information
- **Shopping Cart**: Add/remove items, view cart totals, clear cart
- **Product Comparison**: Compare products side-by-side
- **Natural Language Shopping**: Say things like "add the cheaper one" without specifying product IDs

### AI Agent
The LangChain agent (powered by Google Gemini) has access to these tools:
- `search_products(query, category, price_range)` - Search for products and store results for reference resolution
- `get_product_details(product_id)` - Fetch product details
- `add_to_cart(product_id, quantity, reference)` - Add items to cart using explicit IDs or natural language references
- `remove_from_cart(product_id)` - Remove items from cart
- `get_cart()` - View current cart
- `compare_products(reference)` - Compare products using natural language references
- `clear_cart()` - Clear all items from cart

### Multi-Turn Reference Resolution
The assistant automatically understands contextual references across multiple turns:
- **Ordinal references**: "first", "second", "third" (e.g., "Add the first product to my cart")
- **Comparative references**: "cheaper", "cheapest", "more expensive", "expensive" (e.g., "Compare first two products, then add the cheaper one")
- **Collection references**: "first two", "top three" (e.g., "Compare first two products")

Example conversation:
```
User: Search for laptops
Assistant: Found 5 laptops...

User: Compare first two
Assistant: Comparing first two laptops...

User: Add the cheaper one
Assistant: Added the cheaper laptop to your cart!
```

## Message Format

Assistant responses follow a structured format:

```json
{
  "type": "text" | "products" | "comparison" | "cart",
  "data": {
    "text": "Natural language explanation",
    "results": [...],  // For product searches
    "items": [...],    // For cart
    "products": [...]  // For comparisons
  }
}
```

## Database Schema

### cart
- `id` (PK)
- `session_id` (Unique)
- `created_at`, `updated_at`

### cart_items
- `id` (PK)
- `cart_id` (FK)
- `product_id`, `product_title`, `price`, `quantity`

### conversation_messages
- `id` (PK)
- `session_id`
- `role` (user | assistant)
- `content`
- `created_at`

### product_cache
- `product_id` (PK)
- `category`, `title`, `price`, `description`, `image`
- `cached_at`

## API Endpoints

### POST /chat
Request:
```json
{
  "message": "Search for wireless headphones",
  "session_id": "session_xxx"
}
```

Response: Server-Sent Events (SSE) stream with `text` chunks

### GET /health
Simple health check returning `{"status": "ok"}`

## How It Works

1. **Session Creation**: Frontend generates and stores a unique `session_id` in browser sessionStorage
2. **User Input**: User types a message in the chat interface
3. **API Call**: Frontend sends message + session_id to `/chat` endpoint
4. **Agent Processing**:
   - Backend agent receives the message
   - Decides which tools to use (search, get details, add to cart, etc.)
   - Executes tools with SQLite as source of truth
   - Falls back to Fake Store API if data not cached
5. **Streaming Response**: Backend streams assistant response as Server-Sent Events
6. **Frontend Display**: Frontend renders response based on message type (text, products, cart, comparison)

## Design Decisions

- **No Authentication**: Single anonymous session per browser
- **SQLite is Source of Truth**: All cart and conversation data persisted in SQLite
- **Fake Store API for Fallback**: Only used when product not in cache
- **Streaming Only**: No WebSockets, using SSE for simplicity
- **Minimal Frontend**: Interview-friendly, no over-engineering
- **Linear Agent**: No multi-agent orchestration, simple tool calling
- **Google Gemini LLM**: Free, reliable, no rate limiting concerns for demo purposes
- **Session-Based Conversation State**: Lightweight in-memory tracking of search and comparison results per session, enabling natural multi-turn references without database overhead
- **Defensive UI Pattern**: Frontend calculates cart totals from items as fallback when backend totals are missing, ensuring correct display during streaming

## Development Notes

### Environment Variables
Backend requires: `GOOGLE_API_KEY` (Google Generative Language API key)
Frontend can optionally configure: `NEXT_PUBLIC_BACKEND_URL` (defaults to `http://localhost:8000`)

### Conversation State Management
The backend maintains a per-session `ConversationState` object that tracks:
- `last_search_results`: Products from the most recent search (for ordinal/comparative references)
- `last_compared_products`: Products from the most recent comparison (for price-based references)

This enables the agent to resolve natural language references like "first two" or "cheaper one" without requiring users to specify explicit product IDs.

### Adding New Products
Products are cached automatically from Fake Store API. Cache persists in SQLite database.

### Testing the Agent
Use curl to test the backend:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Find wireless headphones under $100",
    "session_id": "test_session_001"
  }'
```

## Project Structure

```
.
├── backend files (Python)
│   ├── main.py                 # FastAPI application with CORS middleware
│   ├── agent.py                # LangChain agent setup with Google Gemini
│   ├── agent_tools.py          # Tool definitions (search, add_to_cart, compare_products, clear_cart, etc.)
│   ├── conversation_state.py   # Session-based state management for multi-turn references
│   ├── services.py             # Business logic (CartService, ProductService, etc.)
│   ├── models.py               # SQLAlchemy ORM models (Cart, CartItem, etc.)
│   ├── database.py             # Database setup
│   ├── fake_store_client.py    # External API integration
│   ├── schemas.py              # Pydantic models
│   ├── config.py               # Configuration
│   ├── pyproject.toml          # Poetry dependencies
│   └── .env                    # Environment variables
│
└── frontend/                   # Next.js frontend (responsive, mobile-optimized)
    ├── app/
    │   ├── page.tsx            # Home page
    │   ├── layout.tsx          # Root layout
    │   └── globals.css         # Global styles
    ├── components/
    │   ├── ChatInterface.tsx    # Main chat UI with multi-turn streaming
    │   ├── ProductCards.tsx     # Product display cards
    │   └── CartSummary.tsx      # Cart display with clear button
    ├── lib/                     # Utilities
    ├── package.json            # NPM dependencies
    └── .env.local              # Frontend config
```
