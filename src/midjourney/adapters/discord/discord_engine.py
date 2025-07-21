import os
import uuid
import time
import requests
import logging
from typing import Optional
from urllib.parse import urlparse


class DiscordEngine:
    def __init__(
        self,
        discord_token: str,
        application_id: str,
        guild_id: str,
        channel_id: str,
        version: str,
        command_id: str,
        session_id: Optional[str] = "Cannot be empty",
        logger: Optional[logging.Logger] = None,
    ):
        self.token = discord_token
        self.application_id = application_id
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.version = version
        self.command_id = command_id
        self.session_id = session_id
        self.logger = logger or logging.getLogger("discord_engine")
        self.base_url = "https://discord.com/api/v9"
        self.headers = {
            "Authorization": self.token,
            "Content-Type": "application/json",
        }
        self.image_path_str = ""

    def generate_image(self, prompt: str) -> Optional[str]:
        self.logger.info("🔧 [INIT] Sending prompt to Midjourney...")
        self._send_prompt(prompt)

        self.logger.info("📩 [FETCH] Waiting for grid image...")
        message_id, custom_id = self._wait_for_grid_and_get_button()
        if not message_id or not custom_id:
            self.logger.error(
                    "❌ [ERROR] Failed to receive grid or upscale buttons."
                    )
            return None

        self.logger.info(
                f"✅ [BUTTON] Triggering upscale with custom_id: {custom_id}"
            )
        self._send_component_interaction(custom_id, message_id)

        self.logger.info("🖼️ [WAIT] Waiting for upscaled image...")
        final_image_url = self._wait_for_upscale_image()
        if not final_image_url:
            self.logger.error("❌ [ERROR] Failed to receive upscaled image.")
            return None

        self.logger.info(f"📥[DOWNLOAD] Saving img from URL: {final_image_url}")
        self._download_image(final_image_url)
        return self.image_path_str

    def _send_prompt(self, prompt: str):
        self.logger.info(f"📤 [SEND] Sending prompt: `{prompt}`")
        prompt = prompt.strip().strip('""').rstrip('.')
        #url = self.base_url + "/interaction"
        url = f"{self.base_url}/interactions"
        payload = {
                "type": 2,
                "application_id": self.application_id,
                "guild_id": self.guild_id,
                "channel_id": self.channel_id,
                "session_id": self.session_id,
                "data": {
                    "version": self.version,
                    "id": self.command_id,
                    "name": "imagine",
                    "type": 1,
                    "options": [{"type": 3, "name": "prompt", "value": prompt}],
                    "application_command": {
                        "id": self.command_id,
                        "application_id": self.application_id,
                        "version": self.version,
                        "default_member_permissions": None,
                        "type": 1,
                        "nsfw": False,
                        "name": "imagine",
                        "description": "Create images with Midjourney",
                        "dm_permission": True,
                        "contexts": None,
                        "options": [
                            {
                                "type": 3,
                                "name": "prompt",
                                "description": "The prompt to imagine",
                                "required": True,
                                }
                            ],
                        },
                    "attachments": [],
                    },
                }
        response = requests.post(url, headers=self.headers, json=payload)
        if response.status_code != 204:
            raise Exception(f"Failed to send prompt: {response.status_code} - {response.text}")
        self.logger.info("📤 [SENT] Prompt successfully sent.")

    def _wait_for_grid_and_get_button(self) -> tuple[Optional[str], Optional[str]]:
        for attempt in range(6):
            time.sleep(30)
            self.logger.info(f"⏳ [WAIT] Attempt {attempt + 1}/6: Looking for grid...")
            try:
                messages = self._get_messages()
                for msg in messages:
                    message_id = msg.get("id")
                    components_outer = msg.get("components", [])
                    if not components_outer:
                        continue
                    components = components_outer[0].get("components", [])
                    buttons = [c for c in components if c.get("label") in ["U1", "U2", "U3", "U4"]]
                    if buttons:
                        custom_id = buttons[0]["custom_id"]
                        self.logger.info(f"🔘 [FOUND] Button {buttons[0]['label']} - {custom_id}")
                        return message_id, custom_id
            except Exception as e:
                self.logger.error(f"❌ [ERROR] Failed to parse grid message: {e}")
        return None, None

    def _send_component_interaction(self, custom_id: str, message_id: str):
        url = f"{self.base_url}/interactions"
        payload = {
            "type": 3,
            "guild_id": self.guild_id,
            "channel_id": self.channel_id,
            "message_id": message_id,
            "application_id": self.application_id,
            "session_id": self.session_id,
            "message_flags": 0,
            "data": {
                "component_type": 2,
                "custom_id": custom_id,
            },
        }

        response = requests.post(url, headers=self.headers, json=payload)
        if response.status_code != 204:
            raise Exception(f"Button click failed: {response.status_code} - {response.text}")
        self.logger.info(f"📩 [CLICKED] Sent component interaction.")

    def _wait_for_upscale_image(self) -> Optional[str]:
        for attempt in range(6):
            time.sleep(30)
            self.logger.info(f"📥 [FETCH] Attempt {attempt + 1}/6: Checking for final image...")
            try:
                messages = self._get_messages()
                for msg in messages:
                    attachments = msg.get("attachments", [])
                    if len(attachments) == 1:
                        return attachments[0].get("url")
            except Exception as e:
                self.logger.error(f"❌ [ERROR] Failed to fetch upscaled image: {e}")
        return None

    def _get_messages(self):
        url = f"{self.base_url}/channels/{self.channel_id}/messages?limit=50"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def _download_image(self, image_url: str):
        response = requests.get(image_url)
        if response.status_code == 200:
            parsed = urlparse(image_url)
            filename = os.path.basename(parsed.path) + str(uuid.uuid4()) + ".png"
            os.makedirs("images", exist_ok=True)
            self.image_path_str = os.path.join("images", filename)
            with open(self.image_path_str, "wb") as f:
                f.write(response.content)
            self.logger.info(f"✅ [DOWNLOADED] Image saved to {self.image_path_str}")
        else:
            self.logger.error(f"❌ [ERROR] Failed to download image: {response.status_code}")
