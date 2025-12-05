"""
Gemini Chat UI - FastAPI + WebSocket Interface.

Provides a real-time chat interface for Gemini API
conversations integrated into the content farm dashboard.
"""

import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None


app = FastAPI(title="Gemini Chat UI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# MODELS
# =============================================================================

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None


class ChatSession:
    """Manages a Gemini chat session."""

    def __init__(self, model_name: str = "gemini-pro"):
        self.model_name = model_name
        self.history: List[ChatMessage] = []
        self._chat = None
        self._model = None

    def configure(self, api_key: str = None):
        """Configure Gemini API."""
        if not GENAI_AVAILABLE:
            return False

        key = api_key or os.getenv("GOOGLE_API_KEY")
        if not key:
            return False

        genai.configure(api_key=key)
        self._model = genai.GenerativeModel(self.model_name)
        self._chat = self._model.start_chat()
        return True

    async def send_message(self, content: str) -> str:
        """Send a message and get response."""
        # Add user message to history
        self.history.append(ChatMessage(
            role="user",
            content=content,
            timestamp=datetime.utcnow().isoformat()
        ))

        if not self._chat:
            # Return mock response if not configured
            response = f"[Mock] Received: {content}"
        else:
            try:
                response = self._chat.send_message(content)
                response = response.text
            except Exception as e:
                response = f"Error: {str(e)}"

        # Add assistant response to history
        self.history.append(ChatMessage(
            role="assistant",
            content=response,
            timestamp=datetime.utcnow().isoformat()
        ))

        return response

    def get_history(self) -> List[Dict[str, Any]]:
        """Get chat history."""
        return [msg.dict() for msg in self.history]

    def clear_history(self):
        """Clear chat history."""
        self.history = []
        if self._model:
            self._chat = self._model.start_chat()


# Global session manager
sessions: Dict[str, ChatSession] = {}


def get_or_create_session(session_id: str) -> ChatSession:
    """Get or create a chat session."""
    if session_id not in sessions:
        session = ChatSession()
        session.configure()
        sessions[session_id] = session
    return sessions[session_id]


# =============================================================================
# ROUTES
# =============================================================================

@app.get("/", response_class=HTMLResponse)
async def chat_ui():
    """Serve the chat UI."""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gemini Chat - Content Farm</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 100%);
            color: #fff;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }

        .header {
            background: rgba(0, 255, 136, 0.1);
            border-bottom: 1px solid rgba(0, 255, 136, 0.3);
            padding: 1rem 2rem;
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .header h1 {
            background: linear-gradient(90deg, #00ff88, #00d4ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 1.5rem;
        }

        .status {
            margin-left: auto;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #00ff88;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .chat-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            max-width: 900px;
            margin: 0 auto;
            width: 100%;
            padding: 1rem;
        }

        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 1rem;
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }

        .message {
            max-width: 80%;
            padding: 1rem 1.25rem;
            border-radius: 1rem;
            animation: fadeIn 0.3s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .message.user {
            align-self: flex-end;
            background: linear-gradient(135deg, #00ff88 0%, #00d4ff 100%);
            color: #000;
            border-bottom-right-radius: 0.25rem;
        }

        .message.assistant {
            align-self: flex-start;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-bottom-left-radius: 0.25rem;
        }

        .message pre {
            background: rgba(0, 0, 0, 0.3);
            padding: 0.75rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
            overflow-x: auto;
        }

        .input-container {
            display: flex;
            gap: 0.75rem;
            padding: 1rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 1rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        #message-input {
            flex: 1;
            background: transparent;
            border: none;
            color: #fff;
            font-size: 1rem;
            padding: 0.75rem;
            outline: none;
        }

        #message-input::placeholder {
            color: rgba(255, 255, 255, 0.5);
        }

        #send-btn {
            background: linear-gradient(135deg, #00ff88 0%, #00d4ff 100%);
            border: none;
            color: #000;
            padding: 0.75rem 1.5rem;
            border-radius: 0.5rem;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, opacity 0.2s;
        }

        #send-btn:hover {
            transform: scale(1.05);
        }

        #send-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .typing {
            display: flex;
            gap: 0.25rem;
            padding: 0.5rem;
        }

        .typing span {
            width: 8px;
            height: 8px;
            background: #00ff88;
            border-radius: 50%;
            animation: typing 1.4s infinite;
        }

        .typing span:nth-child(2) { animation-delay: 0.2s; }
        .typing span:nth-child(3) { animation-delay: 0.4s; }

        @keyframes typing {
            0%, 100% { opacity: 0.3; transform: translateY(0); }
            50% { opacity: 1; transform: translateY(-5px); }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>✨ Gemini Chat</h1>
        <span style="color: #888;">Content Farm AI Assistant</span>
        <div class="status">
            <div class="status-dot"></div>
            <span id="status-text">Connected</span>
        </div>
    </div>

    <div class="chat-container">
        <div class="messages" id="messages">
            <div class="message assistant">
                👋 Hello! I'm your Content Farm AI assistant powered by Gemini.
                I can help you with image generation prompts, trend analysis,
                workflow optimization, and more!
            </div>
        </div>

        <div class="input-container">
            <input type="text" id="message-input" placeholder="Ask me anything..." autofocus>
            <button id="send-btn">Send</button>
        </div>
    </div>

    <script>
        const messagesDiv = document.getElementById('messages');
        const input = document.getElementById('message-input');
        const sendBtn = document.getElementById('send-btn');
        const statusText = document.getElementById('status-text');

        // Generate session ID
        const sessionId = 'session_' + Math.random().toString(36).substring(7);

        // WebSocket connection
        let ws;

        function connect() {
            ws = new WebSocket(`ws://${window.location.host}/ws/${sessionId}`);

            ws.onopen = () => {
                statusText.textContent = 'Connected';
                document.querySelector('.status-dot').style.background = '#00ff88';
            };

            ws.onclose = () => {
                statusText.textContent = 'Disconnected';
                document.querySelector('.status-dot').style.background = '#ff4444';
                setTimeout(connect, 3000);
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                removeTypingIndicator();
                addMessage(data.content, 'assistant');
                sendBtn.disabled = false;
            };
        }

        connect();

        function addMessage(content, role) {
            const msg = document.createElement('div');
            msg.className = `message ${role}`;
            msg.innerHTML = formatContent(content);
            messagesDiv.appendChild(msg);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        function formatContent(content) {
            // Basic markdown-like formatting
            return content
                .replace(/```([\s\S]*?)```/g, '<pre>$1</pre>')
                .replace(/`([^`]+)`/g, '<code>$1</code>')
                .replace(/\n/g, '<br>');
        }

        function addTypingIndicator() {
            const typing = document.createElement('div');
            typing.className = 'message assistant typing-indicator';
            typing.innerHTML = '<div class="typing"><span></span><span></span><span></span></div>';
            messagesDiv.appendChild(typing);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        function removeTypingIndicator() {
            const indicator = messagesDiv.querySelector('.typing-indicator');
            if (indicator) indicator.remove();
        }

        function sendMessage() {
            const content = input.value.trim();
            if (!content || sendBtn.disabled) return;

            addMessage(content, 'user');
            addTypingIndicator();

            ws.send(JSON.stringify({ content }));

            input.value = '';
            sendBtn.disabled = true;
        }

        sendBtn.onclick = sendMessage;
        input.onkeypress = (e) => {
            if (e.key === 'Enter') sendMessage();
        };
    </script>
</body>
</html>
"""


@app.websocket("/ws/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for chat."""
    await websocket.accept()

    session = get_or_create_session(session_id)

    try:
        while True:
            data = await websocket.receive_json()
            content = data.get("content", "")

            # Get response from Gemini
            response = await session.send_message(content)

            await websocket.send_json({
                "role": "assistant",
                "content": response
            })

    except WebSocketDisconnect:
        pass


@app.get("/api/history/{session_id}")
async def get_history(session_id: str):
    """Get chat history for a session."""
    if session_id not in sessions:
        raise HTTPException(404, "Session not found")
    return sessions[session_id].get_history()


@app.post("/api/clear/{session_id}")
async def clear_history(session_id: str):
    """Clear chat history for a session."""
    if session_id in sessions:
        sessions[session_id].clear_history()
    return {"status": "cleared"}


@app.get("/api/models")
async def list_models():
    """List available Gemini models."""
    if not GENAI_AVAILABLE:
        return {"models": [], "error": "google-generativeai not installed"}

    try:
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY", ""))
        models = [m.name for m in genai.list_models() if "generate" in m.supported_generation_methods]
        return {"models": models}
    except Exception as e:
        return {"models": [], "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7861)
