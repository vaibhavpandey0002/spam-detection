# Spam Detection System

An end-to-end Machine Learning project to classify text messages as Spam or Ham (Not Spam) using Natural Language Processing (NLP) and a Logistic Regression model.

## 🌟 Project Features

- **Machine Learning Pipeline**: Data preprocessing (NLTK), TF-IDF vectorization, and Logistic Regression with 5-fold cross-validation.
- **FastAPI Backend**: A highly performant API to serve the trained model.
- **Modern UI**: A responsive, dark-mode ready web interface built with HTML, Tailwind CSS, and Vanilla JavaScript.
- **Performance Analysis**: Includes Precision, Recall, F1-Score, and a Confusion Matrix heatmap.

## 📂 Folder Structure

```text
/project
│── /backend
│   ├── app.py                  # FastAPI application
│   └── requirements.txt        # Backend dependencies
│── /frontend
│   ├── index.html              # UI Structure
│   └── script.js               # UI Logic & API call
│── /model
│   ├── download_data.py        # Fetches UCI SMS Spam dataset
│   ├── train.py                # ML pipeline (training & export)
│   ├── requirements.txt        # Model dependencies
│   ├── model.pkl               # Saved ML model (generated)
│   ├── vectorizer.pkl          # Saved TF-IDF vectorizer (generated)
│   └── confusion_matrix.png    # Evaluation heatmap (generated)
└── README.md
```

## 🚀 How to Run Locally

### 1. Train the Model

1. Navigate to the `model` directory:
   ```bash
   cd model
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Download the dataset:
   ```bash
   python download_data.py
   ```
4. Train the model (this will generate `model.pkl` and `vectorizer.pkl`):
   ```bash
   python train.py
   ```

### 2. Start the Backend API

1. Navigate to the `backend` directory:
   ```bash
   cd ../backend
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the FastAPI server:
   ```bash
   uvicorn app:app --reload
   ```
   The API will be running at `http://127.0.0.1:8000`.

### 3. Open the Frontend

Simply open `frontend/index.html` in your web browser. You can double-click the file or use a live server extension in VS Code.

## ☁️ Deployment Steps

### Deploying the Backend (Render / Railway)

1. Push your code to a GitHub repository.
2. Sign in to [Render](https://render.com/) or [Railway](https://railway.app/).
3. Create a new **Web Service** and connect your repository.
4. Set the Root Directory to `backend`.
5. Set the Build Command to `pip install -r requirements.txt`.
6. Set the Start Command to `uvicorn app:app --host 0.0.0.0 --port $PORT`.
7. Note: Make sure the `model.pkl` and `vectorizer.pkl` are committed to your repo, or add a build step to train them on the server.

### Deploying the Frontend (Netlify / Vercel)

1. Go to [Netlify](https://www.netlify.com/) or [Vercel](https://vercel.com/).
2. Create a new site from your GitHub repository.
3. Set the Root Directory to `frontend`.
4. Leave build command empty.
5. Deploy! 
*(Note: Update the `fetch` URL in `script.js` to point to your deployed backend URL instead of localhost).*

## 📊 Evaluation Results

The Logistic Regression model was evaluated using a 5-fold cross-validation approach and achieved high accuracy. Key metrics calculated include:
- **Accuracy**: Measures overall correctness.
- **Precision**: Measures how many of the predicted spams were actually spam (minimizes false positives).
- **Recall**: Measures how many actual spams were detected (minimizes false negatives).
- **F1-Score**: Harmonic mean of Precision and Recall.

Check the `confusion_matrix.png` in the `model` folder for a visual representation of the model's performance on the test set.
