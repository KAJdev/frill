import asyncio
import re, async_timeout
from . import actions

ACTIONS = {
    "conditional": actions.Conditional,
    "http": actions.Http,
    "assign": actions.Assign,
    "wait": actions.Wait,
    "google": actions.Google,
    "prompt": actions.Prompt,
    "gpt": actions.Gpt,
}


class Runner:
    """
    Responsible for executing graphs
    """

    def __init__(self, graph: dict, pubsub, redis, user: str) -> None:
        self.manifest = graph.get("manifest", {})
        self.actions = graph.get("actions", [])
        self.env = graph.get("env", {})
        self.current_action = 0
        self.pubsub = redis.pubsub()
        self.redis = redis
        self.user = user
        self.graph = graph

    async def run(self) -> None:
        """
        Run the full graph
        """
        print(f"Running graph {self.graph.get('id')}")

        # populate the environment with redis values
        e = (
            await self.redis.hgetall(f"graph_env:{self.user}:{self.graph.get('id')}")
        ) or {}

        for key, value in e.items():
            self.env[key.decode()] = value.decode()

        while self.current_action < len(self.actions):
            print(f"Running action {self.current_action}")
            await self.run_action(self.actions[self.current_action])
            self.current_action += 1

    async def run_action(self, action: dict) -> None:
        obj = ACTIONS.get(action.get("type", "").lower(), actions.action.Action)

        if obj is None:
            return

        obj = obj(action)
        await obj.run(self)

    def get_action(self, label: str) -> int:
        """
        Get the action index from the label
        """
        for index, action in enumerate(self.actions):
            if action.get("label", "") == label:
                return index

        return -1

    def queue_action(self, label: str) -> None:
        """
        Queue an action to run next
        """
        a = self.get_action(self.template_string(label))
        if a == -1:
            return

        self.current_action = a

    def template_string(self, string: str) -> str:
        """
        Template a string with the graph environment, replace all ${key} with the value of self.env["key"]

        if a key is not found, it will be replaced with None
        """
        print(f"Template string: {string}")
        try:
            for key, value in self.env.items():
                string = string.replace(f"${{{key}}}", value)
        except:
            pass

        return string

    async def assign(self, key: str, value: str) -> None:
        """
        Assign a value to the graph environment
        """
        self.env[self.template_string(str(key))] = self.template_string(str(value))
        await self.redis.hset(
            f"graph_env:{self.user}:{self.graph.get('id')}",
            self.template_string(str(key)),
            self.template_string(str(value)),
        )

    async def send_discord_message(self, content: str) -> None:
        """
        Send a message to a discord channel
        """
        x = await self.redis.publish("discord:send", f"{self.user}:{content}")
        print(f"Published message to {x} listeners.")

    async def wait_for_discord_message(self) -> str:
        """
        Wait for a message in a discord channel
        """
        await self.pubsub.subscribe(f"discord:{self.user}")

        while True:
            try:
                async with async_timeout.timeout(1):
                    message = await self.pubsub.get_message(
                        ignore_subscribe_messages=True
                    )
                    if message is not None:
                        print(f"(Reader) Message Received: {message}")

                        # unsub
                        await self.pubsub.unsubscribe()

                        return message["data"].decode()
                    await asyncio.sleep(0.01)
            except asyncio.TimeoutError:
                pass
