from os import getenv
from . import Action
import aiohttp


class Prompt(Action):
    def __init__(self, action: dict) -> None:
        super().__init__(action)
        self.content = action.get("content", "")
        self.image = action.get("image", "")
        self.gif = action.get("gif", "")
        self.output = action.get("output", "")

    async def run(self, runner):
        await super().run(runner)

        content = runner.template_string(self.content)

        if self.gif:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://tenor.googleapis.com/v2/search?q={self.gif}&key={getenv('TENOR_TOKEN')}&client_key=frill&limit=1"
                ) as resp:
                    json = await resp.json()
                    content += f"\n\n{json['results'][0]['url']}"

        await runner.send_discord_message(
            content=content,
        )

        if self.output:
            await runner.assign(self.output, await runner.wait_for_discord_message())
