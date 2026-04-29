from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import pickle
import os
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re

nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('stopwords', quiet=True)

# Create the FastAPI app for API
api_app = FastAPI(title="Spam Detection API")

api_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "..", "model")
MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")
VECTORIZER_PATH = os.path.join(MODEL_DIR, "vectorizer.pkl")
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")

model = None
vectorizer = None

def preprocess_text(text: str) -> str:
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]
    return " ".join(tokens)

@api_app.on_event("startup")
def load_artifacts():
    global model, vectorizer
    if not os.path.exists(MODEL_PATH) or not os.path.exists(VECTORIZER_PATH):
        print("Warning: Model or vectorizer not found.")
        return
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    with open(VECTORIZER_PATH, "rb") as f:
        vectorizer = pickle.load(f)
    print("Model and Vectorizer loaded successfully.")

class PredictionRequest(BaseModel):
    message: str

class PredictionResponse(BaseModel):
    prediction: str
    confidence: float
    keywords: list[str]
    reasons: list[str] = []

SPAM_INDICATORS = {
    'win', 'free', 'urgent', 'offer', 'prize', 'cash', 'money',
    'claim', 'guaranteed', 'credit', 'click', 'link', 'account',
    'suspended', 'update', 'verify', 'winner', 'selected', 'awarded',
    'bonus', 'txt', 'text', 'call', 'reply', 'stop', 'msg',
    'password', 'otp', 'login', 'unauthorized', 'bank', 'crypto',
    'bitcoin', 'wallet', 'alert', 'security', 'compromised', 'transfer'
}

@api_app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    if model is None or vectorizer is None:
        raise HTTPException(status_code=500, detail="Model is not loaded.")
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    clean_text = preprocess_text(request.message)
    vectorized_text = vectorizer.transform([clean_text])
    probs = model.predict_proba(vectorized_text)[0]
    prob_ham, prob_spam = probs[0], probs[1]

    reasons = []
    if re.search(r'https?://\S+|www\.\S+', request.message):
        reasons.append("Contains a Suspicious Link (URL)")
    if re.search(r'\S+@\S+\.\S+', request.message):
        reasons.append("Contains an Email Address")
    if re.search(r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', request.message):
        reasons.append("Contains a Phone Number")

    tokens = set(word_tokenize(request.message.lower().translate(str.maketrans('', '', string.punctuation))))
    found_keywords = list(tokens.intersection(SPAM_INDICATORS))
    if found_keywords:
        reasons.append(f"Found {len(found_keywords)} fraud-related keywords")

    heuristic_score = 0
    if "Contains a Suspicious Link (URL)" in reasons:
        heuristic_score += 0.35
    if "Contains a Phone Number" in reasons:
        heuristic_score += 0.1
    if "Contains an Email Address" in reasons:
        heuristic_score += 0.1
    heuristic_score += (len(found_keywords) * 0.05)

    final_spam_prob = min(1.0, prob_spam + heuristic_score)
    final_ham_prob = max(0.0, prob_ham - heuristic_score)

    prediction_val = 1 if final_spam_prob > 0.5 else 0
    label = "Spam" if prediction_val == 1 else "Not Spam"

    if prediction_val == 1:
        confidence = round(final_spam_prob * 100, 1)
        if not reasons:
            reasons.append("Machine Learning model detected spam patterns")
    else:
        total = final_ham_prob + final_spam_prob
        norm_ham = final_ham_prob / total if total > 0 else 1.0
        confidence = round(norm_ham * 100, 1)
        reasons = ["Message appears normal"]

    return PredictionResponse(prediction=label, confidence=confidence, keywords=found_keywords, reasons=reasons)

# Create the main app that combines API + SPA
from starlette.routing import Mount, Route
from starlette.responses import FileResponse as StarletteFileResponse
from starlette.staticfiles import StaticFiles as StarletteStaticFiles
from starlette.applications import Starlette

# SPA handler
async def serve_spa(scope, receive, send):
    path = scope.get("path", "/")
    file_path = os.path.join(FRONTEND_DIR, path.lstrip("/"))
    
    # Try to serve the file directly
    if os.path.exists(file_path) and os.path.isfile(file_path):
        response = StarletteFileResponse(file_path)
        await response(scope, receive, send)
        return
    
    # SPA fallback
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        response = StarletteFileResponse(index_path)
        await response(scope, receive, send)
        return
    
    # 404
    from starlette.responses import JSONResponse as StarletteJSONResponse
    response = StarletteJSONResponse({"detail": "Not Found"}, status_code=404)
    await response(scope, receive, send)

# Create the combined app
routes = [
    Mount("/api", app=api_app),
    Route("/{path:path}", endpoint=serve_spa),
]

app = Starlette(debug=True, routes=routes)
