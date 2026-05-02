# NeuralShield Digital Production Environment Notes

This deployment setup is designed to run well on AWS EC2 with PostgreSQL hosted on Amazon RDS.

## Production Startup Command

The production container starts with:

```bash
/app/scripts/start.sh
```

That script:

- syncs application static assets into the shared static volume
- optionally runs Alembic migrations when `RUN_MIGRATIONS=true`
- starts the FastAPI application with Uvicorn workers and proxy header support

Equivalent direct startup command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2 --proxy-headers --forwarded-allow-ips="*"
```

## Recommended AWS Topology

- EC2 instance for Dockerized app + Nginx
- RDS PostgreSQL for the production database
- EBS volume or attached instance storage for local media persistence if not using object storage
- ACM + ALB or CloudFront + ALB for HTTPS termination
- Security Group allowing:
  - `80/443` inbound to the reverse proxy
  - `5432` inbound only from the application security group to RDS

## Environment Variables

Set these in the production `.env` or your orchestration secret store:

- `ENVIRONMENT=production`
- `DEBUG=false`
- `DOMAIN=neuralshielddigital.com`
- `DATABASE_URL=postgresql+psycopg://<user>:<password>@<rds-endpoint>:5432/<database>`
- `SECRET_KEY=<strong-random-secret>`
- `CSRF_SECRET_KEY=<strong-random-secret>`
- `SECURE_COOKIES=true`
- `ALLOWED_HOSTS=neuralshielddigital.com,www.neuralshielddigital.com,<ec2-public-dns>`
- `CORS_ORIGINS=https://neuralshielddigital.com,https://www.neuralshielddigital.com`
- `SMTP_HOST=<provider-host>`
- `SMTP_PORT=<provider-port>`
- `SMTP_USERNAME=<smtp-username>`
- `SMTP_PASSWORD=<smtp-password>`
- `SMTP_FROM_EMAIL=contact@neuralshielddigital.com`
- `SMTP_FROM_NAME=NeuralShield Digital`
- `WEB_CONCURRENCY=2`
- `RUN_MIGRATIONS=false`

## Static and Media Strategy

Static assets:

- repository-managed static files live in `app/static`
- on container startup, `scripts/start.sh` copies them into `/var/www/static`
- Nginx serves `/static/*` directly for better performance and lower app overhead

Media files:

- the Nginx config serves `/media/*` from `/var/www/media`
- for a single EC2 instance, mount `/var/www/media` to a persistent Docker volume or EBS-backed path
- for multi-instance or higher-scale deployments, move media storage to Amazon S3 and serve through CloudFront

Recommended production strategy:

- keep app static files in the image
- keep user-uploaded media out of the image
- use S3 for media once uploads become part of the product

## Database Notes

- prefer RDS PostgreSQL over a Dockerized Postgres container in production
- keep `db` service in `docker-compose.yml` for local development only
- run `alembic upgrade head` during deployment or set `RUN_MIGRATIONS=true` only for controlled rollout jobs
- enable automated backups and Multi-AZ in RDS for resilience

## Practical EC2 Deployment Flow

1. Copy the project to the EC2 host.
2. Create a production `.env`.
3. Point `DATABASE_URL` to RDS.
4. Build and start containers:

```bash
docker compose up -d --build app nginx
```

5. Run migrations once:

```bash
docker compose run --rm -e RUN_MIGRATIONS=true app
```

6. Create the first admin if needed:

```bash
docker compose run --rm app python scripts/create_admin.py
```

7. Seed local demonstration data only when appropriate:

```bash
docker compose run --rm app python scripts/seed_data.py
```

## HTTPS and Reverse Proxy Notes

- if using an AWS Application Load Balancer, terminate TLS at the ALB and forward HTTP to Nginx on port `80`
- preserve `X-Forwarded-*` headers so FastAPI can build correct URLs and secure cookie behavior
- if terminating TLS directly on Nginx instead, add certificate configuration and change the proxy-facing security settings accordingly
