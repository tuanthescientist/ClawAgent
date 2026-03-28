# 🚀 ClawAgent - Getting Started

## Quick Setup for Local Testing

### 1. Install Dependencies
```bash
cd "d:\Data Science\ClawAgent"
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy the example env file
copy .env.example .env

# Edit .env with your credentials:
# - OPENAI_API_KEY: Get from https://platform.openai.com/api-keys
# - TWILIO_ACCOUNT_SID: Get from https://console.twilio.com
# - TWILIO_AUTH_TOKEN: Get from https://console.twilio.com
# - TWILIO_WHATSAPP_NUMBER: Your Twilio WhatsApp sandbox number
```

### 3. Run Locally
```bash
python -m src.main
```

The API will be available at: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

### 4. Push to GitHub

The repository has been initialized locally. To push to GitHub:

```bash
# Option A: Using HTTPS with Personal Access Token
cd "d:\Data Science\ClawAgent"
git push -u origin master

# When prompted:
# Username: tuanthescientist
# Password: <Your GitHub Personal Access Token>

# Option B: Using SSH (if configured)
git remote set-url origin git@github.com:tuanthescientist/ClawAgent.git
git push -u origin master
```

**Get GitHub Personal Access Token:**
1. Go to GitHub Settings > Developer Settings > Personal Access Tokens
2. Click "Generate new token"
3. Select: `repo` (Full control of private repositories)
4. Copy and use as password when pushing

### 5. Test WhatsApp Integration

Local testing options:

**Option A: Using ngrok for webhooks**
```bash
# Install ngrok: https://ngrok.com/download
ngrok http 8000

# Configure Twilio webhook:
# In Twilio Console > Sandbox > When a message comes in:
# https://your-ngrok-url/api/v1/whatsapp/webhook
```

**Option B: Production Deployment**
- Deploy to Heroku, AWS, DigitalOcean, or Render
- Update Twilio webhook URL to your deployed server

## 📚 Available Make Commands

```bash
make install     # Install dependencies
make dev         # Run development server
make test        # Run tests
make lint        # Check code quality
make format      # Auto-format code
make clean       # Clean cache files
make docker-build # Build Docker image
make docker-run   # Run with Docker
```

## 🔧 API Overview

### POST /api/v1/chat
Send a message to the agent:
```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "chat_id": "user-123"}'
```

### POST /api/v1/whatsapp/webhook
Receives WhatsApp messages from Twilio (automatic setup)

### GET /health
Check if API is running

## 🆘 Troubleshooting

**HTTP 422 Validation Error**
- Make sure your .env file has all required variables
- Check OPENAI_API_KEY and Twilio credentials

**WhatsApp messages not received**
- Verify ngrok URL in Twilio settings
- Check webhook token matches in .env
- Look at server logs for errors

**Rate limiting errors**
- You're hitting OpenAI API limits
- Wait a bit or upgrade your OpenAI plan

## 📞 Support

- **Docs**: http://localhost:8000/docs
- **GitHub Issues**: https://github.com/tuanthescientist/ClawAgent/issues
- **README**: See README.md for full documentation

---

**Next Steps:**
1. ✅ Repository structure created
2. ✅ Configure .env file
3. ✅ Run `make dev` to start
4. ✅ Push to GitHub using the commands above
