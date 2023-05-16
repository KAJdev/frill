from . import Action
import aiohttp


class Google(Action):
    def __init__(self, action: dict) -> None:
        super().__init__(action)
        self.query = action.get("query", "")
        self.output = action.get("output", "")

    async def run(self, runner):
        await super().run(runner)

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://www.google.com/search?q={runner.template_string(self.query)}"
            ) as response:
                html = await response.text()
                if self.output:
                    await runner.assign(self.output, str(html))
                else:
                    print(html)
