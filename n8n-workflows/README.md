# n8n WhatsApp Workflows

This directory contains pre-built n8n workflows for integrating with the WhatsApp MCP server.

## Available Workflows

### 1. WhatsApp Auto-Reply (`whatsapp-auto-reply.json`)

**Purpose**: Automatically respond to incoming WhatsApp messages with predefined responses based on keywords.

**Features**:
- Webhook trigger for incoming messages
- Keyword-based response logic
- Ignores messages sent by the bot itself
- Customizable response templates

**Setup**:
1. Import the workflow into n8n
2. Update `YOUR_DROPLET_IP` with your actual server IP
3. Activate the workflow
4. Configure your WhatsApp bridge to send webhooks to: `http://your-n8n-instance/webhook/whatsapp-webhook`

### 2. WhatsApp CRM Sync (`whatsapp-crm-sync.json`)

**Purpose**: Periodically sync WhatsApp contacts with your CRM system.

**Features**:
- Scheduled execution every 6 hours
- Fetches all WhatsApp contacts
- Processes and formats contact data
- Syncs with external CRM API
- Handles contact deduplication

**Setup**:
1. Import the workflow into n8n
2. Update `YOUR_DROPLET_IP` with your actual server IP
3. Configure your CRM API endpoint and authentication
4. Adjust the schedule as needed
5. Activate the workflow

### 3. WhatsApp AI Assistant (`whatsapp-ai-assistant.json`)

**Purpose**: Provide AI-powered responses to WhatsApp messages using OpenAI GPT.

**Features**:
- Webhook trigger for incoming messages
- Fetches recent chat context for better responses
- Uses OpenAI GPT-4 for generating responses
- Context-aware conversations
- Natural language processing

**Setup**:
1. Import the workflow into n8n
2. Update `YOUR_DROPLET_IP` with your actual server IP
3. Configure OpenAI API credentials in n8n
4. Customize the AI system prompt as needed
5. Activate the workflow
6. Configure webhook URL in your WhatsApp bridge

## General Setup Instructions

### 1. Import Workflows

1. Open n8n interface
2. Go to "Workflows" → "Import from File"
3. Select the desired JSON file
4. Click "Import"

### 2. Configure Credentials

For workflows using external APIs, you'll need to set up credentials:

**OpenAI (for AI Assistant)**:
1. Go to n8n "Credentials" → "Create New"
2. Select "OpenAI"
3. Enter your OpenAI API key
4. Save and assign to the OpenAI node

**HTTP Authentication (for CRM)**:
1. Go to n8n "Credentials" → "Create New"
2. Select "Header Auth" or appropriate method
3. Configure authentication details
4. Save and assign to HTTP Request nodes

### 3. Update Configuration

In each workflow, update these placeholders:
- `YOUR_DROPLET_IP`: Replace with your Digital Ocean droplet IP
- `your-crm-api.com`: Replace with your actual CRM API endpoint
- Webhook paths: Ensure they match your setup

### 4. Configure WhatsApp Bridge Webhooks

Update your WhatsApp bridge configuration to send webhooks to n8n:

```go
// In your Go bridge, add webhook sending logic
func sendWebhook(messageData map[string]interface{}) {
    webhookURL := "http://your-n8n-instance/webhook/whatsapp-webhook"
    
    jsonData, _ := json.Marshal(messageData)
    resp, err := http.Post(webhookURL, "application/json", bytes.NewBuffer(jsonData))
    if err != nil {
        log.Printf("Failed to send webhook: %v", err)
    }
    defer resp.Body.Close()
}
```

## Workflow Customization

### Auto-Reply Customization

Modify the "Process Message" function node to add your own keywords and responses:

```javascript
// Add custom responses
if (lowerMessage.includes('booking')) {
  reply = 'To make a booking, please call us at +1-234-567-8900 or visit our website.';
} else if (lowerMessage.includes('hours')) {
  reply = 'We are open Monday-Friday 9AM-6PM, Saturday 10AM-4PM. Closed Sundays.';
}
```

### AI Assistant Customization

Modify the system prompt in the OpenAI node:

```
You are a customer service assistant for [Your Company Name]. 
You help customers with:
- Product inquiries
- Order status
- Technical support
- General questions

Always be professional, helpful, and concise.
```

### CRM Sync Customization

Modify the "Process Contacts" function to match your CRM's data structure:

```javascript
const processedContact = {
  firstName: contact.name?.split(' ')[0] || '',
  lastName: contact.name?.split(' ').slice(1).join(' ') || '',
  phone: contact.phone_number,
  source: 'whatsapp',
  customFields: {
    whatsapp_jid: contact.jid,
    last_whatsapp_activity: contact.last_seen
  }
};
```

## Monitoring and Troubleshooting

### Check Workflow Execution

1. Go to "Executions" in n8n
2. Check for failed executions
3. Review execution data and error messages

### Test Webhooks

Use curl to test webhook endpoints:

```bash
curl -X POST http://your-n8n-instance/webhook/whatsapp-webhook \
  -H "Content-Type: application/json" \
  -d '{
    "chat_jid": "1234567890@s.whatsapp.net",
    "content": "test message",
    "sender": "1234567890",
    "is_from_me": false
  }'
```

### Debug WhatsApp MCP API

Test your MCP server endpoints:

```bash
# Health check
curl http://your-droplet-ip:8000/health

# List available tools
curl http://your-droplet-ip:8000/tools

# Test send message
curl -X POST http://your-droplet-ip:8000/whatsapp/send-message \
  -H "Content-Type: application/json" \
  -d '{"chat_jid": "1234567890@s.whatsapp.net", "message": "Test"}'
```

## Best Practices

1. **Rate Limiting**: Be mindful of WhatsApp's rate limits to avoid account restrictions
2. **Error Handling**: Add error handling nodes to manage failures gracefully
3. **Logging**: Use the "No Operation" node to log important data
4. **Testing**: Test workflows thoroughly before deploying to production
5. **Monitoring**: Set up alerts for workflow failures
6. **Backup**: Export and backup your workflows regularly

## Advanced Use Cases

### Multi-language Support

Add language detection and response translation:

```javascript
// Detect language and respond accordingly
const detectLanguage = (text) => {
  // Use a language detection service
  return 'en'; // default
};

const language = detectLanguage(message);
const responses = {
  'en': 'Thank you for your message!',
  'es': '¡Gracias por tu mensaje!',
  'fr': 'Merci pour votre message!'
};

reply = responses[language] || responses['en'];
```

### Sentiment Analysis

Add sentiment analysis to route messages:

```javascript
// Route based on sentiment
if (sentiment === 'negative') {
  // Route to priority queue
  reply = 'I understand your concern. A senior agent will contact you shortly.';
} else {
  reply = 'Thanks for your positive feedback!';
}
```

### Integration with Calendar Systems

Create appointment booking workflows:

```javascript
// Parse booking requests
if (message.includes('appointment') || message.includes('booking')) {
  // Trigger calendar integration workflow
  // Check availability and confirm booking
}
```
