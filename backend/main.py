import os
import google.generativeai as genai
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

# 1. Configure Gemini with Agency Instructions
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# SYSTEM_PROMPT defines the chatbot's "personality" and knowledge boundaries
SYSTEM_PROMPT = """
You are the official AI assistant for Digital Karvan (digitalkarvan.com).
Your goal is to help potential clients with inquiries about our digital marketing, SEO, web development, and branding services.

RULES:
1. ONLY answer questions related to Digital Karvan, its services, or general digital marketing advice.
2. If a user asks about unrelated topics (e.g., cooking, politics, sports, or other companies), 
   politely say: "I'm sorry, I am only trained to assist with questions regarding Digital Karvan and our digital services."
3. Be professional, creative, and helpful.
4. If you don't know a specific detail about a project, ask the user to contact us via the website form.
"""

model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    system_instruction=SYSTEM_PROMPT
)

app = FastAPI()

# 2. Security: Restricted to your domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://digitalkarvan.com", "http://digitalkarvan.com"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        user_message = data.get("message")
        
        if not user_message:
            raise HTTPException(status_code=400, detail="No message provided")

        # The AI now follows the SYSTEM_PROMPT instructions
        response = model.generate_content(user_message)
        
        return {"reply": response.text}
    except Exception as e:
        return {"error": str(e)}, 500