from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from typing import Optional

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

class ChatRequest(BaseModel):
    prompt: str
    model: Optional[str] = "gemini-2.0-flash"

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
        prompt = request.prompt
        model = request.model

        response = client.models.generate_content(
            model=model,
            contents=prompt
        )

        # return response.model_dump_json(indent=2)
        return response.text

    except Exception as e:
        print(f"Error during text generation: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

if __name__ == '__main__':
    import uvicorn
    client = load_client()
    uvicorn.run(app, port=PORT, reload=FAST_PRODUCTION)