# AI Chat Application with Personalized Memory

A full-stack AI chat application featuring persistent user memory, contextual conversations, and MongoDB-based personal data extraction/storage/retrieval. Built with Flask + MongoDB backend and React frontend.

## Key Features

- 🧠 **AI Persona (AIrana)** - 21-year-old female persona with core values and flirty conversation style
- 💾 **Dual Database Storage**
  - SQLite: Message history and user auth
  - MongoDB: Structured user data extraction/retrieval (personal info, preferences, goals)
- 🔄 **Contextual Memory System**
  - Short-term conversation context
  - Long-term user profile storage
  - Automated information extraction pipeline
- 📊 **Advanced Data Processing**
  - Multi-stage LLM extraction workflow
  - Real-time data merging/updating
  - Async background processing
- 🔐 **Secure Authentication**
  - Session-based user management
  - Protected routes
  - Credential encryption

## Tech Stack

**Frontend:**
- React + React Router
- Context API (State management)
- Axios (API calls)
- CSS Modules

**Backend:**
- Python Flask (REST API)
- MongoDB (User profiles/extracted data)
- SQLite (Messages/auth)
- DeepSeek API (LLM)
- Multi-threading (Background processing)

**AI Components:**
- 3-stage LLM pipeline:
  1. Message understanding
  2. Data extraction/retrieval
  3. Response generation
- Dynamic context management
- Personality enforcement system

## Installation

1. **Prerequisites**
- MongoDB Community Server [Install Guide](https://www.mongodb.com/docs/manual/installation/)
- Python 3.9+
- Node.js 16+

2. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/MacOS
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

3. Frontend Setup

```bash
cd ../frontend
npm install
```

4. Environment Setup
Create .env in backend:

```env
SECRET_KEY=your_flask_secret
DEEPSEEK_API_KEY=your_deepseek_key
MONGO_URI=mongodb://localhost:27017/aigirl
```
## Database Configuration
1. MongoDB

- Install and start MongoDB service

- Create aigirl database (auto-created on first connection)

- Collections will be created automatically per user

2. SQLite

- Auto-created in backend/aigirl.db on first run

## Running the Application
1. Start MongoDB Service

```bash
sudo systemctl start mongod  # Linux
brew services start mongodb-community  # MacOS
```
2. Start Backend

```bash
cd backend && python app.py
```

3. Start Frontend

```bash
cd frontend && npm start
```

Access at: http://localhost:3000

## Data Flow
1. User message → Flask API

2. Context enrichment (SQLite (conversation history) + temp Memory + MongoDB (Long-term memory))

3. Multi-stage processing:

	- Message understanding (DeepSeek, simulating thinking process)

	- Data extraction → MongoDB (For future retrieval)

	- Response generation (Persona-enforced)

4. Response → User + Storage

## Requirements (backend/requirements.txt)
```text
Flask
requests
openai
sqlalchemy
python-dotenv
werkzeug
Flask-Cors
pymongo
python-dateutil
Flask-Session
```
## Configuration Tips
MongoDB Scaling

For production: Use MongoDB Atlas URI

Add replica sets for high availability

Enable SSL for secure connections

Performance

Add Redis caching for frequent queries

Implement connection pooling for MongoDB

Use background workers for data processing

## License
MIT License
