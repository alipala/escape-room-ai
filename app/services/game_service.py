import random
from app.models.models import Game, Puzzle
from app.utils.logger import setup_logger
from sqlalchemy.orm import Session

logger = setup_logger()

class GameService:
    def __init__(self, db: Session):
        self.db = db

    def create_game(self, user_id: int, theme: str, difficulty: int):
        try:
            game = Game(user_id=user_id, theme=theme, difficulty=difficulty)
            self.db.add(game)
            self.db.commit()
            self.db.refresh(game)
            return game
        except Exception as e:
            logger.error(f"Error creating game: {str(e)}")
            self.db.rollback()
            raise

    def generate_puzzle(self, game_id: int):
        try:
            # This is a placeholder. In a real implementation, you would use
            # the RAG service and multiagent service to generate puzzles.
            question = f"Sample question for game {game_id}"
            answer = "Sample answer"
            hints = "Sample hint"

            puzzle = Puzzle(game_id=game_id, question=question, answer=answer, hints=hints)
            self.db.add(puzzle)
            self.db.commit()
            self.db.refresh(puzzle)
            return puzzle
        except Exception as e:
            logger.error(f"Error generating puzzle: {str(e)}")
            self.db.rollback()
            raise

    def check_answer(self, puzzle_id: int, user_answer: str):
        try:
            puzzle = self.db.query(Puzzle).filter(Puzzle.id == puzzle_id).first()
            if not puzzle:
                raise ValueError("Puzzle not found")

            is_correct = user_answer.lower() == puzzle.answer.lower()
            feedback = "Correct!" if is_correct else "Incorrect. Try again!"

            if not is_correct:
                # Implement logic to determine if the answer is close
                if self.is_answer_close(user_answer, puzzle.answer):
                    feedback += " You're close!"
                else:
                    feedback += " You're not quite there yet."

            return is_correct, feedback
        except Exception as e:
            logger.error(f"Error checking answer: {str(e)}")
            raise

    def is_answer_close(self, user_answer: str, correct_answer: str):
        # Implement a more sophisticated comparison logic here
        # This is just a simple example
        return len(set(user_answer.lower()) & set(correct_answer.lower())) > len(correct_answer) / 2