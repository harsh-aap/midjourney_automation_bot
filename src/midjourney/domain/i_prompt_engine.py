# standard library imports
from abc import ABC, abstractmethod
from typing import Dict, Optional

# Internal Project Module Import
from midjourney.utils.logger.logger import Logger


class PromptEngine(ABC):
    @abstractmethod
    def generate_prompt(self, category: str, daily_factors: Dict,
                        logger: Optional[Logger]) -> str:
        """
        Generate a Midjourney prompt for the given category and daily factors
        """
        pass
    @abstractmethod
    def generate_from_description(self, description: str,
                                  logger: Optional[Logger] = None) -> str:
        """
        Generate a prompt from a description using OpenAI's API
        """
        pass