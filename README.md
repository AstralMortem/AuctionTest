# Setup

## Env

Create .env file, use .env-example for reference, main variables is

```
# Database URL
DATABASE_URL=postgresql+asyncpg://appuser:apppassword@postgres:5432/appdb

# Postgres configuration
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=appuser
POSTGRES_PASSWORD=apppassword
POSTGRES_DB=appdb
```


## Start App

```sh
docker compose up
```