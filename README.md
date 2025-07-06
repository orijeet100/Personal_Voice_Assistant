# 🎙️ Voice Assistant: Multi-Modal AI Assistant

A sophisticated voice and text-based AI assistant that combines speech recognition, natural language processing, and integration with external services like Spotify and Gmail. Built with modern web technologies and AI capabilities.

## ✨ Features

### 🎵 **Music Control**
- **Voice-activated Spotify playback** - Control your music with natural language
- **Semantic song search** - Find songs in your liked tracks using AI-powered search
- **Multi-device support** - Play music on any connected Spotify device
- **FAISS-powered indexing** - Fast and accurate song matching

### 📧 **Email Management**
- **Voice-to-email** - Compose and send emails using voice commands
- **Contact integration** - Automatically select recipients from your contact list
- **Gmail API integration** - Seamless email sending through Gmail
- **Context-aware responses** - AI generates personalized email content

### 🎤 **Voice & Text Interface**
- **Dual input modes** - Switch between voice recording and text input
- **Real-time speech recognition** - Browser-based speech-to-text
- **Conversation history** - Track your interactions with the assistant
- **Modern UI** - Beautiful, responsive interface built with React and Tailwind CSS

### 🤖 **AI-Powered Intelligence**
- **Intent classification** - Automatically route requests to appropriate services
- **Natural language processing** - Understand context and user intent
- **Multi-agent architecture** - Specialized agents for different tasks
- **OpenAI integration** - Leverages GPT models for intelligent responses

## 🏗️ Architecture

### Frontend (React + TypeScript)
```
frontend/
├── src/
│   ├── components/
│   │   └── VoiceToText.tsx    # Main voice/text interface
│   ├── pages/
│   │   └── Index.tsx          # Main application page
│   └── App.tsx               # Application routing
```

### Backend (FastAPI + Python)
```
backend/
├── main.py                   # FastAPI server with endpoints
├── agents/
│   ├── spotify_agent.py      # Spotify music control
│   ├── email_agent.py        # Gmail email management
│   └── intent_agent.py       # Intent classification
├── liked_songs_faiss.index   # FAISS index for song search
└── contacts.csv              # Contact list for email
```

### Streamlit Alternative
```
streamlit_app.py              # Simple Streamlit interface
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Spotify Premium account
- Gmail account
- OpenAI API key

### 1. Clone and Setup
```bash
git clone <repository-url>
cd Voice_Assistant
```

### 2. Backend Setup
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

### 4. Spotify Setup
1. Create a Spotify app at [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Add your redirect URI: `http://127.0.0.1:8888/callback`
3. Update the client ID and secret in the backend code

### 5. Gmail Setup
1. Enable Gmail API in Google Cloud Console
2. Download `client_secret.json` to the backend directory
3. Run the app once to authenticate and generate `token.json`

### 6. Run the Application

**Option A: Full Stack (Recommended)**
```bash
# Terminal 1: Backend
cd backend
uvicorn main:app --reload --port 8001

# Terminal 2: Frontend
cd frontend
npm run dev
```

**Option B: Streamlit Only**
```bash
streamlit run streamlit_app.py
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
```

### Spotify Configuration
The app uses these Spotify scopes:
- `user-library-read` - Access to liked songs
- `user-read-playback-state` - Read current playback
- `user-modify-playback-state` - Control playback

### Gmail Configuration
The app requires Gmail API access for:
- Sending emails
- Managing contacts

## 📖 Usage Examples

### Music Commands
- "Play Bohemian Rhapsody"
- "I want to listen to some jazz"
- "Play something upbeat"
- "Start my workout playlist"

### Email Commands
- "Send an email to Mom about dinner plans"
- "Email John about the meeting tomorrow"
- "Write to Sarah about the project update"

### Voice Interface
1. Click the microphone button to start voice recording
2. Speak your command clearly
3. The assistant will process and execute your request
4. View the conversation history below

### Text Interface
1. Type your message in the text input
2. Press Enter or click Send
3. The assistant will respond with the appropriate action

## 🛠️ Technical Details

### AI Models Used
- **OpenAI GPT-3.5-turbo** - Natural language processing and response generation
- **OpenAI Whisper** - Speech-to-text transcription
- **Sentence Transformers** - Semantic search for songs
- **FAISS** - Vector similarity search

### Key Technologies
- **Frontend**: React, TypeScript, Tailwind CSS, Radix UI
- **Backend**: FastAPI, Python, Uvicorn
- **AI/ML**: OpenAI API, FAISS, Sentence Transformers
- **APIs**: Spotify Web API, Gmail API
- **Audio**: Web Speech API, Streamlit Audio Recorder

### Data Storage
- **FAISS Index**: Pre-computed embeddings for song search
- **CSV Files**: Contact information and metadata
- **JSON Files**: Song metadata and configuration

## 🔍 API Endpoints

### Backend API (Port 8001)
- `POST /api/query` - Main endpoint for processing user requests
- `GET /api/test` - Health check endpoint

### Request Format
```json
{
  "message": "Play Bohemian Rhapsody"
}
```

### Response Format
```json
{
  "status": "success",
  "message": "🎵 Now playing: 'Bohemian Rhapsody' by Queen",
  "top_matches": [...]
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT and Whisper APIs
- Spotify for music integration
- Google for Gmail API
- The open-source community for the amazing libraries used

## 🐛 Troubleshooting

### Common Issues

**Speech Recognition Not Working**
- Ensure you're using HTTPS or localhost
- Check browser permissions for microphone access
- Try refreshing the page

**Spotify Authentication Issues**
- Verify your Spotify app credentials
- Check that redirect URI matches exactly
- Clear browser cookies and try again

**Gmail API Errors**
- Ensure `client_secret.json` is in the backend directory
- Check that Gmail API is enabled in Google Cloud Console
- Verify the token.json file exists and is valid

**OpenAI API Errors**
- Verify your API key is correct and has sufficient credits
- Check that the API key has access to the required models

For more help, please open an issue on GitHub.

---

**Made with ❤️ using modern AI and web technologies** 