# Tender Bharat

A FastAPI backend for managing and analyzing civil engineering tender documents. Built with FastAPI, MongoDB, and Motor.


## 📁 Project Structure

```
backend/
├── app/...
├── .env                        # MongoDB connection string and secrets
├── .gitignore                  # Ignore env files, pycache, etc.
└── requirements.txt            # Python dependencies
```


## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/tender-bharat.git
cd backend
```

### 2. Create and Activate a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On MacOS
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up .env File

Create a `.env` file in the root of the `backend/` directory:

```
MONGO_CONNECTION_STRING= your_mongodb_string
DATABASE_NAME=TenderBharat
```

### 5. Run the Server

```bash
uvicorn app.main:app --reload
```

- Server will be running at: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Docs available at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)


## 📦 API Endpoints

- `GET /` – Health check
- `GET /api/tenders/` – Fetch all tenders (JSON)
- `GET /api/tenders/:tender_Id` – Fetch tender by tender_Id (JSON)
- `GET /api/compatibility/` – Fetch all compatibility data (JSON)
- `GET /api/compatibility/:tender_Id` – Fetch compatibility data by tender_Id (JSON)
