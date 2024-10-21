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

class PuzzlePerformance(BaseModel):
    time_spent: float
    attempts: int
    solved: bool

@router.post("/games/{game_id}/puzzles")
def generate_puzzle(game_id: int, db: Session = Depends(get_db)):
    game_service = GameService(db)
    try:
        puzzle = game_service.generate_dynamic_puzzle(game_id)
        return puzzle
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/puzzles/{puzzle_id}/performance")
def update_puzzle_performance(puzzle_id: int, performance: PuzzlePerformance, db: Session = Depends(get_db)):
    game_service = GameService(db)
    try:
        updated_puzzle = game_service.update_puzzle_performance(
            puzzle_id, performance.time_spent, performance.attempts, performance.solved
        )
        return updated_puzzle
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/games")
def create_game(game: GameCreate, db: Session = Depends(get_db)):
    game_service = GameService(db)
    rag_service = RAGService()
    multiagent_service = MultiagentService()

    try:
        # Create the game
        new_game = game_service.create_game(game.user_id, game.theme, game.difficulty, game.age_group)

        # Generate game content using the multiagent service
        try:
            game_content = multiagent_service.generate_game_content(game.theme, game.age_group, game.difficulty)
            game_content_str = str(game_content)  # Convert CrewOutput to string
        except Exception as e:
            logger.error(f"Error generating game content: {str(e)}")
            game_content_str = f"Default content for {game.theme}"

        # Use RAG to enhance the game content
        try:
            rag_service.load_data("data/sample_themes.json")
            enhanced_content = rag_service.query(game_content_str)
        except Exception as e:
            logger.warning(f"RAG service failed: {str(e)}. Proceeding with original game content.")
            enhanced_content = [game_content_str]

        # Generate puzzles based on the enhanced content
        puzzles = []
        for content in enhanced_content:
            try:
                puzzle = game_service.generate_dynamic_puzzle(new_game.id)
                puzzles.append(puzzle)
            except Exception as e:
                logger.error(f"Error generating puzzle: {str(e)}")

        return {
            "game_id": new_game.id,
            "theme": new_game.theme,
            "difficulty": new_game.difficulty,
            "age_group": new_game.age_group,
            "puzzles": [
                {
                    "id": p.id,
                    "question": p.question,
                    "hints": p.hints,
                    "difficulty": p.difficulty,
                    "answer": p.answer if game.user_id == 1 else "Hidden"  # Only show answer for admin (user_id 1)
                } for p in puzzles
            ]
        }
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

@router.get("/games/{game_id}")
def get_game_state(game_id: int, db: Session = Depends(get_db)):
    game_service = GameService(db)
    try:
        game = game_service.get_game(game_id)
        if not game:
            raise HTTPException(status_code=404, detail="Game not found")
        
        puzzles = game_service.get_game_puzzles(game_id)
        return {
            "game_id": game.id,
            "theme": game.theme,
            "difficulty": game.difficulty,
            "score": game.score,
            "start_time": game.start_time,
            "end_time": game.end_time,
            "puzzles": puzzles
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))