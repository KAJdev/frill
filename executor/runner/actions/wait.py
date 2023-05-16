from . import Action
import asyncio


class Wait(Action):
    def __init__(self, action: dict) -> None:
        super().__init__(action)
        self.minutes = action.get("minutes", 0)

    async def run(self, runner):
        await super().run(runner)
        try:
            await asyncio.sleep(int(runner.template_string(self.minutes)) * 60)
        except (ValueError, TypeError):
            pass
