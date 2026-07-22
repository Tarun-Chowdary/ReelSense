# 🎬 ReelSense

[🌐 Visit ReelSense Live](https://reel-sense-omega.vercel.app/)

ReelSense is an intelligent movie recommendation web application that helps users discover movies based on their mood and preferences. Instead of browsing endlessly, users answer a short interactive quiz, and ReelSense generates personalized recommendations using a hybrid recommendation strategy powered by collaborative filtering, genre-based filtering, and explainable AI.

---

## 🚀 Features

- 🎭 Mood-based movie recommendation quiz
- 🤖 Intelligent recommendation engine using SVD Collaborative Filtering
- 🎯 Cold-start recommendation support for new users
- 📊 Explainable recommendations with personalized reasoning
- ⭐ Movie ratings and popularity-based ranking
- 🎨 Beautiful ticket-inspired movie recommendation UI
- 📈 Recommendation diversity and catalog coverage metrics
- 🎞️ Dynamic movie poster support via OMDb API
- 📱 Fully responsive modern interface
- ⚡ FastAPI-powered backend with REST APIs

---

## 🛠 Tech Stack

### Frontend

- HTML5
- CSS3
- Vanilla JavaScript

### Backend

- FastAPI
- Python
- Pandas

### Machine Learning

- Surprise Library
- SVD Collaborative Filtering
- Hybrid Recommendation System
- Genre-Based Ranking
- Explainable Recommendation Logic

### Dataset

- MovieLens Latest Dataset
- OMDb API (Movie Posters)

---

## 🧠 How It Works

1. User opens ReelSense.
2. A short personality and mood-based quiz is presented.
3. User answers questions regarding:
   - Mood
   - Favorite Genre
   - Movie Pace
   - Preferred Era
   - Discovery Preference
4. FastAPI processes the responses.
5. A hybrid recommendation algorithm scores every movie using:
   - Genre similarity
   - User mood
   - Movie quality
   - Popularity/Novelty balance
6. Top personalized movie recommendations are displayed with:
   - Rating
   - Genres
   - Explanation
   - Dynamic poster (OMDb)

---

## 🧠 Recommendation Algorithm

ReelSense combines multiple recommendation strategies:

- 🎯 SVD Collaborative Filtering
- 🎭 Genre-Based Filtering
- ⭐ Average Rating Ranking
- 🌍 Popularity vs Hidden Gem Balancing
- 📊 Intra-List Diversity Optimization
- 📈 Catalog Coverage Analysis

This hybrid approach helps overcome the cold-start problem while providing meaningful and diverse recommendations.

---

## 📊 Recommendation Metrics

Each recommendation list includes:

- 📈 Intra-List Diversity
- 🎯 Catalog Coverage
- ⭐ Average Movie Rating
- 💡 Explainable Recommendation Reason

These metrics help evaluate the quality and diversity of generated recommendations.

---

## 🌐 Live Website

https://reel-sense-omega.vercel.app/

---

## 📦 Installation (Local Setup)

### 1. Clone the Repository

```bash
git clone https://github.com/Tarun-Chowdary/ReelSense.git
cd ReelSense
```

---

### 2. Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

Create a `.env` file inside the backend folder:

```env
apikey=YOUR_OMDB_API_KEY
```

Run the FastAPI server:

```bash
uvicorn main:app --reload --port 8000
```

---

### 3. Frontend Setup

Open another terminal:

```bash
cd frontend
```

Run a local server using VS Code Live Server or Python:

```bash
python -m http.server 5500
```

or simply use the **Live Server** extension in VS Code.

---

## 📁 Project Structure

```text
ReelSense
│
├── backend
│   ├── main.py
│   ├── requirements.txt
│   └── .env
│
├── data
│   ├── raw
│   └── processed
│
├── frontend
│   └── index.html
│
├── models
│   └── svd_model.pkl
│
└── README.md
```

---

## 🛠 API Endpoints

| Method | Endpoint                  | Description                            |
| ------ | ------------------------- | -------------------------------------- |
| GET    | `/api/health`             | Server Health Check                    |
| POST   | `/api/quiz-recommend`     | Mood-based Movie Recommendation        |
| GET    | `/api/users`              | Available Users                        |
| GET    | `/api/movie/{movieId}`    | Movie Details                          |
| GET    | `/api/recommend/{userId}` | Collaborative Filtering Recommendation |

---

## 🛠 Troubleshooting

### Posters not loading

- Verify your OMDb API key.
- Ensure the key is activated.
- Check the `.env` file configuration.

### Backend not connecting

- Make sure FastAPI is running.
- Verify the frontend API URL points to the deployed backend.

### Dataset errors

- Ensure the MovieLens dataset is placed correctly under:

```text
data/raw
data/processed
```

### Model loading issues

Verify the trained SVD model exists:

```text
models/svd_model.pkl
```

---

## 🚀 Future Improvements

- ❤️ Favorite Movies
- 👤 User Accounts
- 🎥 Trailer Integration
- 🎬 Streaming Platform Availability
- 🌍 Multi-language Recommendations
- 🤝 Social Recommendation Sharing
- 📈 Personalized Watch History
- 🔍 Movie Search & Filters

---

## 👨‍💻 Author

**Tarun Chowdary Yegi**

- GitHub: https://github.com/Tarun-Chowdary
- LinkedIn: https://www.linkedin.com/in/taryegi/

---

## 📄 License

This project is developed for educational, research, and portfolio purposes.

---

⭐ If you enjoyed this project, consider giving it a **Star** on GitHub!
