from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from model_logic import predict_cluster
import pandas as pd
from datetime import datetime
import os
import requests
import traceback

# ---------------------------------------------------
# BASIC SETUP
# ---------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "user_usage_log.csv")

print("====================================")
print("FASTAPI BOOTING")
print("BASE_DIR:", BASE_DIR)
print("LOG_FILE:", LOG_FILE)
print("====================================")

# ---------------------------------------------------
# APP INIT
# ---------------------------------------------------
app = FastAPI()

# ---------------------------------------------------
# CORS
# ---------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "https://water-pattern-detection.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("CORS middleware loaded")

# ---------------------------------------------------
# AI CONFIG
# ---------------------------------------------------
COHERE_API_KEY = os.getenv("COHERE_API_KEY", "")
print("DEBUG → COHERE_API_KEY present:", bool(COHERE_API_KEY))

# ---------------------------------------------------
# ROOT
# ---------------------------------------------------
@app.get("/")
def home():
    return {"message": "Smart Water Clustering API Running!"}

# ---------------------------------------------------
# PREDICT
# ---------------------------------------------------
@app.post("/predict")
def predict(data: dict):
    usage = float(data["usage"])
    return predict_cluster(usage)

# ---------------------------------------------------
# LOG USAGE
# ---------------------------------------------------
@app.post("/log-usage")
def log_usage(data: dict):
    usage = float(data["usage"])
    today = datetime.today()

    if os.path.exists(LOG_FILE):
        df = pd.read_csv(LOG_FILE)
        offset = len(df)
    else:
        offset = 0

    new_date = (today + pd.Timedelta(days=offset)).strftime("%Y-%m-%d")
    cluster = predict_cluster(usage)["cluster"]

    row = {"date": new_date, "usage": usage, "cluster": cluster}

    df = pd.concat([pd.read_csv(LOG_FILE)] if os.path.exists(LOG_FILE) else [] + [pd.DataFrame([row])],
                   ignore_index=True) if os.path.exists(LOG_FILE) else pd.DataFrame([row])

    df.to_csv(LOG_FILE, index=False)
    return {"message": "Logged", "entry": row}

# ---------------------------------------------------
# HISTORY
# ---------------------------------------------------
@app.get("/history")
def history(limit: int = 30):
    if not os.path.exists(LOG_FILE):
        return {"history": []}

    df = pd.read_csv(LOG_FILE).tail(limit)
    return {"history": df.to_dict(orient="records")}

# ---------------------------------------------------
# SUMMARY
# ---------------------------------------------------
@app.get("/summary")
def summary():
    try:
        if not os.path.exists(LOG_FILE):
            return {"has_data": False}

        df = pd.read_csv(LOG_FILE)
        if df.empty:
            return {"has_data": False}

        avg = float(df["usage"].mean())
        latest = float(df.iloc[-1]["usage"])

        return {
            "has_data": True,
            "average_usage": avg,
            "latest_usage": latest,
            "is_spike": latest > avg * 1.5,
            "suspected_leak": latest > avg * 1.5 and latest > 100,
            "efficiency_level": predict_cluster(latest)["description"],
        }

    except Exception:
        traceback.print_exc()
        return {"has_data": False}

# ---------------------------------------------------
# AI INSIGHTS (FIXED)
# ---------------------------------------------------
@app.get("/ai-insights")
def ai_insights(limit: int = 30):
    print("AI-INSIGHTS called")

    if not COHERE_API_KEY:
        return {"insight": "AI service not configured. API key missing."}

    try:
        if not os.path.exists(LOG_FILE):
            return {"insight": "Not enough data to analyze."}

        df = pd.read_csv(LOG_FILE).tail(limit)
        if len(df) < 3:
            return {"insight": "Not enough data to analyze."}

        avg = df["usage"].mean()
        latest = df.iloc[-1]["usage"]

        history_text = "\n".join(
            f"{row['date']}: {row['usage']} L"
            for _, row in df.iterrows()
        )

        prompt = f"""
You are an analytical assistant generating a structured water-usage report.
Base every statement strictly on the data provided.
CRITICAL OUTPUT RULES (must follow strictly):
- Output MUST be plain text only
- Do NOT use markdown of any kind
- Do NOT use *, **, _, #, -, or bullet symbols
- Do NOT bold, italicize, or emphasize any word
- Do NOT use lists with symbols
- Use only normal sentences and paragraph breaks
- Section titles must be plain uppercase text followed by a colon
- Do not decorate or stylize text in any way

DATA (use only this data):
Average usage: {avg:.2f} L/day
Latest usage: {latest:.2f} L
Efficiency status: {predict_cluster(latest)["description"]}
Spike detected: {latest > avg * 1.5}
Leak suspected: {latest > avg * 1.5 and latest > 100}

Daily history:
{history_text}

STRUCTURE (follow exactly):

OVERALL SUMMARY:
Write one long paragraph (6–8 sentences) describing overall behavior and efficiency.

USAGE PATTERNS AND INSIGHTS:
Write one detailed paragraph describing patterns, spikes, and irregularities with dates and values.

RISK ASSESSMENT:
Write one paragraph explaining risks based strictly on the data.

GRAPH INTERPRETATION:
Write one paragraph explaining what the usage graph would visually show.

ACTIONABLE SUGGESTIONS:
Write one paragraph containing 3–5 suggestions written as full sentences.
Do NOT number them.
Do NOT use bullet points.

Do not add any other sections.
Do not ask questions.
Do not include disclaimers.
"""

        response = requests.post(
            "https://api.cohere.ai/v1/chat",
            headers={
                "Authorization": f"Bearer {COHERE_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "command-a-03-2025",
                "message": prompt,   # 🔥 THIS IS THE FIX
                "temperature": 0.5,
            },
            timeout=30,
        )

        print("Cohere status:", response.status_code)
        print("Cohere raw:", response.text)

        data = response.json()

        insight = data["text"]  # Cohere returns plain text here

        return {"insight": insight}

    except Exception:
        traceback.print_exc()
        return {"insight": "AI service is temporarily unavailable."}













from pydantic import BaseModel

class QuestionRequest(BaseModel):
    question: str


@app.post("/ai-question")
def ai_question(req: QuestionRequest, limit: int = 30):
    if not COHERE_API_KEY:
        return {"answer": "AI service not configured."}

    if not os.path.exists(LOG_FILE):
        return {"answer": "Not enough data available to answer questions."}

    df = pd.read_csv(LOG_FILE).tail(limit)
    if df.empty:
        return {"answer": "No usage data found."}

    avg = df["usage"].mean()
    latest = df.iloc[-1]["usage"]

    history_text = "\n".join(
        f"{row['date']}: {row['usage']} L"
        for _, row in df.iterrows()
    )

    prompt = f"""
You are answering a user's question about their household water usage.

DATA CONTEXT:
Average usage: {avg:.2f} L/day
Latest usage: {latest:.2f} L
Efficiency: {predict_cluster(latest)["description"]}

Usage history:
{history_text}

USER QUESTION:
{req.question}

ANSWER RULES:
- Answer strictly using the data provided
- Be clear and explanatory
- Do not use markdown
- Do not exaggerate
- Keep response focused on the question
"""

    try:
        response = requests.post(
            "https://api.cohere.ai/v1/chat",
            headers={
                "Authorization": f"Bearer {COHERE_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "command-a-03-2025",
                "message": prompt,
                "temperature": 0.4,
            },
            timeout=30,
        )

        data = response.json()
        return {"answer": data.get("text", "Could not generate an answer.")}

    except Exception as e:
        print("AI QUESTION ERROR:", e)
        return {"answer": "AI service is temporarily unavailable."}
