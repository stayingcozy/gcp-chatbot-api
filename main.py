from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from datetime import datetime
from typing import List
import json

from settings import PROJECT_ID, LOCATION, FAST_PRODUCTION, PORT

app = FastAPI()

if not FAST_PRODUCTION:
    origins = ["http://localhost:3000"]
else:
    origins = ["https://twohearts.tech"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Part(BaseModel):
    type: str
    text: str

class Message(BaseModel):
    role: str
    content: str
    id: str
    createdAt: datetime
    parts: List[Part]

class ChatRequest(BaseModel):
    id: str
    messages: List[Message]
    selectedChatModel: str

def load_client():
    return genai.Client(project=PROJECT_ID, location=LOCATION, vertexai=True)

@app.get("/healthcheck")
def healthcheck():
    return Response(status_code=200)

@app.post('/chat/blurb')
async def generate_text(request: ChatRequest):
    """
    Generates text using the Gemini model based on the provided prompt in the POST request.
    Returns a JSON response containing the generated text.
    """
    try:   

        # Gather inputs 
        model = request.selectedChatModel
        messages = request.messages
        last_user_message = messages[-1].content

        async def stream():
            for chunk in client.models.generate_content_stream(
                model=model, contents=last_user_message
            ):
                # Format the response according to Data Stream Protocol (useChat() from vercel ai library)
                yield  f'0:{json.dumps(chunk.text)}\n'
    
        return StreamingResponse(stream(), media_type="text/event-stream")

    except Exception as e:
        print(f"Error during text generation: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

if __name__ == '__main__':
    import uvicorn
    client = load_client()
    uvicorn.run(app, host="0.0.0.0", port=PORT)
