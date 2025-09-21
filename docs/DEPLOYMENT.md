# Deployment and Setup Documentation

This document provides comprehensive guidance for deploying and setting up the Recipe Recommender application in various environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Local Development Setup](#local-development-setup)
- [Docker Deployment](#docker-deployment)
- [Railway Deployment](#railway-deployment)
- [Production Configuration](#production-configuration)
- [Environment Variables](#environment-variables)
- [Database Setup](#database-setup)
- [Email Configuration](#email-configuration)
- [SSL/TLS Configuration](#ssltls-configuration)
- [Monitoring and Logging](#monitoring-and-logging)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **Python**: 3.11 or higher
- **Node.js**: 18 or higher
- **Memory**: Minimum 512MB RAM, recommended 1GB+
- **Storage**: 2GB free space (including ML model)
- **Network**: HTTPS access for email service integration

### Required Tools

```bash
# Python package manager (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or use pip if uv is not available
pip install --upgrade pip

# Node.js and npm (via nvm recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18
```

### ML Model Requirements

The application requires a trained machine learning model:

```bash
# Ensure model file exists at:
food-recipe-recommender/models/recipe_recommender_model.joblib

# Or set custom path via environment variable:
export MODEL_PATH=/path/to/your/model.joblib
```

## Local Development Setup

### Quick Start

1. **Clone and Install Dependencies**
   ```bash
   git clone <repository-url>
   cd recipe_recommender

   # Install Python dependencies
   uv sync

   # Install frontend dependencies
   cd food-recipe-recommender/app/frontend
   npm install
   cd ../../..
   ```

2. **Environment Configuration**
   ```bash
   # Copy environment template
   cp food-recipe-recommender/app/.env.example food-recipe-recommender/app/.env

   # Edit configuration
   nano food-recipe-recommender/app/.env
   ```

3. **Start Development Servers**

   **Backend** (Terminal 1):
   ```bash
   cd food-recipe-recommender/app
   uv run flask --app app:create_app run --debug --port 8080
   ```

   **Frontend** (Terminal 2):
   ```bash
   cd food-recipe-recommender/app/frontend
   npm run dev
   ```

4. **Access Application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8080/api
   - API Documentation: See [docs/API.md](API.md)

### Development Environment Variables

Create `food-recipe-recommender/app/.env`:

```env
# Development Configuration
SECRET_KEY=dev-secret-key-change-in-production
ENV=development

# Database (SQLite for development)
# DATABASE_URL=  # Leave empty for SQLite

# Email (optional for development)
RESEND_API_KEY=your-resend-api-key
EMAIL_FROM=dev@yourdomain.com
FRONTEND_BASE_URL=http://localhost:5173

# Admin
ADMIN_TOKEN=dev-admin-token

# Rate Limiting
RATE_LIMIT_PER_IP_PER_HOUR=10
RATE_LIMIT_PER_EMAIL_PER_HOUR=5
```

### Running Tests

```bash
# Backend tests
make test

# Backend tests with coverage
make test-cov

# Frontend tests
make test-frontend

# Frontend tests with coverage
make test-frontend-cov

# Integration tests (requires running backend)
make test-live

# Custom API endpoint for integration tests
make test-live API=http://localhost:8080/api
```

## Docker Deployment

### Building the Image

The application uses a multi-stage Docker build process:

```bash
# Build with default settings
make docker-build

# Build with custom image name/tag
make docker-build IMAGE=myregistry/recipe-app TAG=v1.0.0

# Manual build
docker build -t recipe-recommender:latest .
```

### Build Process Details

The Dockerfile implements a two-stage build:

1. **Frontend Build Stage** (`node:20-alpine`)
   - Installs npm dependencies
   - Builds React application with Vite
   - Outputs optimized static files

2. **Runtime Stage** (`python:3.11-slim`)
   - Installs Python dependencies with uv
   - Copies built frontend into Flask templates/static
   - Configures Waitress WSGI server

### Running the Container

```bash
# Run with environment file
make docker-run

# Run with manual environment variables
docker run -p 8080:8080 \
  -e SECRET_KEY=your-secret-key \
  -e DATABASE_URL=postgresql://... \
  -e RESEND_API_KEY=your-api-key \
  recipe-recommender:latest

# Run with volume mounts
docker run -p 8080:8080 \
  -v /host/data:/data \
  -e SQLITE_DIR=/data \
  -e MODEL_PATH=/models/model.joblib \
  -v /host/model.joblib:/models/model.joblib:ro \
  recipe-recommender:latest
```

### Docker Environment Variables

```env
# Core Configuration
SECRET_KEY=production-secret-key
DATABASE_URL=postgresql://user:pass@host:port/db
ENV=production
PORT=8080

# Email Service
RESEND_API_KEY=re_your_api_key
EMAIL_FROM=noreply@yourdomain.com
FRONTEND_BASE_URL=https://yourdomain.com

# Admin Access
ADMIN_TOKEN=secure-admin-token

# ML Model
MODEL_PATH=/app/food-recipe-recommender/models/recipe_recommender_model.joblib

# Database Persistence (if using SQLite)
SQLITE_DIR=/data

# Rate Limiting
RATE_LIMIT_PER_IP_PER_HOUR=5
RATE_LIMIT_PER_EMAIL_PER_HOUR=3
```

### Docker Compose Example

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8080:8080"
    environment:
      - SECRET_KEY=your-secret-key
      - DATABASE_URL=postgresql://postgres:password@db:5432/recipes
      - RESEND_API_KEY=your-api-key
      - EMAIL_FROM=noreply@yourdomain.com
      - FRONTEND_BASE_URL=https://yourdomain.com
      - ADMIN_TOKEN=your-admin-token
    depends_on:
      - db
    volumes:
      - ./models:/app/food-recipe-recommender/models:ro

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=recipes
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

## Railway Deployment

Railway provides a simple deployment platform with automatic builds and managed databases.

### Preparation

1. **Ensure Model File Exists**
   ```bash
   # Model must be in repository at build time
   ls food-recipe-recommender/models/recipe_recommender_model.joblib
   ```

2. **Prepare Environment Variables**
   - List all required variables for Railway configuration
   - Consider using Railway's secret management

### Deployment Steps

1. **Connect Repository**
   - Connect your GitHub repository to Railway
   - Railway will automatically detect the Dockerfile

2. **Add PostgreSQL Database** (Recommended)
   ```bash
   # In Railway dashboard:
   # 1. Add PostgreSQL service
   # 2. Copy DATABASE_URL from service variables
   # 3. Add to application environment variables
   ```

3. **Configure Environment Variables**
   ```env
   # Railway Environment Variables
   SECRET_KEY=<generate-secure-key>
   DATABASE_URL=${{Postgres.DATABASE_URL}}  # From Railway PostgreSQL service
   RESEND_API_KEY=<your-resend-api-key>
   EMAIL_FROM=noreply@yourdomain.com
   FRONTEND_BASE_URL=https://<your-app>.railway.app
   ADMIN_TOKEN=<secure-admin-token>
   ENV=production
   RATE_LIMIT_PER_IP_PER_HOUR=5
   RATE_LIMIT_PER_EMAIL_PER_HOUR=3
   ```

4. **Deploy**
   - Railway automatically builds and deploys on git push
   - Monitor build logs for any issues
   - Access application at provided Railway URL

### Railway-Specific Configuration

#### Database Persistence Options

**Option 1: PostgreSQL Service (Recommended)**
```env
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

**Option 2: Volume with SQLite**
```env
SQLITE_DIR=/data
# Mount Railway volume at /data
```

#### Custom Domain Setup

1. **Add Custom Domain in Railway**
   - Go to Settings → Domains
   - Add your domain (e.g., recipes.yourdomain.com)

2. **Update DNS Records**
   ```
   # CNAME record
   recipes.yourdomain.com → <railway-app-url>.railway.app
   ```

3. **Update Environment**
   ```env
   FRONTEND_BASE_URL=https://recipes.yourdomain.com
   ```

#### Automatic SSL

Railway provides automatic SSL certificates for both Railway domains and custom domains.

## Production Configuration

### Security Checklist

- [ ] Strong `SECRET_KEY` (use `python -c "import secrets; print(secrets.token_hex(32))"`)
- [ ] Secure `ADMIN_TOKEN` for admin endpoints
- [ ] PostgreSQL database with secure credentials
- [ ] HTTPS enforced for all traffic
- [ ] Rate limiting configured appropriately
- [ ] Environment variables secured (not in source code)
- [ ] Regular security updates for dependencies

### Performance Optimization

#### Application Settings

```env
# Production optimizations
ENV=production
PYTHONDONTWRITEBYTECODE=1
PYTHONUNBUFFERED=1

# Waitress configuration (via code in app.py)
# - Multiple threads for concurrent requests
# - Appropriate timeout settings
# - Memory optimization
```

#### Database Optimization

```sql
-- PostgreSQL performance indexes
CREATE INDEX CONCURRENTLY idx_user_email ON "user" (email_address);
CREATE INDEX CONCURRENTLY idx_saved_recipe_user_id ON saved_recipe (user_id);
CREATE INDEX CONCURRENTLY idx_saved_recipe_recipe_id ON saved_recipe (recipe_id);
CREATE INDEX CONCURRENTLY idx_password_reset_log_ip_created ON password_reset_request_log (ip, created_at);
```

#### Caching Strategy

- **Frontend**: Built assets cached with versioning
- **API**: Saved recipes cached client-side (5 minutes)
- **Static files**: Served with appropriate cache headers

### Monitoring and Health Checks

#### Health Check Endpoint

```bash
# Application health check
curl https://yourdomain.com/api/health

# Expected response:
{"status": "healthy"}
```

#### Database Health

```bash
# Admin endpoint to check database connectivity
curl -H "X-Admin-Token: your-token" \
  https://yourdomain.com/api/admin/status/email
```

### Backup Strategy

#### Database Backups

```bash
# PostgreSQL automated backups
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# Railway databases include automatic backups
# Check Railway dashboard for backup settings
```

#### Application Data

```bash
# Export saved recipes for user data backup
# Use admin endpoints to export user data if needed
```

## Environment Variables Reference

### Core Application

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | ✅ | - | Flask session secret (use secure random key) |
| `ENV` | ❌ | `development` | Environment mode (`development`/`production`) |
| `PORT` | ❌ | `8080` | Application port (Railway sets automatically) |

### Database

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | ❌ | SQLite | Full database connection URL |
| `SQLITE_DIR` | ❌ | `instance/` | Directory for SQLite file (if not using PostgreSQL) |

### Email Service

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `RESEND_API_KEY` | ❌ | - | Resend API key for email sending |
| `EMAIL_FROM` | ❌ | - | Verified sender email address |
| `FRONTEND_BASE_URL` | ❌ | - | Base URL for password reset links |

### ML Model

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MODEL_PATH` | ❌ | `../models/recipe_recommender_model.joblib` | Path to ML model file |

### Security & Admin

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ADMIN_TOKEN` | ❌ | - | Token for admin endpoint access |
| `RATE_LIMIT_PER_IP_PER_HOUR` | ❌ | `5` | Password reset rate limit per IP |
| `RATE_LIMIT_PER_EMAIL_PER_HOUR` | ❌ | `3` | Password reset rate limit per email |

## Database Setup

### PostgreSQL Setup

#### Local PostgreSQL

```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE recipe_recommender;
CREATE USER recipe_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE recipe_recommender TO recipe_user;
\q

# Set DATABASE_URL
export DATABASE_URL="postgresql://recipe_user:secure_password@localhost/recipe_recommender"
```

#### Managed PostgreSQL (Railway)

```bash
# Railway automatically provides DATABASE_URL
# Use Railway environment variable: ${{Postgres.DATABASE_URL}}
```

#### Database Initialization

```python
# Tables created automatically on first run
# No manual migration required for initial setup

# For schema updates, see docs/DATABASE.md
```

### SQLite Setup (Development)

```bash
# SQLite database created automatically
# Default location: instance/database.db

# Custom SQLite location
export SQLITE_DIR=/path/to/data
# Creates: /path/to/data/database.db
```

## Email Configuration

### Resend Setup

1. **Create Resend Account**
   - Sign up at https://resend.com
   - Verify your sending domain

2. **Domain Verification**
   ```bash
   # Add DNS records for domain verification
   # Follow Resend documentation for specific records
   ```

3. **API Key Generation**
   ```bash
   # Generate API key in Resend dashboard
   # Copy key for RESEND_API_KEY environment variable
   ```

4. **Configuration**
   ```env
   RESEND_API_KEY=re_your_api_key_here
   EMAIL_FROM=noreply@yourdomain.com  # Must be verified
   FRONTEND_BASE_URL=https://yourdomain.com
   ```

### Email Testing

```bash
# Test email configuration via admin endpoint
curl -X POST \
  -H "Content-Type: application/json" \
  -H "X-Admin-Token: your-admin-token" \
  -d '{"to":"test@example.com"}' \
  https://yourdomain.com/api/admin/test-email
```

### Development Email

```env
# Development mode shows reset tokens in response
ENV=development

# Password reset response includes devResetToken for testing
```

## SSL/TLS Configuration

### Railway SSL

Railway automatically provides SSL certificates:
- Automatic certificate generation
- Automatic renewal
- Support for custom domains

### Manual SSL Setup

If deploying elsewhere, ensure HTTPS:

```nginx
# Nginx SSL configuration example
server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Monitoring and Logging

### Application Logs

```bash
# Docker container logs
docker logs <container-id>

# Railway logs
# Available in Railway dashboard

# Local development logs
# Logged to console with Flask debug mode
```

### Health Monitoring

```bash
# Set up health check monitoring
curl -f https://yourdomain.com/api/health || exit 1

# Monitor admin endpoints
curl -H "X-Admin-Token: token" \
  https://yourdomain.com/api/admin/status/email
```

### Performance Monitoring

```bash
# Monitor response times
curl -w "@curl-format.txt" -o /dev/null -s "https://yourdomain.com/api/health"

# Database performance
# Use PostgreSQL EXPLAIN ANALYZE for query optimization
```

## Troubleshooting

### Common Issues

#### Build Failures

```bash
# Frontend build fails
cd food-recipe-recommender/app/frontend
npm ci
npm run build

# Python dependency issues
uv sync --reinstall

# Docker build fails
docker system prune
docker build --no-cache -t recipe-recommender .
```

#### Runtime Issues

```bash
# Application won't start
# Check environment variables
printenv | grep -E "(SECRET_KEY|DATABASE_URL|PORT)"

# Database connection issues
# Verify DATABASE_URL format
# Check network connectivity

# Email sending fails
# Verify RESEND_API_KEY and EMAIL_FROM
# Check domain verification status
```

#### Performance Issues

```bash
# Slow API responses
# Check database indexes
# Monitor PostgreSQL slow query log

# High memory usage
# Check ML model loading
# Monitor container memory limits
```

### Debugging Steps

1. **Check Application Logs**
   ```bash
   # Railway: Dashboard → Deployments → Logs
   # Docker: docker logs <container>
   # Local: Console output
   ```

2. **Verify Environment Variables**
   ```bash
   # Check critical variables are set
   echo $SECRET_KEY
   echo $DATABASE_URL
   ```

3. **Test Database Connection**
   ```bash
   # PostgreSQL connection test
   psql $DATABASE_URL -c "SELECT 1;"
   ```

4. **Test Email Configuration**
   ```bash
   curl -X POST \
     -H "X-Admin-Token: $ADMIN_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"to":"test@yourdomain.com"}' \
     $FRONTEND_BASE_URL/api/admin/test-email
   ```

5. **Check ML Model Loading**
   ```bash
   # Verify model file exists and is readable
   ls -la food-recipe-recommender/models/recipe_recommender_model.joblib
   ```

### Getting Help

- **Documentation**: Check [docs/](../) directory for detailed guides
- **API Reference**: See [docs/API.md](API.md)
- **Database Schema**: See [docs/DATABASE.md](DATABASE.md)
- **Frontend Guide**: See [docs/FRONTEND.md](FRONTEND.md)

---

For operational procedures, see [docs/OPERATIONS.md](OPERATIONS.md).

For development guidelines, see [docs/CONTRIBUTING.md](CONTRIBUTING.md).