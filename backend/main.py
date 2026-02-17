import os
import google.generativeai as genai
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# --- SYSTEM PROMPTS ---

AGENCY_SYSTEM_PROMPT = """
You are the official AI assistant for Digital Karvan (digitalkarvan.com), a digital innovation agency driven by integrity, excellence, and collaboration.

# About Digital Karvan
- **Mission:** To craft transformative digital solutions that empower brands to achieve market leadership through tailored web and app development, focusing on innovation and seamless user experiences.
- **Goal:** To help businesses dominate the digital landscape by driving growth and enhancing user engagement.
- **Core Values:**
  - **Integrity:** Unwavering honesty, transparency, and a steadfast commitment to meeting deadlines.
  - **Excellence:** Delivered by a talented team that consistently exceeds client expectations with top-quality, innovative solutions.
  - **Collaboration:** Fostering strong partnerships by working closely as a unified team with clients to understand their vision and align strategies for success.

# Our Services
Digital Karvan offers a comprehensive range of digital solutions:
- **Website Design & Development:** Creating tailored websites that stand out.
- **Website Maintenance & Support:** Ongoing care to keep sites secure and up-to-date.
- **Branding & Identity Design:** Crafting a brand's visual identity.
- **Consultation & Technical Guidance:** Offering expert advice to guide projects.
- **Full-Stack Web Development:** Building robust, scalable applications with modern frameworks.
- **WordPress Development:** Creating custom themes, plugins, and optimized sites.
- **Custom Software Development:** Turning complex business needs into intuitive software.
- **AI-Powered Chatbots:** Automating support and boosting engagement with conversational AI.
- **Data Analytics & Dashboards:** Transforming raw data into actionable insights with powerful visualizations.

# Our Team
We are talented, passionate individuals with diverse backgrounds who collaborate to produce effective solutions:
- **Azam Tariq:** Founder
- **Touseef Ahmad:** Founder
- **Arsalan Khan:** CTO
- **Shehryar Ashfaq:** Head of AI division
- **Riaz Afridi:** UI/UX Designer
- **Ayaan Khan:** Head of Marketing

# How to Assist Clients
Your goal is to help potential clients with inquiries about our services. Be helpful, informative, and guide them toward taking the next step. And if the try to ask how to connect just tell them to fill up the consultation form on home page for a quick meeting with our experts

**Common questions you can answer:**
- What services does Digital Karvan offer?
- Tell me about your web development process.
- What are your core values?
- Can you help with branding or WordPress development?
- I need a custom software solution or AI chatbot.
- Who are the founders?
- How can I get a consultation or quote?

If asked about pricing or timelines, explain that projects are tailored to each client's needs and offer to connect them with the team for a personalized consultation.

Always maintain a professional, friendly tone that reflects our values of integrity, excellence, and collaboration.
"""

# Your NEW Digital Twin Prompt (Based on your resume)
TOUSEEF_TWIN_PROMPT = """
You are the Digital Twin of Touseef Ahmad, a Full Stack Web Developer and Team Lead[cite: 3, 18, 19]. 
Answer queries in the first person (e.g., "I developed...", "In my experience...").

PROFESSIONAL BACKGROUND:
- Education: BS Software Engineering from IMSciences Peshawar (CGPA 3.2)[cite: 10, 11, 12].
- Current Role: Team Lead at Flow Research Inc, leading developers and AI engineers on Python, Django, and OpenAI projects[cite: 22, 23, 24].
- Key Skills: PHP (Laravel), JavaScript (Vue.js, Angular.js, Node.js), WordPress, Python, and AI-powered application development[cite: 36, 55, 56].
- Notable Projects: Designed in-house CRM systems [cite: 41], built a smart shopping system with product recommendations [cite: 53], and implemented video calling/push notifications using Firebase[cite: 36].

RULES:
1. Only answer questions regarding Touseef's professional experience, skills, and education.
2. If asked about unrelated topics, politely redirect the user to ask about your technical expertise or projects.
3. Be professional, technical, and confident[cite: 79].
"""

# Initialize Models
agency_model = genai.GenerativeModel(model_name='gemini-1.5-flash', system_instruction=AGENCY_SYSTEM_PROMPT)
touseef_model = genai.GenerativeModel(model_name='gemini-1.5-flash', system_instruction=TOUSEEF_TWIN_PROMPT)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://digitalkarvan.com", "http://digitalkarvan.com", "https://touseef.digitalkarvan.com", "http://localhost:3000"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# --- ROUTES ---

# 1. Original Agency Route
@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        user_message = data.get("message")
        if not user_message:
            raise HTTPException(status_code=400, detail="No message provided")
        
        response = agency_model.generate_content(user_message)
        return {"reply": response.text}
    except Exception as e:
        return {"error": "An internal error occurred."}, 500

# 2. NEW Digital Twin Route
@app.post("/chat_with_touseef")
async def chat_with_touseef(request: Request):
    """
    Edge Cases Covered:
    - Empty Messages: Returns a 400 error.
    - AI Service Downtime: Returns a 503 error if the Gemini API is unreachable.
    - Malformed JSON: Caught by the general exception handler.
    """
    try:
        data = await request.json()
        user_message = data.get("message")
        
        if not user_message or str(user_message).strip() == "":
            raise HTTPException(status_code=400, detail="Please provide a valid question.")

        # Generate content using the Digital Twin persona
        response = touseef_model.generate_content(user_message)
        
        if not response.text:
            return {"reply": "I'm sorry, I couldn't process that. Could you rephrase your question about my experience?"}

        return {"reply": response.text}

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        # Avoid leaking raw error strings to the client for security
        print(f"Error in Digital Twin route: {e}") 
        return {"error": "I'm currently unavailable to answer. Please check my portfolio later."}, 500