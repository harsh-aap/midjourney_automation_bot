import json
import os
import threading
from datetime import datetime
from queue import Queue, Empty
from time import sleep
from typing import Optional
from midjourney.config.container import Container
from midjourney.utils.logger.logger import Logger
from midjourney.adapters.discord.discord_engine import DiscordEngine


class ImageGenerator:
    DEFAULT_CATEGORIES = [
        "career",
        "business",
        "relationship",
        "wealth",
        "family",
        "health",
        "education",
        "wellbeing",
        "spiritual",
        "happiness",
        "luck",
    ]

    def __init__(self):
        try:
            Container.init()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Container: {e}")

        if Container.logger is None:
            raise RuntimeError(
                "Logger not initialized. Please ensure Container.init() was called"
            )

        config = Container.config
        # creating config here
        discord_token = config['DISCORD_AUTH_TOKEN']
        application_id = config['DISCORD_APPLICATION_ID']
        guild_id = config['DISCORD_GUILD_ID']
        version = config['DISCORD_VERSION']
        command_id = config['DISCORD_ID']
        channel_id_1 = config['DISCORD_CHANNEL_ID_1']
        channel_id_2 = config['DISCORD_CHANNEL_ID_2']

        self.logger: Logger = Container.logger
        self.logger.info("🚀 Midjourney bot started successfully.")
        self.discord_engine_1 = DiscordEngine(
            discord_token=discord_token,
            application_id=application_id,
            guild_id=guild_id,
            channel_id=channel_id_1,
            version=version,
            command_id=command_id,
            logger=self.logger,
        )

        self.discord_engine_2 = DiscordEngine(
            discord_token=discord_token,
            application_id=application_id,
            guild_id=guild_id,
            channel_id=channel_id_2,
            version=version,
            command_id=command_id,
            logger=self.logger,
        )

        self.engines = {
            "engine1": (self.discord_engine_1, threading.Lock()),
            "engine2": (self.discord_engine_2, threading.Lock()),
        }

        self.message_queue: Queue[str] = Queue()
        self._shutdown_event = threading.Event()
        self.worker_threads: list[threading.Thread] = []

        # Start multiple worker threads
        self._start_worker_threads(num_threads=2)

    def _start_worker_threads(self, num_threads: int):
        for i in range(num_threads):
            t = threading.Thread(target=self._process_queue_loop, daemon=True)
            t.start()
            self.worker_threads.append(t)
            self.logger.info(f"🧵 Worker thread-{i + 1} started.")

    def log_result(self, result):
        log_file_path = "../storage/results.log"
        log_dir = os.path.dirname(log_file_path)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        with open(log_file_path, "a") as f:
            json.dump(result, f)
            f.write("\n")

    def _get_available_engine(self) -> Optional[tuple[str, DiscordEngine]]:
        for name, (engine, lock) in self.engines.items():
            if lock.acquire(blocking=False):
                return name, engine
        return None

    def _release_engine(self, engine_name: str):
        self.engines[engine_name][1].release()

    def _process_queue_loop(self):
        while not self._shutdown_event.is_set():
            try:
                message = self.message_queue.get(timeout=1)
                prompt = message["prompt"]
                category = message["category"]
                date_based = message["date_based"]
                user_prompt = message["user_prompt"]
                description = message["description"]
            except Empty:
                continue

            engine_name = None
            try:
                while not self._shutdown_event.is_set():
                    engine_info = self._get_available_engine()
                    if engine_info:
                        engine_name, engine = engine_info
                        break
                    else:
                        sleep(0.5)

                if not engine_name:
                    self.logger.error("❌ No engine available for prompt.")
                    continue

                result_img_url = engine.generate_image(prompt)
                self.logger.info(f"✅ Prompt sent via {engine_name}")

                # Log the result
                log_entry = {
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "prompt": prompt,
                    "result_img_url": result_img_url,
                    "category": category,
                    "details": {
                        "date_based": date_based,
                        "user_prompt": user_prompt,
                        "description": description,
                    },
                }
                self.log_result(log_entry)

            except Exception as e:
                self.logger.error(f"❌ Error processing prompt: {e}")

            finally:
                if engine_name:
                    self._release_engine(engine_name)
                    self.logger.info(f"🔓 Released lock for {engine_name}")
                self.message_queue.task_done()

    def shutdown(self):
        self.logger.info("🛑 Shutting down worker threads...")
        self._shutdown_event.set()
        for t in self.worker_threads:
            t.join()
        self.message_queue.join()
        self.logger.info("✅ All worker threads stopped.")

    def create_daily_factors(self, date: Optional[str] = None) -> dict:
        factors = Container.daily_factors.get_factors(date)
        self.logger.info(f"🌞 Daily Factors for {date or 'today'}: {factors}")
        return factors

    def generate_prompt(self, category: str, factors: dict) -> str:
        if not Container.promptEngine:
            raise RuntimeError("Prompt Engine not initialized")
        prompt = Container.promptEngine.generate_prompt(category, factors, self.logger)
        return prompt

    def message_push(
        self,
        date: Optional[str] = None,
        category: Optional[str] = None,
        user_prompt: Optional[str] = None,
        description: Optional[str] = None,
    ):
        self.logger.info("📥 Message push initiated.")
        if user_prompt:
            self.logger.info("🧠 User-provided prompt detected.")
            message = {
                "prompt": user_prompt,
                "category": None,
                "date_based": False,
                "user_prompt": True,
                "description": None,
            }
        elif description:
            self.logger.info("💡 Using OpenAI to generate prompt from description.")
            prompt = Container.promptEngine.generate_from_description(
                description, self.logger
            )
            if not prompt:
                self.logger.error("❌ Failed to generate prompt from description.")
                return
            self.logger.info(f"➡ Generated Prompt: {prompt}")
            message = {
                "prompt": prompt,
                "category": None,
                "date_based": False,
                "user_prompt": False,
                "description": description,
            }
        elif category:
            self.logger.info(f"🔍 Generating for category: {category}")
            prompt = self.generate_prompt(category, self.create_daily_factors(date))
            message = {
                "prompt": prompt,
                "category": category,
                "date_based": True,
                "user_prompt": False,
                "description": None,
            }
        else:
            self.logger.info(
                "📅 No category or prompt given, generating for all default categories."
            )

            for cat in self.DEFAULT_CATEGORIES:
                self.logger.info(
                    f"\n====================== Generating prompt for category: {cat} ======================\n"
                )
                prompt = self.generate_prompt(cat, self.create_daily_factors(date))
                message = {
                    "prompt": prompt,
                    "category": cat,
                    "date_based": True,
                    "user_prompt": False,
                    "description": None,
                }
                self.message_queue.put(message)
            return

        self.message_queue.put(message)

    def generate_images(self):
        self.logger.info(
            "⚠️ `generate_images()` is handled by background worker threads now."
        )
