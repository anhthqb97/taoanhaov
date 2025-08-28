# 🐳 Liên Quân Automation API - Docker Deployment

## 📋 Overview

This document describes how to deploy the Liên Quân Automation API using Docker and Docker Compose.

## 🚀 Quick Start

### Prerequisites

- Docker Desktop installed and running
- Docker Compose available
- At least 4GB RAM available
- Ports 8000, 3306, 6379, 8080, 80, 443 available

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd lienquan

# Make scripts executable
chmod +x scripts/*.sh
```

### 2. Environment Configuration

Copy the environment example and customize:

```bash
# Copy environment file
cp .env.example .env

# Edit with your settings
nano .env
```

**Important settings to customize:**
- `JWT_SECRET_KEY`: Generate a strong secret key
- `SECRET_KEY`: Generate another strong secret key
- `SMTP_USER` and `SMTP_PASSWORD`: Your email credentials
- `ANDROID_HOME`: Path to your Android SDK

### 3. Start the System

```bash
# Start all services
./scripts/start.sh
```

This script will:
- Create necessary directories
- Build Docker images
- Start all services
- Wait for services to be healthy
- Display service URLs and credentials

### 4. Access Services

- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/health
- **Database Admin**: http://localhost:8080
- **Main Application**: http://localhost:8000

### 5. Default Credentials

- **Username**: `admin`
- **Password**: `admin123456`

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx (80/443)│    │  FastAPI (8000) │    │   Adminer (8080)│
│   Reverse Proxy │    │   Application   │    │  Database Admin │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   MySQL (3306)  │
                    │   Database      │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Redis (6379)  │
                    │     Cache       │
                    └─────────────────┘
```

## 🔧 Services

### 1. FastAPI Application (`app`)
- **Port**: 8000
- **Image**: Built from local Dockerfile
- **Features**: Main API, authentication, automation workflows
- **Dependencies**: MySQL, Redis

### 2. MySQL Database (`mysql`)
- **Port**: 3306
- **Image**: mysql:8.0
- **Database**: `lienquan_db`
- **User**: `lienquan_user`
- **Password**: `lienquan_pass123`

### 3. Redis Cache (`redis`)
- **Port**: 6379
- **Image**: redis:7-alpine
- **Purpose**: Session storage, caching, rate limiting

### 4. Nginx (`nginx`)
- **Ports**: 80, 443
- **Image**: nginx:alpine
- **Purpose**: Reverse proxy, SSL termination, static file serving

### 5. Adminer (`adminer`)
- **Port**: 8080
- **Image**: adminer:latest
- **Purpose**: Database management interface

## 📁 Directory Structure

```
lienquan/
├── src/                    # Application source code
├── scripts/               # Startup/stop scripts
├── screenshots/           # Game screenshots (mounted)
├── uploads/              # File uploads (mounted)
├── logs/                 # Application logs (mounted)
├── mysql/                # MySQL data and init scripts
├── nginx/                # Nginx configuration
├── Dockerfile            # Application container
├── docker-compose.yml    # Service orchestration
└── requirements.txt      # Python dependencies
```

## 🛠️ Management Commands

### Start Services
```bash
./scripts/start.sh
# or
docker-compose up -d
```

### Stop Services
```bash
./scripts/stop.sh
# or
docker-compose down
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f app
docker-compose logs -f mysql
docker-compose logs -f redis
```

### Restart Services
```bash
docker-compose restart
# or specific service
docker-compose restart app
```

### Rebuild and Start
```bash
docker-compose up -d --build
```

### Access Container Shell
```bash
# FastAPI app
docker-compose exec app bash

# MySQL
docker-compose exec mysql mysql -u root -p

# Redis
docker-compose exec redis redis-cli
```

## 🔒 Security Considerations

### 1. Environment Variables
- Never commit `.env` files to version control
- Use strong, unique secrets for production
- Rotate secrets regularly

### 2. Network Security
- Services communicate over internal Docker network
- Only necessary ports exposed to host
- Consider using Docker secrets for sensitive data

### 3. Database Security
- Change default passwords
- Limit database access to application only
- Regular backups

## 📊 Monitoring and Health Checks

### Health Check Endpoints
- **App Health**: `GET /health`
- **Database Health**: MySQL ping
- **Cache Health**: Redis ping

### Logging
- Application logs: `./logs/`
- Container logs: `docker-compose logs`
- Database logs: `docker-compose logs mysql`

### Metrics
- Enable metrics in `.env`: `ENABLE_METRICS=true`
- Access via `/metrics` endpoint (if implemented)

## 🚨 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using the port
lsof -i :8000

# Kill the process or change port in docker-compose.yml
```

#### 2. Database Connection Failed
```bash
# Check MySQL container
docker-compose logs mysql

# Check network connectivity
docker-compose exec app ping mysql
```

#### 3. Permission Denied
```bash
# Fix directory permissions
chmod 755 screenshots uploads logs
chown -R $USER:$USER screenshots uploads logs
```

#### 4. Memory Issues
```bash
# Check container resource usage
docker stats

# Increase Docker memory limit in Docker Desktop
```

### Debug Mode

Enable debug mode in `.env`:
```bash
DEBUG=true
LOG_LEVEL=DEBUG
```

### Database Reset

To completely reset the database:
```bash
# Stop services
docker-compose down

# Remove volumes
docker-compose down -v

# Start fresh
./scripts/start.sh
```

## 🔄 Updates and Maintenance

### Update Application
```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose up -d --build
```

### Update Dependencies
```bash
# Update requirements.txt
pip freeze > requirements.txt

# Rebuild container
docker-compose up -d --build app
```

### Backup Database
```bash
# Create backup
docker-compose exec mysql mysqldump -u root -p lienquan_db > backup.sql

# Restore backup
docker-compose exec -T mysql mysql -u root -p lienquan_db < backup.sql
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [MySQL Docker Image](https://hub.docker.com/_/mysql)
- [Redis Docker Image](https://hub.docker.com/_/redis)

## 🆘 Support

If you encounter issues:

1. Check the logs: `docker-compose logs -f`
2. Verify environment variables
3. Check Docker and Docker Compose versions
4. Ensure all ports are available
5. Check system resources (RAM, disk space)

---

**Happy Deploying! 🎉**
