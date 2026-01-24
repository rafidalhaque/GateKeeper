# Deployment Guide

This guide covers deploying GateKeeper to production.

## Prerequisites

- Linux server (Ubuntu 20.04+ recommended)
- Domain name
- SSL certificate (Let's Encrypt recommended)
- Minimum 2GB RAM, 2 CPU cores
- Docker and Docker Compose

## Quick Deployment

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create deployment user
sudo useradd -m -s /bin/bash gatekeeper
sudo usermod -aG docker gatekeeper
```

### 2. Clone and Configure

```bash
# Switch to deployment user
sudo su - gatekeeper

# Clone repository
git clone https://github.com/rafidalhaque/GateKeeper.git
cd GateKeeper

# Copy and edit environment file
cp .env.example .env
nano .env  # Edit with your production values
```

### 3. Configure Environment

Edit `.env` with production values:

```env
# IMPORTANT: Set these for production
SECRET_KEY=<generate-random-64-char-key>
FLASK_ENV=production
DEBUG=False

# Database (use external PostgreSQL in production)
DATABASE_URL=postgresql://user:password@db-host:5432/gatekeeper

# Redis
REDIS_URL=redis://redis:6379/0

# Supabase (set up your project first)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_JWT_SECRET=your-jwt-secret

# SMTP (use production mail service)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@domain.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@yourdomain.com

# Application
APP_URL=https://yourdomain.com

# Security
SESSION_COOKIE_SECURE=True
```

### 4. Generate SECRET_KEY

```bash
# Generate secure secret key
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 5. Deploy

```bash
# Start services
docker-compose up -d

# Run migrations
docker-compose exec web flask db upgrade

# Seed permissions and roles
docker-compose exec web flask seed-permissions
docker-compose exec web flask seed-roles

# Create super admin
docker-compose exec web flask create-super-admin
```

## Nginx Setup

### Install Nginx

```bash
sudo apt install nginx -y
```

### Configure Site

```bash
sudo nano /etc/nginx/sites-available/gatekeeper
```

Use the example configuration from `examples/nginx.conf` and adjust:

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # ... rest of configuration
}
```

### Enable Site

```bash
sudo ln -s /etc/nginx/sites-available/gatekeeper /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal is configured automatically
```

## Firewall Configuration

```bash
# Allow SSH, HTTP, HTTPS
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## Database Backup

### Automated Backup Script

```bash
# Create backup script
nano ~/backup-gatekeeper.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/home/gatekeeper/backups"
mkdir -p $BACKUP_DIR

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/gatekeeper_$TIMESTAMP.sql"

# Backup database
docker-compose exec -T postgres pg_dump -U gatekeeper gatekeeper > $BACKUP_FILE

# Compress backup
gzip $BACKUP_FILE

# Remove backups older than 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_FILE.gz"
```

```bash
chmod +x ~/backup-gatekeeper.sh
```

### Schedule with Cron

```bash
crontab -e
```

Add daily backup at 2 AM:

```cron
0 2 * * * /home/gatekeeper/backup-gatekeeper.sh >> /home/gatekeeper/backup.log 2>&1
```

## Monitoring

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f celery-worker

# Last 100 lines
docker-compose logs --tail=100 web
```

### Service Status

```bash
docker-compose ps
```

### Resource Usage

```bash
docker stats
```

## Updates

### Update Application

```bash
cd /home/gatekeeper/GateKeeper

# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up -d --build

# Run migrations
docker-compose exec web flask db upgrade
```

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose logs web

# Check database connection
docker-compose exec web flask shell
>>> from app.models import db
>>> db.engine.execute('SELECT 1')
```

### Database Migration Issues

```bash
# Check current migration
docker-compose exec web flask db current

# Stamp current version (if needed)
docker-compose exec web flask db stamp head
```

### Email Not Sending

```bash
# Test SMTP connection
docker-compose exec web python3 << EOF
from flask_mail import Mail, Message
from app.app import create_app

app = create_app()
with app.app_context():
    mail = Mail(app)
    msg = Message('Test', recipients=['test@example.com'])
    msg.body = 'Test email'
    mail.send(msg)
    print('Email sent successfully')
EOF
```

### High Memory Usage

```bash
# Restart services
docker-compose restart

# Check memory limits in docker-compose.yml
# Add memory limits if needed:
services:
  web:
    mem_limit: 512m
```

## Performance Tuning

### Gunicorn Workers

Edit `docker-compose.yml`:

```yaml
web:
  command: gunicorn --bind 0.0.0.0:5000 --workers 4 --threads 2 --timeout 120 run:app
```

Workers formula: `(2 × CPU cores) + 1`

### PostgreSQL Optimization

```sql
-- Increase shared_buffers (25% of RAM)
ALTER SYSTEM SET shared_buffers = '512MB';

-- Increase work_mem
ALTER SYSTEM SET work_mem = '16MB';

-- Reload configuration
SELECT pg_reload_conf();
```

### Redis Optimization

Edit `docker-compose.yml`:

```yaml
redis:
  command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
```

## Security Checklist

- [ ] Change default passwords
- [ ] Set strong SECRET_KEY
- [ ] Enable HTTPS only
- [ ] Configure firewall
- [ ] Set up fail2ban
- [ ] Regular security updates
- [ ] Database backups configured
- [ ] Monitor logs regularly
- [ ] Use strong SMTP password
- [ ] Configure Supabase RLS policies

## Scaling

### Horizontal Scaling

1. Use external PostgreSQL (managed service)
2. Use external Redis (managed service)
3. Deploy multiple app instances behind load balancer
4. Use CDN for static assets

### Vertical Scaling

1. Increase server resources
2. Adjust Gunicorn workers
3. Optimize database queries
4. Add database indexes

## Support

For issues:
1. Check logs first
2. Review troubleshooting section
3. Search GitHub issues
4. Create new issue with logs and details
