import os
import pandas as pd
import string
import pickle
import matplotlib.pyplot as plt
import seaborn as sns

# NLTK imports
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

# Ensure NLTK resources are downloaded
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('stopwords', quiet=True)

MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(MODEL_DIR, "SMSSpamCollection")

def preprocess_text(text):
    """
    Lowercasing, removing punctuation, stopword removal, and tokenization.
    """
    # Lowercase
    text = text.lower()
    
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Tokenize
    tokens = word_tokenize(text)
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]
    
    # Rejoin to string for vectorizer (TF-IDF expects strings)
    return " ".join(tokens)

def main():
    if not os.path.exists(DATA_FILE):
        print(f"Error: Dataset {DATA_FILE} not found. Please run download_data.py first.")
        return

    print("Loading dataset...")
    # The dataset is tab-separated: Label \t Message
    df = pd.read_csv(DATA_FILE, sep='\t', header=None, names=['label', 'message'])
    
    # Convert labels to binary: spam=1, ham=0
    df['label'] = df['label'].map({'spam': 1, 'ham': 0})
    
    print("Preprocessing text data...")
    df['clean_message'] = df['message'].apply(preprocess_text)
    
    # TF-IDF Vectorization
    print("Applying TF-IDF Vectorization...")
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(df['clean_message'])
    y = df['label']
    
    # Train-test split
    print("Splitting dataset into train and test sets...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Model Development
    print("Training Logistic Regression model...")
    model = LogisticRegression(random_state=42)
    model.fit(X_train, y_train)
    
    # Cross Validation
    print("Performing 5-fold Cross Validation...")
    cv_scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
    print(f"Mean Accuracy (5-fold CV): {cv_scores.mean():.4f}")
    
    # Evaluation on Test Set
    print("\nEvaluating model on test set...")
    y_pred = model.predict(X_test)
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    print(f"Accuracy:  {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print(f"F1-score:  {f1:.4f}")
    
    # Confusion Matrix Heatmap
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(6, 4))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Not Spam (Ham)', 'Spam'], 
                yticklabels=['Not Spam (Ham)', 'Spam'])
    plt.title('Confusion Matrix')
    plt.xlabel('Predicted Label')
    plt.ylabel('True Label')
    plt.tight_layout()
    cm_path = os.path.join(MODEL_DIR, "confusion_matrix.png")
    plt.savefig(cm_path)
    print(f"\nSaved confusion matrix to {cm_path}")
    
    # Model Export
    model_path = os.path.join(MODEL_DIR, "model.pkl")
    vectorizer_path = os.path.join(MODEL_DIR, "vectorizer.pkl")
    
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
        
    with open(vectorizer_path, 'wb') as f:
        pickle.dump(vectorizer, f)
        
    print(f"Saved trained model to {model_path}")
    print(f"Saved vectorizer to {vectorizer_path}")
    
    print("\nModel training and export complete!")

if __name__ == "__main__":
    main()
