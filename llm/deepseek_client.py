import time
from openai import OpenAI
from typing import List, Dict

from commom.env_tools import get_env_var


class DeepSeekClient:
    __slots__ = (
        "client",
        "config"
    )

    def __init__(self):
        self.client = OpenAI(
            api_key=get_env_var("DEEPSEEK_API_KEY"),
            base_url=get_env_var("DEEPSEEK_BASE_URL")
        )
        self.config = {
            "temperature": 1,
            "stream": False,
        }

    def normal_chat(self, messages: List[Dict[str, str]]) -> str:

        max_retries = 20
        retry_count = 0

        while retry_count < max_retries:
            try:
                response = self.client.chat.completions.create(
                    model="deepseek-chat",
                    messages=messages,
                    temperature=self.config["temperature"],
                    stream=self.config["stream"]
                )

                response_content = response.choices[0].message.content
                return response_content

            except Exception as e:
                retry_count += 1
                print(f"Request failed: {e}. Retrying {retry_count}/{max_retries} in 15 seconds...")
                time.sleep(15)

        raise Exception("Maximum retry limit reached. Unable to complete the request.")

