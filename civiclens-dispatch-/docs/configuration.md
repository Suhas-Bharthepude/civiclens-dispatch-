# CivicLens Dispatch - Configuration Guide

## Environment Variables

All configuration is managed through environment variables stored in `.env` file.

### Setup Instructions

1. Copy the example file:
```bash
   cp backend/.env.example backend/.env
```

2. Edit `.env` with your actual values:
```bash
   nano backend/.env
```

3. Never commit `.env` to git!

## Configuration Settings

### Environment

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ENVIRONMENT` | Current environment | `development` | No |
| `DEBUG` | Enable debug mode | `True` | No |

**Values:**
- `development` - Local development
- `staging` - Pre-production testing
- `production` - Live production

### Database

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | Full PostgreSQL connection string | `postgresql+asyncpg://user:pass@localhost/db` | Yes |
| `POSTGRES_USER` | Database username | `civic_user` | Yes |
| `POSTGRES_PASSWORD` | Database password | `secret123` | Yes |
| `POSTGRES_DB` | Database name | `civiclens` | Yes |
| `POSTGRES_HOST` | Database host | `localhost` | No |
| `POSTGRES_PORT` | Database port | `5432` | No |

### File Storage

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `UPLOAD_DIR` | Directory for uploaded files | `backend/app/media/tmp` | No |
| `MAX_UPLOAD_SIZE` | Max file size in bytes | `10485760` (10MB) | No |

### API Keys (Future)

| Variable | Description | When Needed |
|----------|-------------|-------------|
| `MAPBOX_API_KEY` | Mapbox API key for maps | Day 36 |
| `HUGGINGFACE_API_KEY` | HuggingFace API for AI models | Day 51+ |

### Security (Future)

| Variable | Description | When Needed |
|----------|-------------|-------------|
| `SECRET_KEY` | JWT token signing key | Day 56 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | Day 56 |

## Testing Configuration

Run the configuration test:
```bash
cd backend
python -m playground.test_config
```

## Best Practices

✅ **DO:**
- Use `.env` for local development
- Use system environment variables in production
- Keep `.env.example` updated as you add settings
- Document all environment variables

❌ **DON'T:**
- Commit `.env` to git
- Hardcode secrets in code
- Share your `.env` file with others
- Use the same passwords in development and production

## Production Deployment

In production, set environment variables through:
- Server environment variables
- Docker environment files
- Cloud provider secret management (AWS Secrets Manager, etc.)

**Never** deploy the `.env` file to production!

---

*Last updated: Day 19*



