# 🌩️ MCP Memory Cloud - Deployment Guide

Complete guide for deploying MCP Memory Cloud to production with automatic plugin onboarding.

## 📋 Overview

The MCP Memory Cloud is a fully containerized system that provides:

- **🚀 Auto-Onboarding**: When users install plugins, they're automatically directed to signup
- **💳 Stripe Integration**: Automatic billing and subscription management 
- **📊 Multi-Tenant**: Each user gets isolated MongoDB database
- **🔧 Plugin Support**: Claude, Cursor, ChatGPT, Lovable, Replit
- **📈 Scalable**: Docker-based microservices architecture

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx Proxy   │────│  React Frontend │    │  API Gateway    │
│  (SSL/Routing)  │    │  (Signup/UI)    │    │ (Main Service)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┤
                                 │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Billing Service │    │      Redis      │    │ Background      │
│   (Stripe)      │    │    (Cache)      │    │   Worker        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  MongoDB Atlas  │
                    │ (Multi-tenant)  │
                    └─────────────────┘
```

## 🚀 Quick Start

### 1. Prerequisites

```bash
# Install Docker & Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

### 2. Clone and Configure

```bash
# Clone repository
git clone https://github.com/AiGotsrl/mcp-memory-server.git
cd mcp-memory-server

# Configure environment
cp .env.production .env.production.local
nano .env.production.local  # Add your MongoDB Atlas and Stripe keys
```

### 3. Deploy

```bash
# Make deployment script executable
chmod +x deployment/deploy.sh

# Full deployment
./deployment/deploy.sh deploy
```

## ⚙️ Configuration

### Environment Variables

Create `.env.production` with your configuration:

```bash
# MongoDB Atlas (Get from: https://cloud.mongodb.com)
MONGODB_ATLAS_PUBLIC_KEY=your_atlas_public_key
MONGODB_ATLAS_PRIVATE_KEY=your_atlas_private_key  
MONGODB_ATLAS_PROJECT_ID=your_project_id
MONGODB_MASTER_CONNECTION=mongodb+srv://user:pass@cluster.mongodb.net/mcp_memory_master

# Stripe (Get from: https://dashboard.stripe.com/apikeys)
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Domains
API_BASE_URL=https://api.mcpmemory.cloud
FRONTEND_URL=https://mcpmemory.cloud

# Security
JWT_SECRET=$(openssl rand -base64 32)
```

### DNS Configuration

Point your domains to your server:

```
A    mcpmemory.cloud      → YOUR_SERVER_IP
A    api.mcpmemory.cloud  → YOUR_SERVER_IP
```

### SSL Certificates

For production, place real SSL certificates in `deployment/ssl/`:

```bash
# Copy your certificates
cp your-domain.crt deployment/ssl/cert.pem
cp your-domain.key deployment/ssl/key.pem

# Or use Let's Encrypt
certbot certonly --webroot -w /var/www/html -d mcpmemory.cloud -d api.mcpmemory.cloud
cp /etc/letsencrypt/live/mcpmemory.cloud/fullchain.pem deployment/ssl/cert.pem
cp /etc/letsencrypt/live/mcpmemory.cloud/privkey.pem deployment/ssl/key.pem
```

## 🔧 Plugin Auto-Setup Flow

### How It Works

1. **Plugin Installation**: User installs MCP Memory plugin in Claude/Cursor/ChatGPT
2. **Onboarding Request**: Plugin calls `/api/v1/onboard` with plugin type
3. **Browser Redirect**: User directed to `https://mcpmemory.cloud/signup?session=XXX&plugin=claude`
4. **Account Creation**: User enters email, chooses plan, pays with Stripe
5. **Auto-Configuration**: Plugin receives API key and configures itself

### Plugin Integration Code

Each plugin includes auto-setup code like this:

```python
# plugins/claude_auto_setup.py
import httpx
import webbrowser

async def setup_plugin():
    # Request onboarding session
    response = await httpx.post("https://api.mcpmemory.cloud/api/v1/onboard", json={
        "plugin_type": "claude",
        "user_id": None,
        "return_url": "claude://plugin-configured"
    })
    
    # Open browser for signup
    data = response.json()
    webbrowser.open(data["signup_url"])
    
    # Wait for completion
    while True:
        status = await httpx.get(f"https://api.mcpmemory.cloud/api/v1/onboard/status/{data['session_id']}")
        if status.json()["status"] == "completed":
            api_key = status.json()["api_key"]
            # Configure plugin with API key
            break
        await asyncio.sleep(5)
```

## 📊 Services

### API Gateway (`api-gateway:8000`)

Main service handling:
- Plugin onboarding requests
- Memory operations (save/search)
- User authentication
- Plugin configuration

### Frontend (`frontend:3000`) 

React app providing:
- User signup with Stripe
- Plan selection
- Account dashboard
- Billing management

### Billing Service (`billing-service:8001`)

Stripe integration for:
- Subscription management
- Usage-based billing
- Invoice generation
- Webhook handling

### Background Worker (`worker`)

Processes:
- Memory embeddings
- Usage calculations
- Email notifications
- Maintenance tasks

### Redis (`redis:6379`)

Caching for:
- Session data
- API rate limiting
- Background job queue
- System metrics

## 🔍 Monitoring

### Health Checks

```bash
# API Gateway
curl https://api.mcpmemory.cloud/health

# Frontend
curl https://mcpmemory.cloud

# Service status
./deployment/deploy.sh status
```

### Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api-gateway
docker-compose logs -f billing-service
docker-compose logs -f frontend
```

### Metrics

Access Prometheus metrics at:
- API Gateway: `http://localhost:8000/metrics`
- Billing Service: `http://localhost:8001/metrics`

## 🚀 Scaling

### Horizontal Scaling

```yaml
# docker-compose.override.yml
version: '3.8'
services:
  api-gateway:
    deploy:
      replicas: 3
  
  billing-service:
    deploy:
      replicas: 2
```

### Load Balancer

Nginx automatically load balances between replicas:

```nginx
upstream api_gateway {
    server api-gateway-1:8000;
    server api-gateway-2:8000;
    server api-gateway-3:8000;
}
```

## 💾 Backup & Recovery

### Database Backup

```bash
# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
mongodump --uri="$MONGODB_MASTER_CONNECTION" --out="/backups/mcp_memory_$DATE"
tar -czf "/backups/mcp_memory_$DATE.tar.gz" "/backups/mcp_memory_$DATE"
rm -rf "/backups/mcp_memory_$DATE"

# Keep only last 7 days
find /backups -name "mcp_memory_*.tar.gz" -mtime +7 -delete
```

### Application Backup

```bash
# Backup configuration and data
tar -czf mcp_backup_$(date +%Y%m%d).tar.gz \
    .env.production \
    deployment/ssl/ \
    logs/ \
    data/
```

## 🔒 Security

### Best Practices

1. **Use real SSL certificates** in production
2. **Rotate API keys** regularly
3. **Enable Stripe webhooks** for real-time events
4. **Monitor failed login attempts**
5. **Keep Docker images updated**

### Security Headers

Nginx automatically adds:
- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `Strict-Transport-Security`
- Rate limiting on API endpoints

## 🛠️ Maintenance

### Updates

```bash
# Update application
git pull
./deployment/deploy.sh update

# Update system packages
apt update && apt upgrade -y
docker system prune -f
```

### Database Maintenance

```bash
# MongoDB index optimization
docker-compose exec api-gateway python -c "
import asyncio
from cloud.mongodb_provisioner import MongoDBCloudProvisioner

async def optimize():
    provisioner = MongoDBCloudProvisioner()
    await provisioner.initialize()
    await provisioner.master_db.users.reindex()
    print('Database optimized')

asyncio.run(optimize())
"
```

## 📞 Support

### Troubleshooting

Common issues and solutions:

1. **SSL Certificate Issues**
   ```bash
   ./deployment/deploy.sh ssl
   ```

2. **Database Connection Failed**
   ```bash
   # Check MongoDB Atlas whitelist
   # Verify connection string in .env
   ```

3. **Stripe Webhook Failed**
   ```bash
   # Update webhook URL in Stripe dashboard
   # Check webhook secret in .env
   ```

### Support Channels

- **GitHub Issues**: [Report bugs](https://github.com/AiGotsrl/mcp-memory-server/issues)
- **Documentation**: [Full docs](https://docs.mcpmemory.cloud)
- **Community**: [Discord server](https://discord.gg/mcpmemory)

## 🎯 Next Steps

After successful deployment:

1. **Test Plugin Installation**: Install Claude/Cursor plugins
2. **Monitor Usage**: Check logs and metrics
3. **Scale as Needed**: Add more replicas for high traffic
4. **Set Up Alerts**: Monitor system health
5. **Regular Backups**: Automate backup procedures

Your MCP Memory Cloud is now ready to provide seamless AI memory across all supported platforms! 🚀 