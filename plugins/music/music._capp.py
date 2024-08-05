"""
title: Music
author: Wes Caldwell
author_url: https://github.com/musicheardworldwide/Cerebro-OpenWebUI-Package-Manager/edit/main/plugins
funding_url: https://github.com/open-webui
version: 0.1.0
"""

import asyncio
from asyncio import sleep
from pydantic import BaseModel, Field
from typing import Optional, Union, Generator, Iterator
from apps.webui.models.files import Files
from config import UPLOAD_DIR
import requests
import hashlib
import time

class Tools:
    """
    Launches the artist dashboard applet
    """

    class Valves(BaseModel):
        priority: int = Field(
            default=0, description="Priority level for the filter operations."
        )

    def __init__(self):
        self.valves = self.Valves()
        self.package_name = "music"
        self.applet_file_id = None

    async def run(
        self,
        body: Optional[dict] = None,
        __user__: Optional[dict] = None,
        __event_emitter__: Optional[callable] = None,
        __event_call__: Optional[callable] = None,
    ) -> str:
        """
        Launches the artist dashboard applet
        :param body: The request body.
        :param __user__: User information, including the user ID.
        :param __event_emitter__: Function to emit events during the process.
        :param __event_call__: Function to call for the final output.
        :return: The final message or an empty string.
        """
        if not __user__ or "id" not in __user__:
            return "Error: User ID not provided"
        if not __event_emitter__ or not __event_call__:
            return "Error: Event emitter or event call not provided"

        user_id = __user__["id"]

        try:
            expected_filename = f"{UPLOAD_DIR}/cerebro/plugins/{self.package_name}/{self.package_name}_capp.html"
            all_files = Files.get_files()
            matching_file = next(
                (
                    file
                    for file in all_files
                    if file.user_id == user_id and file.filename == expected_filename
                ),
                None,
            )

            if not matching_file:
                error_message = f"Error: Applet file for {self.package_name} not found. Make sure the package is installed."
                await __event_emitter__(
                    {"type": "replace", "data": {"content": error_message}}
                )
                await __event_call__(error_message)
                return error_message

            self.applet_file_id = matching_file.id

            # Simulate a loading process
            loading_messages = [
                "Applet file found... launching",
            ]
            for message in loading_messages:
                await __event_emitter__(
                    {"type": "replace", "data": {"content": message}}
                )
                await asyncio.sleep(1)

            # Finally, replace with the actual applet embed
            final_message = f"{{{{HTML_FILE_ID_{self.applet_file_id}}}}}"
            await __event_emitter__(
                {"type": "replace", "data": {"content": final_message}}
            )

            # Simulate a short delay to ensure the message is displayed
            await sleep(0.5)

            return ""

        except Exception as e:
            error_message = f"An error occurred while launching the applet: {str(e)}"
            await __event_emitter__(
                {"type": "replace", "data": {"content": error_message}}
            )
            await __event_call__(error_message)
            return error_message

    async def handle_login(self, username: str, password: str, __event_emitter__: callable):
        """
        Handles user login
        :param username: User's username.
        :param password: User's password.
        :param __event_emitter__: Function to emit events during the process.
        :return: Token if login is successful, otherwise None.
        """
        try:
            timestamp = str(int(time.time()))
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            passphrase = hashlib.sha256((timestamp + password_hash).encode()).hexdigest()

            response = requests.get(
                f"{ampache_url}/server/json.server.php",
                headers={'User-Agent': 'Ampache Handshake'},
                params={
                    'action': 'handshake',
                    'auth': passphrase,
                    'timestamp': timestamp,
                    'user': username,
                    'version': '6.5.0'
                },
                verify=True
            )
            response.raise_for_status()

            if response.status_code == 200:
                response_json = response.json()
                token = response_json.get('auth')
                if token:
                    await __event_emitter__({"type": "replace", "data": {"content": "Login successful!"}})
                    return token
                else:
                    await __event_emitter__({"type": "replace", "data": {"content": "Token not found in response."}})
                    return None
            else:
                await __event_emitter__({"type": "replace", "data": {"content": "Handshake failed."}})
                return None

        except Exception as e:
            await __event_emitter__({"type": "replace", "data": {"content": f"Login error: {str(e)}"}})
            return None

    async def handle_upload(self, token: str, file_path: str, __event_emitter__: callable):
        """
        Handles file upload
        :param token: Authentication token.
        :param file_path: Path to the file to be uploaded.
        :param __event_emitter__: Function to emit events during the process.
        :return: Response message from the server.
        """
        try:
            with open(file_path, 'rb') as file:
                files = {'file': file}
                response = requests.post(
                    f"{ampache_url}/server/json.server.php",
                    params={'action': 'upload', 'auth': token},
                    files=files,
                    verify=True
                )
                response.raise_for_status()

                response_json = response.json()
                await __event_emitter__({"type": "replace", "data": {"content": response_json.get('message', 'Upload successful!')}})
                return response_json

        except Exception as e:
            await __event_emitter__({"type": "replace", "data": {"content": f"Upload error: {str(e)}"}})
            return None

    async def handle_profile_update(self, token: str, profile_data: dict, __event_emitter__: callable):
        """
        Handles profile update
        :param token: Authentication token.
        :param profile_data: Dictionary containing profile data.
        :param __event_emitter__: Function to emit events during the process.
        :return: Response message from the server.
        """
        try:
            response = requests.post(
                f"{ampache_url}/server/json.server.php",
                params={'action': 'update_user', 'auth': token},
                data=profile_data,
                verify=True
            )
            response.raise_for_status()

            response_json = response.json()
            await __event_emitter__({"type": "replace", "data": {"content": response_json.get('message', 'Profile update successful!')}})
            return response_json

        except Exception as e:
            await __event_emitter__({"type": "replace", "data": {"content": f"Profile update error: {str(e)}"}})
            return None
