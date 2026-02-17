import os
import google.generativeai as genai
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from slowapi import Limiter
from slowapi.util import get_remote_address

load_dotenv()

# 1. Setup Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

app = FastAPI()
limiter = Limiter(key_func=get_remote_address)

# 2. Security: Enable CORS for your WordPress domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"], # REPLACE with your WP domain
    allow_methods=["POST"],
    allow_headers=["*"],
)

@app.post("/chat")
@limiter.limit("10/minute") # Basic rate limiting
async def chat(request: Request):
    try:
        data = await request.json()
        user_message = data.get("message")
        
        if not user_message:
            raise HTTPException(status_code=400, detail="No message provided")

        # Call Gemini API
        response = model.generate_content(user_message)
        
        return {"reply": response.text}
    except Exception as e:
        return {"error": str(e)}, 500