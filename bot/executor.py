import aiohttp
from os import getenv


async def get_graphs(user: str) -> list[dict]:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"http://{getenv('EXECUTOR_HOST')}:{getenv('EXECUTOR_PORT')}/{user}/graphs"
        ) as resp:
            return await resp.json()


async def get_graph(user: str, id: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"http://{getenv('EXECUTOR_HOST')}:{getenv('EXECUTOR_PORT')}/{user}/graphs/{id}"
        ) as resp:
            return await resp.json()


async def create_graph(user: str, graph: dict) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"http://{getenv('EXECUTOR_HOST')}:{getenv('EXECUTOR_PORT')}/{user}/graphs",
            json=graph,
        ) as resp:
            return await resp.json()


async def delete_graph(user: str, id: str) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.delete(
            f"http://{getenv('EXECUTOR_HOST')}:{getenv('EXECUTOR_PORT')}/{user}/graphs/{id}"
        ) as resp:
            return await resp.json()
