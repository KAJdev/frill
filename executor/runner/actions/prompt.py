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

        await runner.send_discord_message(
            content=runner.template_string(self.content),
        )

        if self.output:
            await runner.assign(self.output, await runner.wait_for_discord_message())
