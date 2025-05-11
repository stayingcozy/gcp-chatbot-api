from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types
from datetime import datetime
from typing import List
import json

from settings import PROJECT_ID, LOCATION, PRODUCTION, PORT, SUPASECRET
from cloud import access_secret_version, download_image_db, upload_image_db, create_signed_url, get_random_hex

app = FastAPI()

if PRODUCTION:
    origins = ["*"] # ["https://twohearts.tech"]
else:
    origins = ["http://localhost:3000"]

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

class Attachment(BaseModel):
    name: str | None = None
    contentType: str
    url: str

class Message(BaseModel):
    role: str
    content: str
    id: str
    createdAt: datetime
    parts: List[Part]
    experimental_attachments: List[Attachment] | None = None

class ChatRequest(BaseModel):
    id: str
    messages: List[Message]
    selectedChatModel: str

def load_client():
    return genai.Client(project=PROJECT_ID, location=LOCATION, vertexai=True)

@app.get("/healthcheck")
def healthcheck():
    return Response(status_code=200)

@app.get("/secretcheck")
def secretcheck():
    """ Return a hello world secret """

    # copy secret ID from secret create in google cloud console / vs code extension
    message = access_secret_version(SUPASECRET) 

    return {"message": message}
    

@app.post('/chat/blurb')
async def multimodal_generate_text(request: ChatRequest):
    """
    Generates text using the Gemini model based on the provided prompt in the POST request.
    Returns a JSON response containing the generated text.
    """
    try:   

        # split messages 
        messages = request.messages
        message = messages[-1]

        # get model
        model = request.selectedChatModel

        # sets prompt default to text content
        prompt = message.content

        if message.experimental_attachments is not None and message.experimental_attachments:
            # add image attachment
            attachment = message.experimental_attachments[-1]

            # storage bucket in supabase name 
            storageBucket = attachment.name

            # url -> bytes (download) for google client 
            imageBytes = download_image_db(storageBucket, attachment.url) 
        
            # if image bytes exist, overwrite prompt to include
            if (imageBytes):
                prompt = [
                    types.Part.from_bytes(
                        data = imageBytes,
                        mime_type = attachment.contentType
                    ),
                    message.content
                ]

        async def stream():
            for chunk in client.models.generate_content_stream(
                model=model, contents=prompt
            ):
                # Format the response according to Data Stream Protocol (useChat() from vercel ai library)
                yield  f'0:{json.dumps(chunk.text)}\n'
    
        return StreamingResponse(stream(), media_type="text/event-stream")

    except Exception as e:
        print(f"Error during text generation: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@app.post("/chat/image")
async def image_to_image(request: ChatRequest):
    '''Modify an image based on prompt. Return an Image'''

    print("Running /chat/image...")

    try:
        
        # convert request to model inputs
        model, prompt, storage_bucket, download_path = request_to_model_input(request=request)

        # send to google gemini
        gemini_response = client.models.generate_content(
            model=model, 
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE']
            )
        )

        for part in gemini_response.candidates[0].content.parts:
            if part.inline_data is not None:
                image = part.inline_data.data

        # upload response image to supabase
        if (image):
            upload_response = upload_image_db(storage_bucket=storage_bucket, upload_path=f"geminiImages/{get_random_hex()}", image_bytes=image)
        else:
            raise HTTPException(status_code=400, detail="Upload Failed")

        # if supabase upload is successful return uri (path to image in supabase)
        result = upload_response.path
        if result:
            signed_url = create_signed_url(storage_bucket=storage_bucket, result=result)
            return {"image_signed_path": signed_url, "image_full_path": result, "image_bucket": storage_bucket}
        else:
            raise HTTPException(status_code=400, detail="Result from upload failed")



    except Exception as e:
        print(f"Error while converting image to stylized image: {e}")
        raise HTTPException(status_code=500, detail=f"An error occured: {e}")


def request_to_model_input(request: ChatRequest):

    try: 
        # split messages
        messages = request.messages
        message = messages[-1]

        # get model
        model = request.selectedChatModel

        # set model default to text context
        prompt = message.content

        if message.experimental_attachments is not None and message.experimental_attachments:
            # add image attachment
            attachment = message.experimental_attachments[-1]
             
            # get supabase storage bucket
            storage_bucket = attachment.name
            download_path = attachment.url

            # url -> bytes download for google client
            image_bytes = download_image_db(storage_bucket=storage_bucket, download_path=attachment.url)

            # if image exist, overwrite prompt 
            if (image_bytes):
                prompt = [
                    types.Part.from_bytes(
                        data = image_bytes,
                        mime_type = attachment.contentType
                    ),
                    message.content
                ]

        return model, prompt, storage_bucket, download_path

    except Exception as e:
        print(f"Error while converting request to model input: {e}")
        raise HTTPException(status_code=500, detail=f"An error occured: {e}")


if __name__ == '__main__':
    import uvicorn
    client = load_client()
    uvicorn.run(app, host="0.0.0.0", port=PORT)
