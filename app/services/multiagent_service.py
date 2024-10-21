from crewai import Agent, Task, Crew
from app.utils.logger import setup_logger

logger = setup_logger()

class MultiagentService:
    def __init__(self):
        self.storyteller = Agent(
            role='Storyteller',
            goal='Create engaging storylines and themes for escape rooms',
            backstory='You are a creative writer with a knack for crafting immersive narratives.'
        )
        self.puzzle_master = Agent(
            role='Puzzle Master',
            goal='Design challenging and age-appropriate puzzles',
            backstory='You are an expert in creating puzzles that are both fun and educational.'
        )
        self.difficulty_scaler = Agent(
            role='Difficulty Scaler',
            goal='Adjust puzzle complexity based on player age and skill level',
            backstory='You have a deep understanding of cognitive development and problem-solving skills across different age groups.'
        )

    def generate_game_content(self, theme: str, age_group: str, difficulty: int):
        try:
            crew = Crew(
                agents=[self.storyteller, self.puzzle_master, self.difficulty_scaler],
                tasks=[
                    Task(
                        description=f"Create a storyline for an escape room with the theme: {theme}",
                        agent=self.storyteller,
                        expected_output="A detailed storyline for the escape room"
                    ),
                    Task(
                        description=f"Design puzzles fitting the theme and appropriate for age group: {age_group}",
                        agent=self.puzzle_master,
                        expected_output="A list of puzzle ideas with descriptions"
                    ),
                    Task(
                        description=f"Adjust puzzle difficulty to level {difficulty} for age group {age_group}",
                        agent=self.difficulty_scaler,
                        expected_output="Difficulty-adjusted puzzle descriptions"
                    )
                ]
            )

            result = crew.kickoff()
            return str(result)  # Convert CrewOutput to string
        except Exception as e:
            logger.error(f"Error generating game content: {str(e)}")
            raise