# standard library imports
import os
from dotenv import load_dotenv


def load_config():
    load_dotenv()

    return {
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
            "DISCORD_APPLICATION_ID": os.getenv("DISCORD_APPLICATION_ID"),
            "DISCORD_GUILD_ID": os.getenv("DISCORD_GUILD_ID"),
            "DISCORD_CHANNEL_ID_1": os.getenv("DISCORD_CHANNEL_ID_1"),
            "DISCORD_CHANNEL_ID_2": os.getenv("DISCORD_CHANNEL_ID_2"),
            "DISCORD_VERSION": os.getenv("DISCORD_VERSION"),
            "DISCORD_ID": os.getenv("DISCORD_ID"),
            "DISCORD_AUTH_TOKEN": os.getenv("DISCORD_AUTH_TOKEN"),
            "LEVEL": os.getenv("LOG_LEVEL", "INFO"),
            "BASE_OUTPUT_FOLDER": os.getenv("BASE_OUTPUT_FOLDER")
    }
