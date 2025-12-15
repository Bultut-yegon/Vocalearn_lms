# 🐳 Docker Deployment Guide - VocaLearn AI Services

Complete guide for deploying VocaLearn AI Services using Docker.

---

## Prerequisites

- **Docker**: 20.10+ ([Install Docker](https://docs.docker.com/get-docker/))
- **Docker Compose**: 2.0+ (included with Docker Desktop)
- **System Requirements**: 
  - CPU: 2+ cores
  - RAM: 4GB minimum (8GB recommended)
  - Storage: 10GB free space
  - OS: Linux, macOS, or Windows with WSL2

---

##  Quick Start (2 Minutes)

### Step 1: Clone and Setup

```bash
cd vocalearn_ai
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### Step 2: Build and Run

```bash
# Using Make (recommended)
make build
make up

# OR using docker-compose directly
docker-compose up -d --build
```

### Step 3: Verify

```bash
# Check services are running
docker-compose ps

# Test API
curl http://localhost:8000/health

# View logs
docker-compose logs -f
```

**That's it! Your services are running at http://localhost:8000**

---

## File Structure

```
vocalearn_ai/
├── Dockerfile              # Main application image
├── docker-compose.yml      # Service orchestration
├── .dockerignore          # Files to exclude from build
├── Makefile               # Convenient commands
├── nginx/
│   └── nginx.conf         # Reverse proxy config
└── .env                   # Environment variables (create this)
```

---

## Configuration

### Environment Variables

Create `.env` file in project root:

```env
# Required
GROQ_API_KEY=your_groq_api_key_here

# Optional (with defaults)
LLM_MODEL=llama-3.1-8b-instant
ENV=production
ALLOWED_ORIGINS=*
PORT=8000
WORKERS=4
```

### Service Configuration

**docker-compose.yml** includes:
- **vocalearn-ai**: FastAPI application (port 8000)
- **redis**: Caching layer (port 6379) - optional
- **nginx**: Reverse proxy (port 80/443) - optional

---

## Build Options

### Standard Build

```bash
docker build -t vocalearn-ai:latest .
```

### Build with Custom Tag

```bash
docker build -t vocalearn-ai:v1.0.0 .
```

### Multi-Architecture Build (for ARM/AMD)

```bash
docker buildx build --platform linux/amd64,linux/arm64 \
  -t vocalearn-ai:latest .
```

### No Cache Build

```bash
docker build --no-cache -t vocalearn-ai:latest .
```

---

## Running Services

### Using Make Commands (Easiest)

```bash
make help              # Show all available commands
make build             # Build image
make up                # Start services
make down              # Stop services
make logs              # View logs
make shell             # Access container shell
make restart           # Restart services
make clean             # Remove containers and volumes
```

### Using Docker Compose

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d vocalearn-ai

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Using Docker Run (Single Container)

```bash
docker run -d \
  --name vocalearn-ai \
  -p 8000:8000 \
  -e GROQ_API_KEY=your_key \
  -e WORKERS=4 \
  vocalearn-ai:latest
```

---

## Monitoring & Logs

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f vocalearn-ai

# Last 100 lines
docker-compose logs --tail=100 vocalearn-ai

# With timestamps
docker-compose logs -f -t vocalearn-ai
```

### Container Stats

```bash
# Real-time stats
docker stats

# Specific container
docker stats vocalearn-ai-service
```

### Health Checks

```bash
# Check health endpoint
curl http://localhost:8000/health

# Check container health status
docker inspect --format='{{.State.Health.Status}}' vocalearn-ai-service

# Using Make
make health
```

---

## Development Mode

### Hot Reload Setup

Uncomment in `docker-compose.yml`:

```yaml
volumes:
  - ./app:/app/app  # Mount source code
```

Then restart:

```bash
docker-compose restart vocalearn-ai
```

### Development Commands

```bash
# Run tests
make test

# Access Python shell
docker-compose exec vocalearn-ai python

# Install new package
docker-compose exec vocalearn-ai pip install package-name
```

---

## Production Deployment

### Recommended Production Stack

```yaml
services:
  vocalearn-ai:
    image: vocalearn-ai:latest
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 2G
    environment:
      - ENV=production
      - WORKERS=4
```

### With SSL/HTTPS

1. **Generate SSL certificates** (Let's Encrypt):

```bash
certbot certonly --standalone -d your-domain.com
```

2. **Update nginx config** (uncomment HTTPS block)

3. **Mount certificates**:

```yaml
volumes:
  - /etc/letsencrypt:/etc/nginx/ssl:ro
```

### Production Checklist

- [ ] Set `ENV=production` in `.env`
- [ ] Configure proper CORS origins
- [ ] Enable SSL/HTTPS
- [ ] Set up health monitoring
- [ ] Configure log aggregation
- [ ] Set resource limits
- [ ] Enable automatic restarts
- [ ] Set up backup strategy
- [ ] Configure rate limiting

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs vocalearn-ai

# Check if port is in use
lsof -i :8000

# Restart from scratch
docker-compose down -v
docker-compose up -d --build
```

### Out of Memory

```bash
# Check memory usage
docker stats

# Increase Docker memory (Docker Desktop: Settings → Resources)

# Reduce workers in .env
WORKERS=2
```

### Permission Errors

```bash
# Fix file permissions
sudo chown -R $(whoami):$(whoami) .

# Run as root (not recommended for production)
docker-compose exec -u root vocalearn-ai bash
```

### Build Failures

```bash
# Clear build cache
docker builder prune -a

# Build with verbose output
docker-compose build --no-cache --progress=plain
```

### API Not Responding

```bash
# Check if container is running
docker-compose ps

# Test inside container
docker-compose exec vocalearn-ai curl localhost:8000/health

# Check firewall
sudo ufw status
```

### Redis Connection Issues

```bash
# Check Redis is running
docker-compose ps redis

# Test connection
docker-compose exec redis redis-cli ping

# View Redis logs
docker-compose logs redis
```

---

## Security Best Practices

### 1. Non-Root User

Already configured in Dockerfile:
```dockerfile
USER appuser
```

### 2. Read-Only Filesystem

Add to docker-compose.yml:
```yaml
security_opt:
  - no-new-privileges:true
read_only: true
tmpfs:
  - /tmp
```

### 3. Network Isolation

```yaml
networks:
  frontend:
    internal: false
  backend:
    internal: true
```

### 4. Secret Management

Use Docker secrets instead of env vars:

```bash
echo "your_api_key" | docker secret create groq_api_key -
```

### 5. Regular Updates

```bash
# Update base images
docker-compose pull
docker-compose up -d --build
```

---

## Backup & Restore

### Backup Volumes

```bash
# Using Make
make backup

# Manual backup
docker run --rm \
  -v vocalearn-redis-data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/backup-$(date +%Y%m%d).tar.gz -C /data .
```

### Restore from Backup

```bash
# Using Make
make restore

# Manual restore
docker run --rm \
  -v vocalearn-redis-data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar xzf /backup/latest-backup.tar.gz -C /data
```

---

## Deployment Platforms

### AWS EC2

```bash
# Install Docker
sudo yum update -y
sudo yum install docker -y
sudo service docker start
sudo usermod -a -G docker ec2-user

# Deploy
git clone your-repo
cd vocalearn_ai
docker-compose up -d
```

### Google Cloud Run

```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/vocalearn-ai

# Deploy
gcloud run deploy vocalearn-ai \
  --image gcr.io/PROJECT_ID/vocalearn-ai \
  --platform managed \
  --region us-central1
```

### DigitalOcean

```bash
# Use App Platform or Droplet
doctl apps create --spec app-spec.yaml
```

### Heroku

```bash
heroku container:login
heroku container:push web
heroku container:release web
```

---

## Scaling

### Horizontal Scaling

```yaml
deploy:
  replicas: 5
  update_config:
    parallelism: 2
    delay: 10s
```

### Load Balancing

Use nginx upstream with multiple containers:

```nginx
upstream vocalearn_api {
    server vocalearn-ai-1:8000;
    server vocalearn-ai-2:8000;
    server vocalearn-ai-3:8000;
}
```

### Auto-Scaling (Kubernetes)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: vocalearn-ai
spec:
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

---

## Testing

### Run Tests in Container

```bash
# Using Make
make test

# Direct command
docker-compose exec vocalearn-ai pytest tests/ -v
```

### Load Testing

```bash
# Using Apache Bench
ab -n 1000 -c 10 http://localhost:8000/health

# Using hey
hey -n 1000 -c 10 http://localhost:8000/api/recommendation/health
```

---

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [FastAPI in Docker](https://fastapi.tiangolo.com/deployment/docker/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)

---

## Pro Tips

1. **Use .dockerignore**: Keep images small
2. **Multi-stage builds**: Separate build and runtime
3. **Layer caching**: Order Dockerfile commands by change frequency
4. **Health checks**: Always define health checks
5. **Resource limits**: Prevent resource exhaustion
6. **Logging**: Use proper log drivers
7. **Monitoring**: Set up Prometheus + Grafana
8. **Backups**: Automate volume backups
9. **Updates**: Keep base images updated
10. **Documentation**: Keep this guide updated!

---

## Support

If you encounter issues:

1. Check logs: `docker-compose logs -f`
2. Review health: `make health`
3. Restart services: `make restart`
4. Clean rebuild: `make clean && make up-build`
5. Check documentation: Visit `/docs`

**Still stuck?** Open an issue on GitHub with:
- Error logs
- `docker-compose ps` output
- System information
- Steps to reproduce

---

**🐳 Happy Dockerizing!**

*For vocalearn TVET EDUCATION*