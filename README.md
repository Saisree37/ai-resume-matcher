# 🤖 AI Resume & Job Matching System

An AI-powered full-stack application that analyzes resumes against job descriptions and provides a semantic match score, matched skills, skill gaps, resume strengths, and improvement suggestions.

---

## 🚀 Features

- 📄 Upload PDF resumes
- 🔍 Extract and clean resume text
- 📑 Identify resume sections
- 🛠️ Extract resume skills
- 💼 Create and manage job descriptions
- 🧠 Calculate semantic resume-job match score
- 🤖 Extract required job skills using an LLM
- 🔎 Retrieve relevant resume context using RAG
- ✅ Identify matched skills
- ❌ Identify missing skills
- 💪 Identify resume strengths
- 💡 Provide improvement suggestions
- 🗄️ Store jobs using PostgreSQL
- 🌐 REST API using FastAPI
- ⚛️ React frontend
- ☁️ Cloud deployment

---

## 🏗️ Architecture

```text
                    React Frontend
                          |
                          | HTTP / JSON
                          ↓
                  FastAPI Backend
                          |
             ┌────────────┼────────────┐
             ↓            ↓            ↓
        PostgreSQL      Resume       AI / RAG
          (Neon)       Processing     Pipeline
                           |            |
                           ↓            ↓
                         PDF        Embeddings
                         Text           |
                                       ↓
                                    ChromaDB
                                       |
                                       ↓
                                      LLM
                                       |
                                       ↓
                              Resume Analysis
```

---

## 🛠️ Tech Stack

### Frontend

- React
- Vite
- Axios

### Backend

- Python
- FastAPI
- Uvicorn
- SQLAlchemy
- Pydantic

### Database

- PostgreSQL
- Neon

### AI / GenAI

- LangChain
- Ollama
- Llama 3.1
- Nomic Embed Text
- ChromaDB
- Retrieval-Augmented Generation (RAG)

### Resume Processing

- PyMuPDF

---

## 📁 Project Structure

```text
ai-resume-matcher/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── database.py
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── job.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── job.py
│   │   │
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   └── jobs.py
│   │   │
│   │   └── services/
│   │       ├── __init__.py
│   │       └── resume_processor.py
│   │
│   ├── requirements.txt
│   ├── .env
│   └── .gitignore
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   ├── main.jsx
│   │   └── services/
│   │       └── api.js
│   │
│   ├── package.json
│   ├── package-lock.json
│   └── .env.example
│
├── .gitignore
├── README.md
├── package.json
└── package-lock.json
```

---

# ⚙️ Local Setup

## 1. Clone the Repository

```bash
git clone https://github.com/Saisree37/ai-resume-matcher.git
cd ai-resume-matcher
```

---

## 2. Backend Setup

Navigate to the backend:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv env
```

### Activate the Environment

Windows:

```powershell
env\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 3. Backend Environment Variables

Create:

```text
backend/.env
```

Add:

```env
DATABASE_URL=your_postgresql_connection_string
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_LLM_MODEL=llama3.1:latest
OLLAMA_EMBEDDING_MODEL=nomic-embed-text:latest
```

> Never commit your `.env` file or expose your database credentials.

---

## 4. Install Ollama Models

Make sure Ollama is installed and running locally.

Pull the required models:

```bash
ollama pull llama3.1
ollama pull nomic-embed-text
```

Verify:

```bash
ollama list
```

---

## 5. Start the Backend

From the `backend` directory:

```bash
uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger API documentation:

```text
http://127.0.0.1:8000/docs
```

---

# ⚛️ Frontend Setup

Open another terminal.

Navigate to the frontend:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Create:

```text
frontend/.env
```

Add:

```env
VITE_API_URL=http://127.0.0.1:8000
```

Start the frontend:

```bash
npm run dev
```

The Vite development server will provide the frontend URL in the terminal.

---

# 🔌 API Endpoints

## Job Management

| Method | Endpoint | Description |
|---|---|---|
| POST | `/jobs` | Create a new job |
| GET | `/jobs` | Get all jobs |
| GET | `/jobs/{job_id}` | Get a specific job |
| DELETE | `/jobs/{job_id}` | Delete a job |

---

## Resume Matching

### `POST /jobs/{job_id}/match`

Accepts a PDF resume and analyzes it against the selected job description.

Returns:

- Match Score
- Required Skills
- Matched Skills
- Skill Gaps
- Resume Strengths
- Improvement Suggestions

---

## Resume Upload

### `POST /Upload_file`

Accepts a PDF resume and extracts structured resume information.

Returns:

- Filename
- Number of pages
- Cleaned resume content
- Resume sections
- Extracted skills

---

# 🧠 AI Pipeline

```text
Resume PDF
    ↓
Text Extraction
    ↓
Text Cleaning
    ↓
Section Extraction
    ↓
Skill Extraction
    ↓
Text Chunking
    ↓
Embeddings
    ↓
ChromaDB
    ↓
Semantic Retrieval
    ↓
RAG Context
    ↓
LLM Analysis
    ↓
Final Resume-Job Analysis
```

---

# 📊 Resume-Job Matching

The system uses two AI-based approaches.

### 1. Semantic Similarity

The resume and job description are converted into embeddings using:

```text
Nomic Embed Text
```

Cosine similarity is then used to calculate a semantic match score.

---

### 2. RAG + LLM Analysis

The resume is divided into smaller chunks and stored in ChromaDB.

Relevant resume chunks are retrieved based on the job description.

The retrieved context is passed to the LLM to identify:

```text
Matched Skills
Missing Skills
Resume Strengths
Improvement Suggestions
```

This provides more meaningful analysis than relying only on a similarity score.

---

# 🗄️ Database

The application uses:

```text
PostgreSQL
     ↓
Neon
```

Job information is stored in PostgreSQL, while resume processing and AI analysis are performed during the matching request.

---

# ☁️ Deployment

### Backend

Deployed using:

```text
Render
```

### Database

Hosted using:

```text
Neon PostgreSQL
```

### Frontend

Deployed as a:

```text
Render Static Site
```

---

# 🔐 Environment Variables

Sensitive configuration is not committed to GitHub.

### Backend

```env
DATABASE_URL=
OLLAMA_BASE_URL=
OLLAMA_LLM_MODEL=
OLLAMA_EMBEDDING_MODEL=
```

### Frontend

```env
VITE_API_URL=
```

---

# 🛡️ Security

- Database credentials are stored in environment variables.
- `.env` files are excluded from Git.
- Local development configuration is separated from production configuration.
- API configuration is handled through environment variables.

---

# 🔮 Future Improvements

- User authentication
- Multiple resume management
- Resume history
- Job recommendation system
- AI-powered resume improvement
- Resume PDF generation
- Better skill normalization
- Job ranking
- Dashboard and analytics
- Production cloud AI provider
- Persistent production vector database
- Improved error handling
- Rate limiting
- User-specific resume storage

---

# 📌 Current Deployment

The application is deployed using free-tier cloud services for learning and portfolio purposes.

```text
React Frontend
      ↓
Render
      ↓
FastAPI Backend
      ↓
Neon PostgreSQL
      ↓
AI / RAG Pipeline
```

> Note: The current AI pipeline uses Ollama locally. A production deployment requires a cloud-accessible LLM and embedding provider instead of `127.0.0.1`.

---

# 👩‍💻 Author

**Saisree**

GitHub:

https://github.com/Saisree37