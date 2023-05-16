from . import Action


class Assign(Action):
    def __init__(self, action: dict) -> None:
        super().__init__(action)
        self.value = action.get("value", "")
        self.output = action.get("output", "")

    async def run(self, runner):
        await super().run(runner)
        await runner.assign(self.output, self.value)
