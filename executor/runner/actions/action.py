class Action:
    """
    An abstract class that represents an action that can be performed by a runner.
    """

    def __init__(self, action: dict) -> None:
        self.type = action.get("type", "")
        self.label = action.get("label", "")
        self.goto = action.get("goto", "")

    async def run(self, runner) -> None:
        if self.goto:
            runner.queue_action(self.goto)
