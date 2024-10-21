from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.utils.logger import setup_logger
from app.services.game_service import GameService
from app.services.rag_service import RAGService
from app.services.multiagent_service import MultiagentService
from pydantic import BaseModel

# Set up logging
logger = setup_logger()


router = APIRouter()

class GameCreate(BaseModel):
    user_id: int
    theme: str
    difficulty: int
    age_group: str

class AnswerSubmit(BaseModel):
    puzzle_id: int
    answer: str

@router.post("/games")
def create_game(game: GameCreate, db: Session = Depends(get_db)):
    game_service = GameService(db)
    rag_service = RAGService()
    multiagent_service = MultiagentService()

    try:
        # Create the game
        new_game = game_service.create_game(game.user_id, game.theme, game.difficulty)

        # Generate game content using the multiagent service
        game_content = multiagent_service.generate_game_content(game.theme, game.age_group, game.difficulty)

        # Use RAG to enhance the game content
        try:
            rag_service.load_data("data/sample_themes.json")  # Load your dataset here
            enhanced_content = rag_service.query(game_content)
        except Exception as e:
            logger.warning(f"RAG service failed: {str(e)}. Proceeding with original game content.")
            enhanced_content = [game_content]

        # Generate puzzles based on the enhanced content
        puzzles = []
        for content in enhanced_content:
            puzzle = game_service.generate_puzzle(new_game.id)
            puzzles.append(puzzle)

        return {"game_id": new_game.id, "puzzles": puzzles}
    except Exception as e:
        logger.error(f"Error creating game: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/games/{game_id}/puzzles")
def generate_puzzle(game_id: int, db: Session = Depends(get_db)):
    game_service = GameService(db)
    try:
        puzzle = game_service.generate_puzzle(game_id)
        return puzzle
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/puzzles/check-answer")
def check_answer(answer_submit: AnswerSubmit, db: Session = Depends(get_db)):
    game_service = GameService(db)
    try:
        is_correct, feedback = game_service.check_answer(answer_submit.puzzle_id, answer_submit.answer)
        return {"is_correct": is_correct, "feedback": feedback}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
