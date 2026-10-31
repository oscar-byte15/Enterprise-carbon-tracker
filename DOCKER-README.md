# Enterprise Carbon Tracker — local Docker Compose setup

The bundle is an **overlay**: copy the files into the corresponding paths in the existing repository; do not replace the project's source code.

## Requirements
- Docker Desktop running (WSL2 on Windows recommended)
- Ports 5173 and 8000 must be free. Existing Windows MongoDB at 27017 may remain running.

## First run
1. Optional but recommended: copy the root `.env.example` to `.env`, and change `SECRET_KEY`. The root `.env` must NOT be committed. If OpenAI recommendations are needed, set `OPENAI_API_KEY` in that same root `.env`.
2. Run at the project root:

   ```bash
   docker compose up --build -d
   docker compose ps
   ```

3. Open React at http://localhost:5173 and FastAPI docs at http://localhost:8000/docs.
4. MongoDB Compass: `mongodb://127.0.0.1:27018` (Docker). This is separate from a directly installed MongoDB at `mongodb://127.0.0.1:27017`.

## Important
- Inside Docker, the backend uses `mongodb://mongodb:27017` (Compose service DNS).
- From Windows, Compass uses `mongodb://127.0.0.1:27018` (published port).
- Docker MongoDB data is kept in the `mongodb_data` named volume. `docker compose down` preserves it, but **`docker compose down -v` deletes it**.
- Each teammate gets independent local data, not a shared cloud database.
- Xiangping's current users/enterprises/departments are in Python memory; restarting the backend loses those accounts until Subsystem 1 migrates to persistent storage. The `enterprise_id` changes on re-registering, so existing activities may no longer appear for the new account even though MongoDB retained them.
- These Dockerfiles are for local development; production deployment needs hardened secrets, authentication, security, and proper frontend serving.

## Common commands
```bash
docker compose logs -f backend
docker compose logs -f frontend
docker compose down
docker compose up --build -d   # rebuild after editing application source
```

## Demo registration (not a pre-created account)
- Email: admin@carbontrack.com
- Password: Password123
- Company: GreenTech Solutions
- Industry: Technology

## Git
Add files in a `feature/docker-compose` branch and create a pull request after testing. `.env` must remain ignored. Root `.gitignore` already ignores `.env`; `.env.example` should be allowed explicitly if `.env.*` is ignored.
