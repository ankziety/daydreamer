# Daydreamer AI Web Interface

A modern web-based interface for the Daydreamer AI system, providing chat functionality, analytics, model management, and automated testing capabilities.

## Features

### 🚀 Core Features
- **Real-time Chat Interface**: Interact with Daydreamer AI through a modern chat interface
- **Conversation Management**: View, search, and manage conversation history
- **Model Configuration**: Adjust AI parameters and restart models
- **Analytics Dashboard**: Visualize conversation data and system performance
- **Automated Testing**: Run comprehensive test suites
- **Settings Management**: Configure application preferences

### 🎨 User Interface
- **Dark/Light Mode**: Toggle between themes with system preference detection
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Modern UI**: Clean, intuitive interface built with Tailwind CSS
- **Real-time Updates**: Live chat with WebSocket support

### 📊 Analytics & Monitoring
- **Conversation Analytics**: Track message counts, response times, and activity
- **System Metrics**: Monitor CPU, memory, and performance
- **Visual Charts**: Interactive charts using Recharts
- **Performance Tracking**: Response time analysis and uptime monitoring

### 🔧 Technical Features
- **SQLite Database**: Persistent storage for conversations and settings
- **RESTful API**: FastAPI backend with comprehensive endpoints
- **WebSocket Support**: Real-time communication
- **State Management**: Zustand for client-side state
- **TypeScript**: Full type safety throughout the application

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Daydreamer AI system (parent directory)

### Installation

1. **Clone and navigate to the web app directory:**
   ```bash
   cd web_app
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

4. **Build the frontend:**
   ```bash
   npm run build
   ```

5. **Start the development server:**
   ```bash
   # Terminal 1: Start backend
   python main.py
   
   # Terminal 2: Start frontend (optional for development)
   npm run dev
   ```

6. **Access the application:**
   - Backend API: http://localhost:8000
   - Frontend: http://localhost:3000 (dev mode) or http://localhost:8000 (production)

## Project Structure

```
web_app/
├── main.py                 # FastAPI backend application
├── database.py            # SQLAlchemy models and database utilities
├── requirements.txt       # Python dependencies
├── package.json          # Node.js dependencies
├── vite.config.ts        # Vite configuration
├── tailwind.config.js    # Tailwind CSS configuration
├── tsconfig.json         # TypeScript configuration
├── index.html            # Main HTML file
├── src/
│   ├── main.tsx          # React application entry point
│   ├── App.tsx           # Main app component with routing
│   ├── index.css         # Global styles and Tailwind imports
│   ├── stores/           # Zustand state management
│   │   ├── themeStore.ts # Theme management
│   │   └── chatStore.ts  # Chat state management
│   ├── components/       # Reusable UI components
│   │   ├── Layout.tsx    # Main layout with sidebar
│   │   └── ChatMessage.tsx # Individual chat message component
│   └── pages/            # Page components
│       ├── ChatPage.tsx      # Main chat interface
│       ├── AnalyticsPage.tsx # Analytics dashboard
│       ├── SettingsPage.tsx  # Settings management
│       ├── ModelsPage.tsx    # AI model configuration
│       ├── TestsPage.tsx     # Automated testing
│       └── ConversationsPage.tsx # Conversation history
└── data/                 # SQLite database files (created automatically)
```

## API Endpoints

### Chat
- `POST /api/chat` - Send a message to Daydreamer AI
- `GET /api/conversations` - Get conversation history
- `DELETE /api/conversations/{id}` - Delete a conversation
- `DELETE /api/conversations` - Clear all conversations

### Models
- `GET /api/models` - Get available models and configuration
- `POST /api/models/restart` - Restart AI model with new config

### Analytics
- `GET /api/analytics` - Get analytics data and metrics

### Settings
- `GET /api/settings` - Get application settings
- `POST /api/settings` - Update application settings

### WebSocket
- `WS /ws/chat` - Real-time chat connection

## Configuration

### Environment Variables
Create a `.env` file in the web_app directory:

```env
# Database
DATABASE_URL=sqlite:///data/daydreamer_web.db

# Server
HOST=0.0.0.0
PORT=8000

# Daydreamer AI
DAYDREAMER_MODEL=llama2
DAYDREAMER_TEMPERATURE=0.7
DAYDREAMER_MAX_TOKENS=2048

# Development
DEBUG=true
```

### Model Configuration
Configure AI models through the Models page or by modifying the default configuration in `main.py`.

## Development

### Running Tests
```bash
# Backend tests
pytest

# Frontend tests
npm test
```

### Code Formatting
```bash
# Python
black .

# TypeScript/JavaScript
npm run lint
```

### Building for Production
```bash
# Build frontend
npm run build

# The built files will be in the static/ directory
# The FastAPI server will serve them automatically
```

## Features in Detail

### Chat Interface
- Real-time messaging with Daydreamer AI
- Message history with timestamps
- Thinking and daydreaming time display
- Conversation context management
- Auto-scroll to latest messages

### Analytics Dashboard
- Conversation activity charts
- Response time analysis
- System performance metrics
- Popular topics visualization
- Daily activity tracking

### Model Management
- View available AI models
- Configure model parameters (temperature, max tokens)
- Restart models with new settings
- Test model functionality
- Monitor model performance

### Automated Testing
- API endpoint testing
- Model functionality testing
- Database operation testing
- Integration testing
- Test result tracking and statistics

### Settings Management
- Theme customization (light/dark/system)
- Auto-save preferences
- Notification settings
- API configuration
- Data management (export/import)

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure the Daydreamer AI system is properly installed and the Python path includes the parent directory.

2. **Database Errors**: Check that the `data/` directory exists and has write permissions.

3. **Model Loading Issues**: Verify that Ollama is running and the specified model is available.

4. **Frontend Build Errors**: Ensure all Node.js dependencies are installed and the build process completes successfully.

### Logs
- Backend logs are displayed in the terminal running `main.py`
- Frontend logs are available in the browser's developer console
- Database logs can be enabled by setting `DEBUG=true` in the environment

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is part of the Daydreamer AI system and follows the same license terms.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the Daydreamer AI documentation
3. Open an issue in the repository
4. Check the API documentation at `/docs` when the server is running