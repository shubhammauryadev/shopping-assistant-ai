# Quick Start Guide

This guide will get you up and running with the AI Shopping Assistant in minutes.

## Prerequisites

- **Python 3.12+** with Poetry installed
- **Node.js 18+** with npm installed
- **Google Gemini API Key** (sign up at https://ai.google.dev)

## Step 1: Backend Setup (5 minutes)

### 1.1 Create environment file
```bash
cp .env.example .env
```

### 1.2 Add your Google Gemini API key
Edit `.env` and set your API key:
```
GOOGLE_API_KEY=your_actual_gemini_key_here
```
**Note**: The Google Generative Language API must be enabled for your API key in Google Cloud Console.

### 1.3 Install dependencies
```bash
poetry install
```

### 1.4 Start the backend
```bash
poetry run uvicorn main:app --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Started server process [xxxxx]
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

The database (`shopping_assistant.db`) will be created automatically.

## Step 2: Frontend Setup (2 minutes)

### 2.1 Open a new terminal and navigate to frontend
```bash
cd frontend
```

### 2.2 Install dependencies
```bash
npm install
```

### 2.3 Start the development server
```bash
npm run dev
```

You should see:
```
 ▲ Next.js 16.1.1
...
○ Ready in 1234ms
```

## Step 3: Use the Application

1. Open your browser to `http://localhost:3000`
2. You should see the AI Shopping Assistant chat interface
3. Try these commands:
   - "Search for electronics under $100"
   - "Find the cheapest laptop"
   - "Compare first two products"
   - "Add the cheaper one to my cart"
   - "Show me my cart"
   - "Clear my cart"

## Testing

### Quick Test (Backend Only)

```bash
curl -X POST http://localhost:8000/health
```

Expected response:
```json
{"status": "ok"}
```

### Full Integration Test

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Search for t-shirts",
    "session_id": "test_session"
  }'
```

The response will stream with server-sent events.

## Troubleshooting

### Backend won't start
- Check if port 8000 is already in use: `lsof -i :8000`
- Verify Google Gemini API key is correct in `.env`
- Ensure Google Generative Language API is enabled in Google Cloud Console
- Try: `poetry run uvicorn main:app --port 8001`

### Frontend won't start
- Check if port 3000 is already in use: `lsof -i :3000`
- Clear npm cache: `npm cache clean --force`
- Reinstall dependencies: `rm -rf node_modules && npm install`

### Agent not responding
- Check backend logs for errors
- Verify Google Gemini API key is valid and API is enabled
- Make sure you have API quota available
- Check that the agent can access conversation state for multi-turn references

### Multi-turn references not working
- Ensure conversation state is properly maintained per session
- Verify that previous search or comparison results were stored
- Check backend logs for reference resolution attempts
- Example: After "search for laptops", try "compare first two" and then "add the cheaper one"

### Clear cart not working
- Ensure CartService.clear_cart() is properly implemented
- Verify the clear_cart LangChain tool is available to the agent
- Check that session_id is being passed correctly
- Frontend should show "Clear Cart" button only when items exist in cart

### Database errors
- Delete `shopping_assistant.db` and restart backend
- Check SQLite has write permissions in the project directory

## Development Mode

### Backend with hot reload
Poetry watches Python files automatically when you edit them.

### Frontend with hot reload
Changes to frontend code are reflected immediately at `http://localhost:3000`

## Production Build

### Frontend
```bash
cd frontend
npm run build
npm run start
```

### Backend
```bash
poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## File Structure Overview

```
├── main.py              # FastAPI app entry point
├── agent.py             # LLM agent setup
├── services.py          # Business logic
├── database.py          # SQLite setup
├── models.py            # Database models
├── README.md            # Full documentation
│
└── frontend/
    ├── app/page.tsx     # Main chat page
    ├── components/      # React components
    └── package.json     # Frontend dependencies
```

## Next Steps

1. Review the conversation flow in the chat interface
2. Examine how the agent uses tools in `agent.py`
3. Explore the database schema in `models.py`
4. Check the API contract in `main.py`
5. Test different user queries to understand agent behavior

## Support

For issues or questions, check:
- `README.md` for architecture details
- Backend logs from terminal running the server
- Frontend console (browser DevTools) for client-side errors
- OpenAI API status page for service issues
