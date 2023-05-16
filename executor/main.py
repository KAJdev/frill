import asyncio
from os import getenv
from uuid import uuid4
import runner
from sanic import Sanic
from sanic.response import json
from redis import asyncio as aioredis
from motor.motor_asyncio import AsyncIOMotorClient
import scheduler

app = Sanic("executor")


@app.before_server_start
async def setup_db(app, loop):
    app.config.redis = await aioredis.from_url(
        f"redis://{getenv('REDIS_HOST')}:{getenv('REDIS_PORT')}"
    )
    app.config.db = AsyncIOMotorClient(
        f"mongodb://{getenv('MONGODB_HOST')}:{getenv('MONGODB_PORT')}",
        io_loop=loop,
    )[getenv("DATABASE_NAME")]

    app.config.scheduler = scheduler.Scheduler(
        app.config.redis.pubsub(), app.config.redis
    )
    active = await app.config.db.graphs.find(
        {"manifest.cron": {"$exists": True}}
    ).to_list(None)

    for graph in active:
        print(f"Adding graph to scheduler: {graph}")
        app.config.scheduler.add(graph)


@app.after_server_stop
async def close_db(app, loop):
    app.config.redis.close()
    await app.config.redis.wait_closed()


@app.route("/<user>/graphs", methods=["GET"])
async def get_graphs(request, user):
    # get rid of _id
    graphs = await app.config.db.graphs.find({"user": user}, {"_id": 0}).to_list(None)
    return json(graphs)


@app.route("/<user>/graphs", methods=["POST"])
async def create_graph(request, user):
    graph = request.json
    graph["user"] = user
    graph["id"] = str(uuid4())
    if not graph.get("manifest"):
        graph["manifest"] = {}

    if not graph.get("actions"):
        return json({"success": False, "error": "No actions provided."})

    if not graph.get("env"):
        graph["env"] = {}

    print(f"Creating graph: {graph}")

    if graph.get("manifest").get("cron") is not None:
        await app.config.db.graphs.insert_one(graph)
        app.config.scheduler.add(graph)
        print("Added graph to scheduler.")

    else:
        new_runner = runner.Runner(
            graph, app.config.redis.pubsub(), app.config.redis, graph.get("user", None)
        )
        asyncio.create_task(new_runner.run())
        print("Started one-time graph.")

    return json({"success": True})


@app.route("/<user>/graphs/<id>", methods=["DELETE"])
async def delete_graph(request, user, id):
    await app.config.db.graphs.delete_one({"user": user, "id": id})

    app.config.scheduler.remove(id)

    return json({"success": True})


@app.route("/<user>/graphs/<id>", methods=["GET"])
async def get_graph(request, user, id):
    return json(await app.config.db.graphs.find_one({"user": user, "id": id}))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(getenv("EXECUTOR_PORT", 8000)))
