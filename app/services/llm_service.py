import openai
from app.utils.logger import setup_logger
from openai import OpenAI
import os

logger = setup_logger()


class LLMService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def generate_puzzle(self, theme: str, difficulty: float, age_group: str):
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a creative puzzle designer for an escape room game."},
                    {"role": "user", "content": f"Create a puzzle with theme '{theme}', difficulty {difficulty}/2.0, for {age_group} age group. Include a question, answer, and hint."}
                ]
            )
            puzzle_content = response.choices[0].message.content
            
            # Simple parsing logic (you might want to improve this)
            lines = puzzle_content.split('\n')
            question = next((line for line in lines if line.startswith("Question:")), "").replace("Question:", "").strip()
            answer = next((line for line in lines if line.startswith("Answer:")), "").replace("Answer:", "").strip()
            hint = next((line for line in lines if line.startswith("Hint:")), "").replace("Hint:", "").strip()
            
            return {"question": question, "answer": answer, "hint": hint}
        except Exception as e:
            logger.error(f"Error generating puzzle with LLM: {str(e)}")
            return {"question": f"Default question for {theme}", "answer": "Default answer", "hint": "Default hint"}