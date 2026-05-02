# NeuralShield Digital

Production-oriented FastAPI, Jinja2, Tailwind CSS, PostgreSQL, SQLAlchemy, Alembic, Docker, Nginx, and AWS scaffold for the NeuralShield Digital company website and admin platform.

## Stack

- FastAPI
- Jinja2
- Tailwind CSS
- PostgreSQL
- SQLAlchemy
- Alembic
- Docker
- Nginx
- AWS deployment

## Prerequisites

- Python 3.12+
- PostgreSQL 16+
- Node.js 18+
- npm 9+
- Git

## Environment Setup

1. Create the environment file:

```bash
cp .env.example .env
```

2. Update `.env` values for your machine, especially:

- `DATABASE_URL`
- `POSTGRES_*`
- `SECRET_KEY`
- `CSRF_SECRET_KEY`
- `SMTP_*`

## Local Setup Without Docker

1. Create a virtual environment:

```bash
python -m venv .venv
```

2. Activate the virtual environment:

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source .venv/bin/activate
```

3. Install Python dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. Install frontend dependencies:

```bash
npm install
```

5. Build Tailwind CSS:

```bash
npm run build:css
```

6. Create the PostgreSQL database:

```sql
CREATE DATABASE neuralshielddigital;
```

7. Run migrations:

```bash
alembic upgrade head
```

8. Create the initial admin user:

```bash
python scripts/create_admin.py
```

9. Start the FastAPI development server:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

10. Open the application:

- Public site: `http://127.0.0.1:8000`
- Admin login: `http://127.0.0.1:8000/admin/login`

## Local Setup With Docker

1. Create the environment file:

```bash
cp .env.example .env
```

2. Build and start the stack:

```bash
docker compose up --build
```

3. Run database migrations in the app container:

```bash
docker compose exec app alembic upgrade head
```

4. Create the initial admin user:

```bash
docker compose exec app python scripts/create_admin.py
```

5. Open the application:

- Public site: `http://127.0.0.1`
- Admin login: `http://127.0.0.1/admin/login`

## Production Notes

- Set `DEBUG=false`
- Use a strong `SECRET_KEY`
- Use a strong `CSRF_SECRET_KEY`
- Set `SECURE_COOKIES=true` behind HTTPS
- Point `DATABASE_URL` to production PostgreSQL/RDS
- Replace SMTP sandbox credentials with production credentials
- Run FastAPI behind Nginx
- Apply Alembic migrations during deployment
- Production startup command: `/app/scripts/start.sh`
- Static files are served by Nginx from a shared volume at `/var/www/static`
- Media files are served by Nginx from `/var/www/media`
- For AWS production, prefer RDS for PostgreSQL and use EC2 only for app + Nginx containers
- See [infra/aws/production-environment.md](/F:/neuralshielddigital/infra/aws/production-environment.md) for the recommended EC2 + RDS setup

## Common Commands

```bash
npm run build:css
alembic upgrade head
python scripts/create_admin.py
pytest
```

## Project Startup Files

- `requirements.txt`: pinned Python dependencies for app startup
- `.env.example`: environment template for app, database, security, and SMTP
- `app/core/config.py`: typed settings loader
- `app/core/database.py`: SQLAlchemy engine and session setup
- `app/main.py`: FastAPI entrypoint and router registration
- `alembic.ini` and `migrations/env.py`: database migration startup configuration
