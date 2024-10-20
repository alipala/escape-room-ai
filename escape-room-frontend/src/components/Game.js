import React, { useState, useEffect} from 'react';
import { Button, TextField, Select, MenuItem, FormControl, InputLabel, Typography, Box, Paper } from '@mui/material';
import { createGame, createUser, generatePuzzle, checkAnswer } from '../services/api';

function Game() {
  const [gameData, setGameData] = useState({
    user_id: localStorage.getItem('userId') || null,
    theme: '',
    difficulty: 1,
    age_group: ''
  });

  useEffect(() => {
    createTestUser();
  }, []);

  const [gameId, setGameId] = useState(null);
  const [puzzle, setPuzzle] = useState(null);
  const [answer, setAnswer] = useState('');
  const [feedback, setFeedback] = useState('');

  const handleInputChange = (e) => {
    setGameData({ ...gameData, [e.target.name]: e.target.value });
  };

  const createTestUser = async () => {
    try {
      const response = await createUser({
        username: "testuser",
        email: "testuser@example.com",
        password: "testpassword"
      });
      console.log("User created:", response.data);
      localStorage.setItem('userId', response.data.id);
      setGameData(prevData => ({ ...prevData, user_id: response.data.id }));
    } catch (error) {
      console.error("Error creating user:", error);
    }
  };

  const handleCreateGame = async () => {
    if (!gameData.user_id) {
      setFeedback('Please create a user first or log in.');
      return;
    }
    try {
      const response = await createGame(gameData);
      setGameId(response.data.id);
      setFeedback('Game created successfully! Generate a puzzle to start playing.');
    } catch (error) {
      console.error('Error creating game:', error);
      setFeedback(`Error creating game: ${error.response?.data?.detail || error.message}`);
    }
  };

  const handleCreateGame = async () => {
    try {
      const response = await createGame(gameData);
      setGameId(response.data.id);
      setFeedback('Game created successfully! Generate a puzzle to start playing.');
    } catch (error) {
      console.error('Error creating game:', error);
      if (error.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        setFeedback(`Error creating game: ${error.response.data.detail || error.response.statusText}`);
      } else if (error.request) {
        // The request was made but no response was received
        setFeedback('Error creating game: No response received from server');
      } else {
        // Something happened in setting up the request that triggered an Error
        setFeedback(`Error creating game: ${error.message}`);
      }
    }
  };

  const handleGeneratePuzzle = async () => {
    if (!gameId) {
      setFeedback('Please create a game first.');
      return;
    }
    try {
      const response = await generatePuzzle(gameId);
      setPuzzle(response.data);
      setFeedback('New puzzle generated!');
    } catch (error) {
      setFeedback('Error generating puzzle. Please try again.');
      console.error('Error generating puzzle:', error);
    }
  };

  const handleCheckAnswer = async () => {
    if (!puzzle) {
      setFeedback('Please generate a puzzle first.');
      return;
    }
    try {
      const response = await checkAnswer({ puzzle_id: puzzle.id, answer });
      if (response.data.correct) {
        setFeedback('Correct answer! Well done!');
        setPuzzle(null);
      } else {
        setFeedback('Incorrect answer. Try again!');
      }
    } catch (error) {
      setFeedback('Error checking answer. Please try again.');
      console.error('Error checking answer:', error);
    }
  };

  return (
    <Box sx={{ maxWidth: 600, margin: 'auto', mt: 4 }}>
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          AI-Enhanced Escape Room
        </Typography>
        
        <FormControl fullWidth margin="normal">
          <TextField
            name="theme"
            label="Theme"
            value={gameData.theme}
            onChange={handleInputChange}
          />
        </FormControl>
        
        <FormControl fullWidth margin="normal">
          <InputLabel>Difficulty</InputLabel>
          <Select
            name="difficulty"
            value={gameData.difficulty}
            onChange={handleInputChange}
          >
            <MenuItem value={1}>Easy</MenuItem>
            <MenuItem value={2}>Medium</MenuItem>
            <MenuItem value={3}>Hard</MenuItem>
          </Select>
        </FormControl>
        
        <FormControl fullWidth margin="normal">
          <TextField
            name="age_group"
            label="Age Group"
            value={gameData.age_group}
            onChange={handleInputChange}
          />
        </FormControl>
        
        <Button variant="contained" color="primary" onClick={handleCreateGame} sx={{ mt: 2 }}>
          Create Game
        </Button>
        
        {gameId && (
          <Button variant="contained" color="secondary" onClick={handleGeneratePuzzle} sx={{ mt: 2, ml: 2 }}>
            Generate Puzzle
          </Button>
        )}
        
        {puzzle && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h6">Puzzle:</Typography>
            <Typography>{puzzle.question}</Typography>
            <TextField
              fullWidth
              label="Your Answer"
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              margin="normal"
            />
            <Button variant="contained" color="primary" onClick={handleCheckAnswer}>
              Submit Answer
            </Button>
          </Box>
        )}
        
        {feedback && (
          <Typography sx={{ mt: 2, fontWeight: 'bold' }}>{feedback}</Typography>
        )}
      </Paper>
    </Box>
  );
}

export default Game;