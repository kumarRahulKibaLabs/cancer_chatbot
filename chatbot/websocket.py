from fastapi import WebSocket, WebSocketDisconnect
from chatbot.graph import setup_graph
from chatbot.prompt import sys_prompt
from langchain_openai import ChatOpenAI
import os
import uuid
from langchain_core.messages import AIMessage, ToolMessage
from dotenv import load_dotenv
from chatbot.tools import premium_filter


# Load environment variables once at module level
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable must be set")

async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for chatbot interaction."""
    await websocket.accept()
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    # Initialize model and graph once per connection
    try:
        model = ChatOpenAI(
            model="gpt-4o",
            temperature=0,
            api_key=OPENAI_API_KEY
        ).bind_tools([premium_filter])
        app = setup_graph(model)

        # Send initial greeting
        initial_message = await app.ainvoke(
            {"messages": [("system", sys_prompt), ("user", "Hi")]},
            config=config
        )
        await websocket.send_text(initial_message["messages"][-1].content)

        # Main chat loop
        while True:
            try:
                user_input = await websocket.receive_text()
                
                # Handle exit commands
                if user_input.lower() in {"quit", "exit", "q"}:
                    await _handle_disconnect(websocket)
                    return

                # Process user input
                await _process_message(app, user_input, websocket, config)

            except WebSocketDisconnect:
                await _handle_disconnect(websocket)
                return
            except Exception as e:
                await websocket.send_text(f"Error processing message: {str(e)}")

    except Exception as e:
        await websocket.send_text(f"Connection error: {str(e)}")
        await websocket.close(code=1011)  # Internal error

async def _process_message(app, user_input: str, websocket: WebSocket, config: dict) -> None:
    """Process a single user message and stream responses."""
    async for event in app.astream(
        {"messages": [("user", user_input)]},
        config,
        stream_mode="values"
    ):
        last_message = event["messages"][-1]
        
        if isinstance(last_message, AIMessage):
            if last_message.tool_calls:
                # Don't send tool processing messages to the user
                pass
            elif last_message.response_metadata.get('finish_reason') == 'stop':
                await websocket.send_text(last_message.content)
        elif isinstance(last_message, ToolMessage):
            # Don't send tool results directly to the user
            pass

async def _handle_disconnect(websocket: WebSocket) -> None:
    """Handle WebSocket disconnection gracefully."""
    await websocket.send_text("Goodbye!")
    await websocket.close(code=1000)  # Normal closure

    
