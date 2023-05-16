from . import Action


class Conditional(Action):
    def __init__(self, action: dict) -> None:
        super().__init__(action)
        self.condition = action.get("condition", None)
        self.if_true = action.get("if_true", None)
        self.if_false = action.get("if_false", None)

    async def run(self, runner):
        """
        eval self.condition (string) as a python expression
        """
        await super().run(runner)

        try:
            if eval(runner.template_string(self.condition)):
                runner.queue_action(self.if_true)
            else:
                runner.queue_action(self.if_false)

        except Exception as e:
            print(e)
            return
