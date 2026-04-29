from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import pickle
import os
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re

# Ensure NLTK resources are available
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('stopwords', quiet=True)

app = FastAPI(title="Spam Detection API")

# Create a sub-application for API routes
from fastapi import APIRouter
api_router = APIRouter(prefix="/api")

# Include the API router
app.include_router(api_router)

# Enable CORS for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production to match your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths to the model and vectorizer
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "..", "model")
MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")
VECTORIZER_PATH = os.path.join(MODEL_DIR, "vectorizer.pkl")

# Global variables to hold the loaded model and vectorizer
model = None
vectorizer = None

def preprocess_text(text: str) -> str:
    """Same preprocessing as used during training."""
    # Lowercase
    text = text.lower()
    
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Tokenize
    tokens = word_tokenize(text)
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]
    
    # Rejoin to string
    return " ".join(tokens)

@app.on_event("startup")
def load_artifacts():
    global model, vectorizer
    if not os.path.exists(MODEL_PATH) or not os.path.exists(VECTORIZER_PATH):
        print("Warning: Model or vectorizer not found. Please run train.py first.")
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

@api_router.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    if model is None or vectorizer is None:
        raise HTTPException(status_code=500, detail="Model is not loaded. Please train the model first.")
        
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
        
    # Preprocess the input text
    clean_text = preprocess_text(request.message)
    
    # Vectorize
    vectorized_text = vectorizer.transform([clean_text])
    
    # Predict probabilities (0 = Ham, 1 = Spam)
    probs = model.predict_proba(vectorized_text)[0]
    prob_ham, prob_spam = probs[0], probs[1]
    
    # Heuristic Detection for "Outside" text
    reasons = []
    
    # Regex for URLs, emails, phones
    if re.search(r'https?://\S+|www\.\S+', request.message):
        reasons.append("Contains a Suspicious Link (URL)")
    
    if re.search(r'\S+@\S+\.\S+', request.message):
        reasons.append("Contains an Email Address")
        
    if re.search(r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', request.message):
        reasons.append("Contains a Phone Number")
    
    # Extract spam-indicative keywords
    tokens = set(word_tokenize(request.message.lower().translate(str.maketrans('', '', string.punctuation))))
    found_keywords = list(tokens.intersection(SPAM_INDICATORS))
    
    if found_keywords:
        reasons.append(f"Found {len(found_keywords)} fraud-related keywords")
        
    # Hybrid Scoring: Boost spam probability based on heuristics
    heuristic_score = 0
    if "Contains a Suspicious Link (URL)" in reasons:
        heuristic_score += 0.35  # Links are highly suspicious in unsolicited messages
    if "Contains a Phone Number" in reasons:
        heuristic_score += 0.1
    if "Contains an Email Address" in reasons:
        heuristic_score += 0.1
    heuristic_score += (len(found_keywords) * 0.05)
    
    final_spam_prob = min(1.0, prob_spam + heuristic_score)
    final_ham_prob = max(0.0, prob_ham - heuristic_score)
    
    # Determine label and confidence
    prediction_val = 1 if final_spam_prob > 0.5 else 0
    label = "Spam" if prediction_val == 1 else "Not Spam"
    
    if prediction_val == 1:
        confidence = round(final_spam_prob * 100, 1)
        if not reasons:
            reasons.append("Machine Learning model detected spam patterns")
    else:
        # Normalize ham confidence
        total = final_ham_prob + final_spam_prob
        norm_ham = final_ham_prob / total if total > 0 else 1.0
        confidence = round(norm_ham * 100, 1)
        reasons = ["Message appears normal"]
    
    return PredictionResponse(prediction=label, confidence=confidence, keywords=found_keywords, reasons=reasons)

@api_router.get("/")
def read_root():
    return {"message": "Welcome to the Spam Detection API"}

# Serve frontend static files (must be after API routes)
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
else:
    print(f"Warning: Frontend directory not found at {FRONTEND_DIR}")
