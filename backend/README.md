# Real Estate Platform — Backend API

FastAPI backend for a property listing platform with Google OAuth, PostGIS geospatial queries, Cloudinary image uploads, and Gemini AI chatbot. Uses **Supabase** (hosted PostgreSQL + PostGIS).

## Quick Start

### 1. Install Dependencies

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Fill in all credentials (see **How to Get Credentials** below).

### 3. Run Migrations

```bash
alembic upgrade head
```

### 4. Start the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs: **http://localhost:8000/docs**

---

## How to Get All Credentials

### 🟢 Supabase (DATABASE_URL)

1. Go to [https://supabase.com](https://supabase.com) → **Start your project**
2. Create a new project — pick a name, set a **database password**, choose a region
3. Wait for the project to finish provisioning
4. Go to **Project Settings** → **Database**
5. Under **Connection string** → select **URI** tab
6. Copy the URI and replace `[YOUR-PASSWORD]` with your database password
7. Change the prefix from `postgresql://` to `postgresql+asyncpg://` for async support
8. **Enable PostGIS**: Go to **Database** → **Extensions** → search for `postgis` → toggle it **ON**

```
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@db.XXXXX.supabase.co:5432/postgres
```

> **Tip:** Use port `5432` (direct connection). If you face connection issues, try port `6543` (connection pooler) instead.

---

### 🔵 Google OAuth (GOOGLE_CLIENT_ID & GOOGLE_CLIENT_SECRET)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Navigate to **APIs & Services** → **Credentials**
4. Click **+ CREATE CREDENTIALS** → **OAuth client ID**
5. If prompted, configure the **OAuth consent screen** first:
   - User Type: **External**
   - App name, email, etc. → fill in basics → **Save**
6. Back in Credentials → **OAuth client ID**:
   - Application type: **Web application**
   - **Authorized redirect URIs**: add `http://localhost:8000/auth/google/callback`
7. Copy the **Client ID** and **Client Secret**

```
GOOGLE_CLIENT_ID=123456789-xxxxxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xxxxxxxxxxxxx
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
```

---

### 🟠 Cloudinary (Image Uploads)

1. Go to [https://cloudinary.com](https://cloudinary.com) → **Sign Up Free**
2. After login, go to the **Dashboard**
3. You'll see **Cloud Name**, **API Key**, and **API Secret** right on the dashboard

```
CLOUDINARY_CLOUD_NAME=dxxxxxxxxx
CLOUDINARY_API_KEY=123456789012345
CLOUDINARY_API_SECRET=xxxxxxxxxxxxxxxxxxxxxx
```

---

### 🟣 Gemini API Key (AI Chatbot)

1. Go to [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. Click **Create API Key**
3. Select your Google Cloud project (or create one)
4. Copy the generated key

```
GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

---

### 🔐 JWT_SECRET

Generate a random string. You can use:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py             # Pydantic settings
│   ├── database.py           # Async SQLAlchemy engine
│   ├── auth/
│   │   ├── router.py         # /auth routes (Google OAuth, logout)
│   │   ├── dependencies.py   # get_current_user, require_role
│   │   ├── jwt.py            # JWT encode/decode
│   │   └── oauth.py          # Authlib Google client
│   ├── models/
│   │   ├── base.py           # Declarative base
│   │   ├── user.py           # User model
│   │   ├── listing.py        # Listing model
│   │   ├── broker.py         # Broker + BrokerAssignment
│   │   ├── wishlist.py       # Wishlist model
│   │   └── token_blacklist.py # JWT blacklist (replaces Redis)
│   ├── schemas/
│   │   ├── common.py         # APIResponse wrapper
│   │   ├── user.py           # User schemas
│   │   ├── listing.py        # Listing schemas
│   │   ├── broker.py         # Broker schemas
│   │   ├── wishlist.py       # Wishlist schemas
│   │   └── chat.py           # Chat schemas
│   └── routers/
│       ├── users.py          # /users routes
│       ├── listings.py       # /listings routes
│       ├── brokers.py        # /brokers routes
│       ├── wishlist.py       # /wishlist routes
│       ├── chat.py           # /chat routes
│       └── admin.py          # /admin routes
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 001_initial_schema.py
├── alembic.ini
├── docker-compose.yml        # Optional (for local Postgres only)
├── requirements.txt
├── .env.example
└── README.md
```

## API Modules

| Module | Prefix | Description |
|---|---|---|
| Auth | `/auth` | Google OAuth login, JWT, logout |
| Users | `/users` | Profile management, onboarding |
| Listings | `/listings` | CRUD, filters, image upload, auto broker assignment |
| Brokers | `/brokers` | Registration, verification, assignments |
| Wishlist | `/wishlist` | Add/remove/list saved listings |
| Chat | `/chat` | AI property assistant (Gemini) |
| Admin | `/admin` | User/listing/broker management |
