# Enterprise Carbon Tracker - Subsystem 1 Backend

This backend implements:
- Login and registration
- JWT-based authentication
- Enterprise profile management
- Department management
- OpenAI API integration support

## 1) Go to the backend folder

```bash
cd backend
```

## 2) Create a virtual environment

```bash
python -m venv .venv
```

## 3) Activate the virtual environment

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

If activation is blocked by PowerShell execution policy, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate again:

```powershell
.\.venv\Scripts\Activate.ps1
```

## 4) Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 5) Create .env from example

```bash
copy .env.example .env
```

If you are on macOS/Linux:

```bash
cp .env.example .env
```

## 6) Set your secret and OpenAI key in .env

Open `.env` and update it:

```env
SECRET_KEY=change-me-to-a-strong-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_BASE_URL=
```

Important:
- Replace `SECRET_KEY` with a real secret string
- Replace `OPENAI_API_KEY` with your actual OpenAI key
- If you do not need OpenAI yet, the app can still start, but AI features will not work until the key is set

## 7) Start the backend

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 8) Open Swagger UI

Open these URLs in your browser:

- http://localhost:8000/docs
- http://localhost:8000/redoc

## 9) Health check

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "service": "enterprise-carbon-tracker"
}
```

## Supported endpoints

### Register

`POST /register`

Request body:

```json
{
  "email": "admin@example.com",
  "password": "Password123",
  "company_name": "GreenWorks Ltd",
  "industry": "Manufacturing"
}
```

### Login

`POST /login`

Request body:

```json
{
  "email": "admin@example.com",
  "password": "Password123"
}
```

### Get profile

`GET /profile`

Headers:

```http
Authorization: Bearer <token>
```

### Update profile

`PUT /profile`

Headers:

```http
Authorization: Bearer <token>
```

Request body:

```json
{
  "company_name": "GreenWorks Ltd",
  "industry": "Manufacturing",
  "address": "123 Sustainability Ave",
  "city": "Singapore",
  "state": "Central",
  "postal_code": "018970",
  "country": "Singapore",
  "website": "https://greenworks.example",
  "phone": "+65 9123 4567"
}
```

### Get departments

`GET /departments`

Headers:

```http
Authorization: Bearer <token>
```

### Create department

`POST /departments`

Headers:

```http
Authorization: Bearer <token>
```

Request body:

```json
{
  "name": "Operations",
  "description": "Carbon tracking and facility management"
}
```

## Notes

- Passwords are stored with bcrypt hashing
- JWT contains the `enterprise_id`
- Protected routes enforce enterprise-level tenant isolation
- This uses an in-memory store for local/demo development
- OpenAI support is included in the backend service layer for AI features