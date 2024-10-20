import React, { useState } from 'react';
import { createGame, generatePuzzle } from '../services/api';
import log from '../utils/logger';
import { Button, TextField, Select, MenuItem, FormControl, InputLabel } from '@material-ui/core';

const Game = () => {
  const [gameData, setGameData] = useState({
    user_id: 1, // Replace with actual user ID
    theme: '',
    difficulty: 1,
    age_group: ''
  });
  const [gameId, setGameId] = useState(null);
  const [puzzle, setPuzzle] = useState(null);

  const handleInputChange = (e) => {
    setGameData({ ...gameData, [e.target.name]: e.target.value });
  };

  const handleCreateGame = async () => {
    try {
      log.info('Creating new game', gameData);
      const response = await createGame(gameData);
      setGameId(response.data.id);
      log.info('Game created successfully', response.data);
    } catch (error) {
      log.error('Error creating game', error);
    }
  };

  const handleGeneratePuzzle = async () => {
    if (!gameId) {
      log.warn('No game ID available');
      return;
    }
    try {
      log.info('Generating puzzle for game', gameId);
      const response = await generatePuzzle(gameId);
      setPuzzle(response.data);
      log.info('Puzzle generated successfully', response.data);
    } catch (error) {
      log.error('Error generating puzzle', error);
    }
  };

  return (
    <div>
      <h2>Create New Game</h2>
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
      <Button variant="contained" color="primary" onClick={handleCreateGame}>
        Create Game
      </Button>
      {gameId && (
        <Button variant="contained" color="secondary" onClick={handleGeneratePuzzle}>
          Generate Puzzle
        </Button>
      )}
      {puzzle && (
        <div>
          <h3>Puzzle</h3>
          <p>{puzzle.question}</p>
          {/* Add more puzzle display logic here */}
        </div>
      )}
    </div>
  );
};

export default Game;