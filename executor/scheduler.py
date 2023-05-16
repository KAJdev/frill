from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import runner


class Scheduler:
    """
    Provides a way to schedule tasks to be executed at some point in the future using cron expressions.
    """

    def __init__(self, pubsub, redis) -> None:
        self.aio_scheduler = AsyncIOScheduler()
        self.aio_scheduler.start()

        self.pubsub = pubsub
        self.redis = redis

    def add(self, graph: dict) -> None:
        """
        Schedules a task to be executed at some point in the future using cron expressions.
        """

        async def task(graph: dict):
            new_runner = runner.Runner(
                graph, self.pubsub, self.redis, graph.get("user", None)
            )
            await new_runner.run()

        self.aio_scheduler.add_job(
            task,
            trigger=CronTrigger.from_crontab(
                " ".join(graph.get("manifest", {}).get("cron").split(" ")[:5])
            ),
            args=[graph],
            id=graph.get("id", None),
        )

    def remove(self, graph_id: str) -> None:
        """
        Removes a task from the scheduler.
        """

        self.aio_scheduler.remove_job(graph_id)
