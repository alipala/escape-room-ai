## Project Overview
This project implements an AI-enhanced escape room game using FastAPI for the backend, SQLAlchemy for database operations, and integrates AI services like OpenAI and Pinecone for dynamic content generation. The game features adaptive difficulty, multi-agent content generation, and retrieval-augmented generation for enhanced gameplay experiences.

## File Structure
escape-ai/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models/
│   │   └── models.py
│   ├── routes/
│   │   ├── game.py
│   │   └── user.py
│   ├── services/
│   │   ├── game_service.py
│   │   ├── rag_service.py
│   │   ├── llm_service.py
│   │   └── multiagent_service.py
│   └── utils/
│       ├── database.py
│       └── logger.py
├── alembic/
│   └── versions/
├── data/
│   └── sample_themes.json
├── venv/
├── .env
├── requirements.txt
├── alembic.ini
└── run.py

## Key Components

### 1. models/models.py

Defines SQLAlchemy models for User, Game, and Puzzle:
- User: Represents a player
- Game: Represents an escape room game instance
- Puzzle: Represents individual puzzles within a game

### 2. routes/game.py

Defines API endpoints for game-related operations:
- POST /games: Create a new game
- POST /games/{game_id}/puzzles: Generate a new puzzle for a game
- POST /puzzles/check-answer: Check the answer for a puzzle
- GET /games/{game_id}: Get the current state of a game

### 3. services/game_service.py

GameService class handles game logic and database operations:
- create_game: Creates a new game instance
- generate_dynamic_puzzle: Generates a puzzle with dynamic difficulty
- check_answer: Checks if a submitted answer is correct
- update_puzzle_performance: Updates puzzle metrics based on player performance

### 4. services/rag_service.py

RAGService class implements Retrieval-Augmented Generation:
- Uses FAISS for efficient similarity search
- load_data: Loads and processes data from a JSON file
- query: Performs similarity search on loaded data

### 5. services/llm_service.py

LLMService class interacts with OpenAI's GPT model:
- generate_puzzle: Creates a puzzle using the LLM based on theme, difficulty, and age group

### 6. services/multiagent_service.py

MultiagentService class implements a multi-agent system for content generation:
- Uses CrewAI to create a team of AI agents (Storyteller, Puzzle Master, Difficulty Scaler)
- generate_game_content: Generates game content using the multi-agent system

### 7. utils/database.py

- Sets up database connection using SQLAlchemy
- Provides a get_db function for dependency injection in FastAPI routes

### 8. utils/logger.py

- Sets up a custom logger for the application

### 9. main.py

- FastAPI application setup
- Includes routers and sets up database

### 10. run.py

- Entry point for running the FastAPI application

## Key Features

- Dynamic puzzle generation based on theme, difficulty, and age group
- Adaptive difficulty scaling based on player performance
- Multi-agent system for rich content generation
- Retrieval-Augmented Generation for enhancing game content
- User management system

## Database Structure and Schema

The database consists of three main tables: Users, Games, and Puzzles.

### Users Table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(100) NOT NULL
);

### Games Table
CREATE TABLE games (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    theme VARCHAR(100) NOT NULL,
    difficulty INTEGER NOT NULL,
    age_group VARCHAR(50) NOT NULL,
    score INTEGER DEFAULT 0,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP
);

### Puzzles Table
CREATE TABLE puzzles (
    id SERIAL PRIMARY KEY,
    game_id INTEGER REFERENCES games(id),
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    hints TEXT,
    difficulty FLOAT DEFAULT 1.0,
    attempts INTEGER DEFAULT 0,
    time_spent FLOAT DEFAULT 0.0,
    solved BOOLEAN DEFAULT FALSE
);

## Testing the Game
### 1. Create a new user:
curl -X POST http://localhost:8000/users/ \
     -H "Content-Type: application/json" \
     -d '{
         "username": "testplayer",
         "email": "testplayer@example.com",
         "password": "securepassword"
     }'

### 2. Create a new game:
curl -X POST http://localhost:8000/games \
     -H "Content-Type: application/json" \
     -d '{
         "user_id": 1,
         "theme": "Space Adventure",
         "difficulty": 1,
         "age_group": "teen"
     }'

### 3. Generate a new puzzle for the game (replace {game_id} with the id returned from the previous command):
curl -X POST http://localhost:8000/games/{game_id}/puzzles

### 4. Get the current state of the game:
curl http://localhost:8000/games/{game_id}

### 5. Check an answer for a puzzle (replace {puzzle_id} with an actual puzzle id):
curl -X POST http://localhost:8000/puzzles/check-answer \
     -H "Content-Type: application/json" \
     -d '{
         "puzzle_id": {puzzle_id},
         "answer": "your answer here"
     }'

### Update puzzle performance (replace {puzzle_id} with an actual puzzle id):
curl -X POST http://localhost:8000/puzzles/{puzzle_id}/performance \
     -H "Content-Type: application/json" \
     -d '{
         "time_spent": 120.5,
         "attempts": 2,
         "solved": true
     }'