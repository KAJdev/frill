from os import getenv
from . import Action
import aiohttp


class Gpt(Action):
    def __init__(self, action: dict) -> None:
        super().__init__(action)
        self.prompt = action.get("prompt", "")
        self.output = action.get("output", "")

    async def run(self, runner):
        await super().run(runner)

        try:
            async with aiohttp.ClientSession(
                headers={"Authorization": f'Bearer {getenv("OPENAI_TOKEN")}'}
            ) as session:
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    json={
                        "model": "gpt-4",
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are an assistant to a computer system (user). Complete the task given by the user without providing extra details.",
                            },
                            {
                                "role": "user",
                                "content": runner.template_string(self.prompt),
                            },
                        ],
                    },
                ) as response:
                    json = await response.json()
                    content = json["choices"][0]["message"]["content"]

                    if self.output:
                        await runner.assign(self.output, content)
        except Exception as e:
            print(f"Failed to create completion: {e}")
            return None
