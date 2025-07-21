# standard library imports
import logging
from typing import Optional

# Internal Project Module Imports
from midjourney.config.load_config import load_config
from midjourney.utils.logger.logger import Logger
from midjourney.utils.logger.app_logger import AppLogger
from midjourney.domain.i_daily_factors import DailyFactors
from midjourney.adapters.factors.daily_factors import DefaultDailyFactors
from midjourney.domain.i_prompt_engine import PromptEngine
from midjourney.adapters.prompts.prompt_engine import OpenAIPromptEngine


class Container:
    """
    A dependency injection container for shared
    resources like configuration, logger, and daily factors.
    Attributes:
        config (Optional[dict]): Application config loaded from .env.
        logger (Optional[Logger]): Logging interface.
        daily_factors (Optional[DailyFactors]): Provides
            daily factors like lunar phase, numerology, etc.
    """
    config: Optional[dict] = None
    logger: Optional[Logger] = None
    daily_factors: Optional[DailyFactors] = None
    promptEngine: Optional[PromptEngine] = None

    @classmethod
    def init(cls) -> None:
        """
        Initialize the configuration, logger, and daily factor components.
        This method is idempotent —
        calling it multiple times won’t reinitialize components.
        """

        if (cls.logger is not None) and (
                cls.daily_factors is not None) and (
                cls.promptEngine is not None):
            return  # Already initialized

        # Load configuration
        cls.config = load_config()

        # Set logging level from config
        try:
            env_log_level = cls.config.get("LEVEL", "INFO").upper()
            if not hasattr(logging, env_log_level):
                raise ValueError(f"Invalid log level: {env_log_level}")
            log_level = getattr(logging, env_log_level)
        except Exception as e:
            print(f"⚠️  Using default log level INFO due to error: {e}")
            log_level = logging.INFO

        # Initialize logger
        cls.logger = AppLogger(name="midjour", level=log_level, log_file=True)

        # Initialize daily factors provider
        cls.daily_factors = DefaultDailyFactors()

        # Initializing the PromptEngine
        open_ai_key = cls.config.get("OPENAI_API_KEY")
        if not open_ai_key or not isinstance(open_ai_key, str):
            raise ValueError(
                    "OPENAI_API_KEY is missing or invalid in configuration"
            )

        cls.promptEngine = OpenAIPromptEngine(
                api_key=open_ai_key,
                logger=cls.logger
        )
