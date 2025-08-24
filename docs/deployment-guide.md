# Deployment Guide - Urdu Marsiya NER Web Application

## Overview

This guide covers the deployment of the Marsiya NER application in various environments, from development to production.

## Prerequisites

### System Requirements

- **OS**: Ubuntu 20.04+ / CentOS 8+ / macOS 12+
- **Python**: 3.9+
- **Node.js**: 18+
- **Database**: PostgreSQL 13+ or SQLite (development)
- **Redis**: 6.0+ (for Celery and caching)
- **Memory**: 4GB+ RAM
- **Storage**: 20GB+ available space

### Software Dependencies

- Git
- Docker & Docker Compose (optional)
- Nginx (production)
- Supervisor or systemd
- Virtual environment tools (venv, conda)

## Development Setup

### 1. Clone Repository

```bash
git clone https://github.com/your-org/marsiya-llm-ner.git
cd marsiya-llm-ner
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Environment variables
cp .env.example .env
# Edit .env with your configuration

# Database setup
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic

# Run development server
python manage.py runserver
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Environment variables
cp .env.example .env.local
# Edit .env.local with your configuration

# Run development server
npm run dev
```

### 4. Redis Setup

```bash
# Install Redis
sudo apt-get install redis-server  # Ubuntu
brew install redis  # macOS

# Start Redis
sudo systemctl start redis-server
# or
redis-server
```

## Production Deployment

### Option 1: Docker Deployment

#### Docker Compose Setup

```yaml
# docker-compose.yml
version: "3.8"

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: marsiya_ner
      POSTGRES_USER: marsiya_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  backend:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://marsiya_user:secure_password@db:5432/marsiya_ner
      - REDIS_URL=redis://redis:6379
      - SECRET_KEY=your_secret_key
      - DEBUG=False
    volumes:
      - ./backend:/app
      - media_files:/app/media
    depends_on:
      - db
      - redis
    ports:
      - "8000:8000"

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend

volumes:
  postgres_data:
  redis_data:
  media_files:
```

#### Build and Deploy

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
```

### Option 2: Traditional Server Deployment

#### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv nginx postgresql redis-server

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

#### 2. Database Setup

```bash
# PostgreSQL setup
sudo -u postgres psql
CREATE DATABASE marsiya_ner;
CREATE USER marsiya_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE marsiya_ner TO marsiya_user;
\q

# Test connection
psql -h localhost -U marsiya_user -d marsiya_ner
```

#### 3. Application Deployment

```bash
# Create application directory
sudo mkdir -p /opt/marsiya-ner
sudo chown $USER:$USER /opt/marsiya-ner

# Clone repository
cd /opt/marsiya-ner
git clone https://github.com/your-org/marsiya-llm-ner.git .

# Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Environment configuration
cp .env.example .env
# Edit .env with production settings

# Database migration
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

#### 4. Gunicorn Configuration

```python
# backend/gunicorn.conf.py
bind = "127.0.0.1:8000"
workers = 3
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
```

#### 5. Supervisor Configuration

```ini
# /etc/supervisor/conf.d/marsiya-ner.conf
[program:marsiya-ner-backend]
command=/opt/marsiya-ner/backend/venv/bin/gunicorn marsiya_ner.wsgi:application -c gunicorn.conf.py
directory=/opt/marsiya-ner/backend
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/marsiya-ner/backend.log

[program:marsiya-ner-celery]
command=/opt/marsiya-ner/backend/venv/bin/celery -A marsiya_ner worker --loglevel=info
directory=/opt/marsiya-ner/backend
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/marsiya-ner/celery.log
```

#### 6. Nginx Configuration

```nginx
# /etc/nginx/sites-available/marsiya-ner
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    # Frontend
    location / {
        root /opt/marsiya-ner/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket support
    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    # Media files
    location /media/ {
        alias /opt/marsiya-ner/backend/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Static files
    location /static/ {
        alias /opt/marsiya-ner/backend/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

#### 7. SSL Certificate Setup

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Generate certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Environment Configuration

### Backend Environment Variables

```bash
# .env
DEBUG=False
SECRET_KEY=your_very_secure_secret_key
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database
DATABASE_URL=postgresql://marsiya_user:secure_password@localhost:5432/marsiya_ner

# Redis
REDIS_URL=redis://localhost:6379

# LLM API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password

# Security
CORS_ALLOWED_ORIGINS=https://your-domain.com
CSRF_TRUSTED_ORIGINS=https://your-domain.com
```

### Frontend Environment Variables

```bash
# .env.local
VITE_API_BASE_URL=https://your-domain.com/api
VITE_WS_BASE_URL=wss://your-domain.com/ws
VITE_APP_NAME=Marsiya NER
VITE_APP_VERSION=1.0.0
```

## Monitoring and Maintenance

### Log Management

```bash
# Create log directory
sudo mkdir -p /var/log/marsiya-ner
sudo chown www-data:www-data /var/log/marsiya-ner

# Log rotation
sudo nano /etc/logrotate.d/marsiya-ner
```

### Health Checks

```bash
# Backend health check
curl -f http://localhost:8000/api/health/ || exit 1

# Database health check
pg_isready -h localhost -U marsiya_user -d marsiya_ner || exit 1

# Redis health check
redis-cli ping || exit 1
```

### Backup Strategy

```bash
# Database backup script
#!/bin/bash
BACKUP_DIR="/opt/backups/marsiya-ner"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup
pg_dump -h localhost -U marsiya_user marsiya_ner > $BACKUP_DIR/db_$DATE.sql

# Media files backup
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /opt/marsiya-ner/backend/media/

# Clean old backups (keep 30 days)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

## Scaling Considerations

### Horizontal Scaling

- Use load balancer (HAProxy, Nginx)
- Multiple application instances
- Database read replicas
- Redis clustering

### Performance Optimization

- Enable database connection pooling
- Implement caching strategies
- Use CDN for static files
- Optimize database queries

## Troubleshooting

### Common Issues

1. **Database Connection**: Check PostgreSQL service and credentials
2. **Redis Connection**: Verify Redis service is running
3. **Static Files**: Ensure collectstatic was run
4. **Permissions**: Check file ownership and permissions
5. **Port Conflicts**: Verify no other services use required ports

### Debug Commands

```bash
# Check service status
sudo systemctl status postgresql redis nginx

# View logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/marsiya-ner/backend.log

# Test database connection
psql -h localhost -U marsiya_user -d marsiya_ner -c "SELECT 1;"

# Test Redis connection
redis-cli ping
```

This deployment guide provides comprehensive instructions for setting up the Marsiya NER application in various environments.
