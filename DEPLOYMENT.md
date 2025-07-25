# WhatsApp MCP Server - Digital Ocean Deployment Guide

This guide will help you deploy the WhatsApp MCP server on Digital Ocean and integrate it with n8n workflows.

## Prerequisites

1. Digital Ocean account
2. Docker installed locally (for testing)
3. n8n instance (can be hosted on Digital Ocean as well)

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌────────────────┐
│                 │    │                  │    │                │
│   n8n Workflow  │◄──►│ WhatsApp MCP API │◄──►│ WhatsApp Bridge│
│                 │    │   (Port 8000)    │    │  (Port 3000)   │
└─────────────────┘    └──────────────────┘    └────────────────┘
                                 │
                                 ▼
                       ┌──────────────────┐
                       │ SQLite Database  │
                       │ (Persistent Vol) │
                       └──────────────────┘
```

## Deployment Steps

### 1. Prepare Your Digital Ocean Droplet

Create a new droplet with the following specifications:
- **OS**: Ubuntu 22.04 LTS
- **Size**: Minimum 2GB RAM (for stable performance)
- **Datacenter**: Choose closest to your location
- **Additional Options**: Enable backups (recommended)

### 2. Initial Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
sudo apt install -y docker.io docker-compose
sudo systemctl enable docker
sudo systemctl start docker

# Add your user to docker group
sudo usermod -aG docker $USER
# Log out and log back in for group changes to take effect
```

### 3. Deploy the Application

```bash
# Clone the repository
git clone https://github.com/lharries/whatsapp-mcp.git
cd whatsapp-mcp

# Build and start the containers
docker-compose up -d

# Check logs
docker-compose logs -f
```

### 4. Initial WhatsApp Authentication

The first time you run the container, you'll need to authenticate with WhatsApp:

```bash
# View the logs to see the QR code
docker-compose logs whatsapp-mcp

# Scan the QR code with your WhatsApp mobile app
# The authentication will be saved in the persistent volume
```

### 5. Configure Firewall

```bash
# Allow HTTP traffic
sudo ufw allow 8000/tcp
sudo ufw allow 3000/tcp
sudo ufw enable
```

## API Endpoints

Once deployed, your WhatsApp MCP server will be available at:

- **Health Check**: `http://your-droplet-ip:8000/health`
- **Bridge Health**: `http://your-droplet-ip:3000/health`

### Main API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Server health status |
| `/tools` | GET | List available WhatsApp tools |
| `/execute` | POST | Execute any MCP tool |
| `/whatsapp/send-message` | POST | Send WhatsApp message |
| `/whatsapp/send-file` | POST | Send file via WhatsApp |
| `/whatsapp/chats` | GET | Get WhatsApp chats |
| `/whatsapp/messages` | GET | Get WhatsApp messages |
| `/whatsapp/contacts` | GET | Search WhatsApp contacts |

## n8n Integration

### Setting up n8n Workflows

1. **Create HTTP Request Node**:
   ```json
   {
     "method": "POST",
     "url": "http://your-droplet-ip:8000/whatsapp/send-message",
     "headers": {
       "Content-Type": "application/json"
     },
     "body": {
       "chat_jid": "1234567890@s.whatsapp.net",
       "message": "Hello from n8n!"
     }
   }
   ```

2. **Use Webhook Trigger**:
   - Set up webhook to receive WhatsApp messages
   - Process incoming messages with AI
   - Respond automatically

### Example n8n Workflow: Auto-Reply Bot

```json
{
  "name": "WhatsApp Auto-Reply",
  "nodes": [
    {
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "position": [250, 300],
      "parameters": {
        "path": "whatsapp-webhook",
        "httpMethod": "POST"
      }
    },
    {
      "name": "Process Message",
      "type": "n8n-nodes-base.function",
      "position": [450, 300],
      "parameters": {
        "functionCode": "// Extract message data\nconst messageData = items[0].json;\nconst message = messageData.message;\nconst chatJid = messageData.chat_jid;\n\n// Simple auto-reply logic\nlet reply = 'Thanks for your message!';\nif (message.toLowerCase().includes('help')) {\n  reply = 'How can I help you today?';\n}\n\nreturn [{\n  json: {\n    chat_jid: chatJid,\n    message: reply\n  }\n}];"
      }
    },
    {
      "name": "Send Reply",
      "type": "n8n-nodes-base.httpRequest",
      "position": [650, 300],
      "parameters": {
        "method": "POST",
        "url": "http://your-droplet-ip:8000/whatsapp/send-message",
        "headers": {
          "Content-Type": "application/json"
        },
        "body": "={{JSON.stringify($json)}}"
      }
    }
  ],
  "connections": {
    "Webhook": {
      "main": [
        [
          {
            "node": "Process Message",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Process Message": {
      "main": [
        [
          {
            "node": "Send Reply",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

## Available WhatsApp Tools

### 1. Send Message
```bash
curl -X POST http://your-droplet-ip:8000/whatsapp/send-message \
  -H "Content-Type: application/json" \
  -d '{
    "chat_jid": "1234567890@s.whatsapp.net",
    "message": "Hello from API!"
  }'
```

### 2. Send File
```bash
curl -X POST http://your-droplet-ip:8000/whatsapp/send-file \
  -H "Content-Type: application/json" \
  -d '{
    "chat_jid": "1234567890@s.whatsapp.net",
    "file_path": "/path/to/file.jpg",
    "caption": "Here is your file"
  }'
```

### 3. Get Messages
```bash
curl "http://your-droplet-ip:8000/whatsapp/messages?chat_jid=1234567890@s.whatsapp.net&limit=10"
```

### 4. Search Contacts
```bash
curl "http://your-droplet-ip:8000/whatsapp/contacts?query=John"
```

## Production Considerations

### 1. Security
- Use HTTPS with SSL certificates (Let's Encrypt)
- Implement API authentication
- Restrict access to specific IP addresses

### 2. Monitoring
- Set up health check monitoring
- Configure log aggregation
- Monitor disk space for SQLite database

### 3. Backup
- Regular database backups
- Container image backups
- Session data backups

### 4. Scaling
- Use load balancer for multiple instances
- Database replication if needed
- Container orchestration (Kubernetes)

## Troubleshooting

### Common Issues

1. **QR Code Not Appearing**:
   ```bash
   docker-compose logs whatsapp-mcp
   # Look for QR code in logs
   ```

2. **Connection Issues**:
   ```bash
   # Check if WhatsApp bridge is running
   curl http://your-droplet-ip:3000/health
   
   # Check if MCP server is running
   curl http://your-droplet-ip:8000/health
   ```

3. **Database Issues**:
   ```bash
   # Check persistent volumes
   docker volume ls
   docker volume inspect whatsapp-mcp_whatsapp_data
   ```

## Environment Variables

You can customize the deployment using environment variables:

```bash
# In docker-compose.yml
environment:
  - BRIDGE_HOST=0.0.0.0
  - BRIDGE_PORT=3000
  - MCP_HOST=0.0.0.0
  - MCP_PORT=8000
  - SQLITE_PATH=/app/store
  - LOG_LEVEL=INFO
```

## Support

For issues and questions:
1. Check the logs: `docker-compose logs`
2. Verify health endpoints
3. Check firewall and network settings
4. Review n8n workflow configuration
