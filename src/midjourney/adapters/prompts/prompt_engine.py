# Standard Library Imports
import logging
import json
from typing import Dict, Optional

# Third-Party Imports
import openai

# Internal Project Imports
from midjourney.utils.logger.logger import Logger
from midjourney.domain.i_prompt_engine import PromptEngine


class OpenAIPromptEngine(PromptEngine):
    def __init__(self, api_key: str,
                 logger: Optional[Logger] = None) -> None:
        if not logger:
            def_logger = logging.getLogger("def_logger")
        else:
            def_logger = logger
        if api_key:
            try:
                self.client = openai.OpenAI(api_key=api_key)
                def_logger.info("Successfully")
            except Exception as e:
                print(f"[PromptEngine Init Error]: {e}")
                self.client = None
        else:
            self.client = None
            print("[PromptEngine Init Error]: Missing API key")

    def generate_prompt(self, category: str, daily_factors: Dict,
                        logger: Optional[Logger] = None) -> str:
        def_logger = logger or logging.getLogger("default_prompt_logger")

        if not self.client:
            def_logger.error("OpenAI client is not initialized.")
            return "Prompt generation failed: OpenAI client unavailable."

        system_prompt = (
            "You are a mystical prompt engineer specializing in creating MidJourney prompts"
            " for lucky wallpapers. Create visually stunning, magical,"
            " and auspicious prompts that incorporate daily cosmic influences,"
            " numerology, and spiritual elements."
        )

        user_prompt = f"""Create a Midjourney prompt for a {category} lucky wallpaper with these
        daily influences:
            - Date: {daily_factors["date"]}
            - Day: {daily_factors["dayOfWeek"]}
            - Lunar Phase: {daily_factors["lunarPhase"]}
            - Time of Day: {daily_factors["timeOfDay"]}
            - Season: {daily_factors["season"]}
            - Numerology Number: {daily_factors["numerology"]}
            - Element: {daily_factors["element"]}
            - Planetary Influence: {daily_factors["planetaryInfluence"]}
            - Lucky Colors: {", ".join(daily_factors["luckyColors"])}
            - Lucky Numbers: {", ".join(map(str, daily_factors["luckyNumbers"]))}
            Requirements:
                1. Include visual elements related to {category}
                2. Use mystical and magical imagery
                3. End with "--ar 9:16"
                4. Under 350 characters
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.95,
                max_tokens=150
            )

            # Pretty-print full response for dev
            #try:
            #    pretty_response = json.dumps(response.model_dump(), indent=2)
            #except Exception:
            #    pretty_response = str(response)
            #def_logger.info(f"[Prompt Raw Response]:\n{pretty_response}")

            content = getattr(response.choices[0].message, "content", None)
            if content:
                return content.strip()
            else:
                def_logger.warning("Response received but no message content found.")
                return "Prompt generation failed: No content in response."

        except Exception as e:
            def_logger.error(f"[PromptEngine Error]: {e}")
            raise RuntimeError(f"Prompt generation failed: {str(e)}")
    
    def generate_from_description(self, description: str,
                                  logger: Optional[Logger] = None) -> str:
        def_logger = logger or logging.getLogger("default_prompt_logger")

        if not self.client:
            def_logger.error("OpenAI client is not initialized.")
            return "Prompt generation failed: OpenAI client unavailable."

        system_prompt = (
            "You are a mystical prompt engineer who crafts MidJourney prompts for lucky and "
            "aesthetic wallpapers. Your job is to turn simple descriptions into powerful, "
            "beautiful, and surreal MidJourney prompts under 300 characters."
        )

        user_prompt = f"""Convert the following user description into a MidJourney prompt:
        
        Description: "{description}"

        Requirements:
        - Add mystical, beautiful, and artistic flair
        - Must remain under 300 characters
        - End with "--ar 9:16"
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.9,
                max_tokens=120
            )

            content = getattr(response.choices[0].message, "content", None)
            if content:
                def_logger.info(f"Generated prompt from description: {content.strip()}")
                return content.strip()
            else:
                def_logger.warning("Response received but no message content found.")
                return "Prompt generation failed: No content in response."

        except Exception as e:
            def_logger.error(f"[PromptEngine Error - Desc]: {e}")
            raise RuntimeError(f"Prompt generation from description failed: {str(e)}")