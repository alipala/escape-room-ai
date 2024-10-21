from sqlalchemy.orm import Session
from app.models.models import Game, Puzzle
from app.utils.logger import setup_logger
from app.services.llm_service import LLMService
import random

logger = setup_logger()

class GameService:
    def __init__(self, db: Session):
        self.db = db
        self.llm_service = LLMService()

    def create_game(self, user_id: int, theme: str, difficulty: int, age_group: str):
        try:
            game = Game(user_id=user_id, theme=theme, difficulty=difficulty, age_group=age_group)
            self.db.add(game)
            self.db.commit()
            self.db.refresh(game)
            return game
        except Exception as e:
            logger.error(f"Error creating game: {str(e)}")
            self.db.rollback()
            raise

    def get_game(self, game_id: int):
        game = self.db.query(Game).filter(Game.id == game_id).first()
        if game:
            # Ensure all puzzles for this game have a difficulty set
            for puzzle in game.puzzles:
                if puzzle.difficulty is None:
                    puzzle.difficulty = 1.0
            self.db.commit()
        return game

    def generate_dynamic_puzzle(self, game_id: int):
        try:
            game = self.get_game(game_id)
            if not game:
                raise ValueError(f"Game with id {game_id} not found")

            # Calculate average difficulty and performance of solved puzzles
            solved_puzzles = [p for p in game.puzzles if p.solved]
            if solved_puzzles:
                avg_difficulty = sum(p.difficulty for p in solved_puzzles) / len(solved_puzzles)
                avg_attempts = sum(p.attempts for p in solved_puzzles) / len(solved_puzzles)
                avg_time = sum(p.time_spent for p in solved_puzzles) / len(solved_puzzles)
            else:
                avg_difficulty = game.difficulty
                avg_attempts = 0
                avg_time = 0

            # Adjust difficulty based on performance
            new_difficulty = avg_difficulty
            if avg_attempts > 3:  # If average attempts are high, decrease difficulty
                new_difficulty -= 0.1
            elif avg_attempts < 2:  # If average attempts are low, increase difficulty
                new_difficulty += 0.1

            if avg_time > 300:  # If average time is more than 5 minutes, decrease difficulty
                new_difficulty -= 0.1
            elif avg_time < 60:  # If average time is less than 1 minute, increase difficulty
                new_difficulty += 0.1

            # Ensure difficulty stays within bounds
            new_difficulty = max(0.1, min(2.0, new_difficulty))

            # Generate puzzle content using LLM
            try:
                puzzle_content = self.llm_service.generate_puzzle(game.theme, new_difficulty, game.age_group)
            except Exception as e:
                logger.error(f"Error generating puzzle with LLM: {str(e)}")
                # Fallback to a default puzzle if LLM fails
                puzzle_content = {
                    "question": f"Default question for {game.theme}",
                    "answer": "Default answer",
                    "hint": "Default hint"
                }

            puzzle = Puzzle(
                game_id=game_id, 
                question=puzzle_content["question"],
                answer=puzzle_content["answer"],
                hints=puzzle_content["hint"],
                difficulty=new_difficulty
            )
            self.db.add(puzzle)
            self.db.commit()
            self.db.refresh(puzzle)
            return puzzle
        except Exception as e:
            logger.error(f"Error generating dynamic puzzle: {str(e)}")
            self.db.rollback()
            raise

    def check_answer(self, puzzle_id: int, user_answer: str):
        try:
            puzzle = self.get_puzzle(puzzle_id)
            if not puzzle:
                raise ValueError("Puzzle not found")

            is_correct = user_answer.lower() == puzzle.answer.lower()
            feedback = "Correct!" if is_correct else "Incorrect. Try again!"

            puzzle.attempts += 1
            if is_correct:
                puzzle.solved = True
                # Adjust difficulty based on attempts and time spent
                time_factor = min(puzzle.time_spent / 60, 5) / 5  # Normalize time spent to 0-1 range, cap at 5 minutes
                attempt_factor = min(puzzle.attempts, 5) / 5  # Normalize attempts to 0-1 range, cap at 5 attempts
                difficulty_adjustment = 0.1 * (1 - (time_factor + attempt_factor) / 2)
                puzzle.difficulty = max(0.1, min(2.0, puzzle.difficulty + difficulty_adjustment))
            
            self.db.commit()

            if not is_correct:
                if self.is_answer_close(user_answer, puzzle.answer):
                    feedback += " You're close!"
                else:
                    feedback += " You're not quite there yet."

            return is_correct, feedback
        except Exception as e:
            logger.error(f"Error checking answer: {str(e)}")
            raise

    def get_puzzle(self, puzzle_id: int):
        puzzle = self.db.query(Puzzle).filter(Puzzle.id == puzzle_id).first()
        if puzzle and puzzle.difficulty is None:
            puzzle.difficulty = 1.0
            self.db.commit()
        return puzzle

    def update_puzzle_performance(self, puzzle_id: int, time_spent: float, attempts: int, solved: bool):
        try:
            puzzle = self.get_puzzle(puzzle_id)
            if not puzzle:
                raise ValueError("Puzzle not found")

            puzzle.time_spent = time_spent
            puzzle.attempts = attempts
            puzzle.solved = solved
            self.db.commit()
            self.db.refresh(puzzle)
            return puzzle
        except Exception as e:
            logger.error(f"Error updating puzzle performance: {str(e)}")
            self.db.rollback()
            raise

    def get_game_puzzles(self, game_id: int):
        try:
            game = self.get_game(game_id)
            if not game:
                raise ValueError(f"Game with id {game_id} not found")

            puzzles = self.db.query(Puzzle).filter(Puzzle.game_id == game_id).all()
            return [
                {
                    "id": puzzle.id,
                    "question": puzzle.question,
                    "hints": puzzle.hints,
                    "difficulty": puzzle.difficulty or 1.0,  # Default to 1.0 if difficulty is None
                    "attempts": puzzle.attempts,
                    "time_spent": puzzle.time_spent,
                    "solved": puzzle.solved,
                    "answer": puzzle.answer if puzzle.solved else None  # Only include answer if puzzle is solved
                }
                for puzzle in puzzles
            ]
        except Exception as e:
            logger.error(f"Error getting game puzzles: {str(e)}")
            raise

    def is_answer_close(self, user_answer: str, correct_answer: str):
        # Implement a more sophisticated comparison logic here
        # This is just a simple example
        return len(set(user_answer.lower()) & set(correct_answer.lower())) > len(correct_answer) / 2