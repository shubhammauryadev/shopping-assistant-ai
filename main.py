"""FastAPI application with streaming chat endpoint."""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import StreamingResponse
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import init_db, get_db, SessionLocal
from schemas import ChatRequest
from agent import create_agent
from agent_tools import set_session_context
from models import ConversationMessage
from datetime import datetime
import json

app = FastAPI(title="AI Shopping Assistant")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup():
    """Initialize database on app startup."""
    init_db()


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Chat endpoint with streaming response.
    Accepts a message and session_id, streams back assistant response.
    """
    db = SessionLocal()

    try:
        # Get or create agent
        agent = create_agent()

        # Store user message in database
        user_msg = ConversationMessage(
            session_id=request.session_id,
            role="user",
            content=request.message,
            created_at=datetime.utcnow()
        )
        db.add(user_msg)
        db.commit()

        # Helper function to stream response
        def generate_response():
            """Generator that streams agent response."""
            try:
                # Set session context for tools
                set_session_context(db, request.session_id)

                # Invoke agent
                input_text = request.message

                response = agent.invoke(
                    {"messages": [{"role": "user", "content": input_text}]},
                    config={"configurable": {"thread_id": request.session_id}}
                )
                print(response["messages"][-1].content)
                # LangGraph returns messages in the response
                output_text = ""
                if "messages" in response and response["messages"]:
                    last_message = response["messages"][-1]
                    if hasattr(last_message, "content"):
                        content = last_message.content
                        if isinstance(content, list):
                            # Handle list of content blocks
                            parts = []
                            for part in content:
                                if isinstance(part, str):
                                    parts.append(part)
                                elif isinstance(part, dict):
                                    if "text" in part:
                                        parts.append(part["text"])
                                    elif "content" in part: # some models use content key
                                        parts.append(part["content"])
                            output_text = "".join(parts)
                        else:
                            output_text = content
                    elif isinstance(last_message, dict) and "content" in last_message:
                        output_text = last_message["content"]
                    else:
                        output_text = str(last_message)

                # Defensive cleanup: strip markdown code blocks if present
                if isinstance(output_text, str):
                    output_text = output_text.strip()
                    if output_text.startswith("```json"):
                        output_text = output_text[7:]  # Remove ```json
                    elif output_text.startswith("```"):
                        output_text = output_text[3:]  # Remove ```
                    if output_text.endswith("```"):
                        output_text = output_text[:-3]  # Remove trailing ```
                    output_text = output_text.strip()

                # Try to parse output as JSON, otherwise wrap in text type
                try:
                    import json as json_lib
                    parsed = json_lib.loads(output_text)
                    if isinstance(parsed, dict) and "type" in parsed and "data" in parsed:
                        output_text = output_text  # Already structured
                    else:
                        # If parsed but not in expected format, wrap it
                        output_text = json_lib.dumps({
                            "type": "text",
                            "data": {"text": output_text}
                        })
                except json.JSONDecodeError:
                    # Not JSON, wrap in text type
                    output_text = json.dumps({
                        "type": "text",
                        "data": {"text": output_text}
                    })

                # Store assistant message
                assistant_msg = ConversationMessage(
                    session_id=request.session_id,
                    role="assistant",
                    content=output_text,
                    created_at=datetime.utcnow()
                )
                db.add(assistant_msg)
                db.commit()

                # Stream the response in chunks
                chunk_size = 50
                for i in range(0, len(output_text), chunk_size):
                    chunk = output_text[i:i + chunk_size]
                    yield f"data: {json.dumps({'text': chunk})}\n\n"

                # Send done signal
                yield f"data: {json.dumps({'done': True})}\n\n"

            except Exception as e:
                # Send error
                error_msg = str(e)
                yield f"data: {json.dumps({'error': error_msg})}\n\n"
            finally:
                db.close()

        # Return streaming response
        return StreamingResponse(
            generate_response(),
            media_type="text/event-stream"
        )

    except Exception as e:
        db.close()
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)
