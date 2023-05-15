import asyncio
import toml
import interactions
import frill, executor, graph
from os import getenv
from redis import asyncio as aioredis

from interactions.api.events import MessageCreate

print("Loading bot...")

bot = interactions.Client(
    intents=interactions.Intents.MESSAGES | interactions.Intents.DEFAULT
)


@interactions.listen()
async def on_startup():
    print("logged in as", bot.user)

    print("starting redis...")
    bot.redis = await aioredis.from_url(
        f"redis://{getenv('REDIS_HOST')}:{getenv('REDIS_PORT')}"
    )


@interactions.listen()
async def on_message_create(event: MessageCreate):
    message = event.message
    if not message.content or (
        f"<@!{bot.user.id}>" not in message.content
        and f"<@{bot.user.id}>" not in message.content
    ):
        return

    # if the mention is at the start, remove it, otherwise, replace it with Frill
    if message.content.startswith(f"<@!{bot.user.id}>"):
        message.content = message.content[len(f"<@!{bot.user.id}>") :]
    elif message.content.startswith(f"<@{bot.user.id}>"):
        message.content = message.content[len(f"<@{bot.user.id}>") :]
    else:
        message.content = message.content.replace(f"<@!{bot.user.id}>", "Frill")
        message.content = message.content.replace(f"<@{bot.user.id}>", "Frill")

    await message.channel.trigger_typing()

    jobs = await executor.get_graphs(message.author.id)

    frill_msg = await frill.talk(message.content, message.author.id, jobs)

    if not frill_msg:
        return

    print(frill_msg)

    if frill_msg[0]:
        await message.reply(content=frill_msg[0])

    if frill_msg[1]:  # actions
        for action in frill_msg[1]:
            if action["type"].lower() == "create":
                new_graph = await graph.parse(action["content"], message.author.id)
                if new_graph:
                    await executor.create_graph(message.author.id, new_graph)
                    await message.reply(
                        content=f"Created graph.\n\n```toml\n{toml.dumps(new_graph)}```",
                    )

            elif action["type"].lower() == "delete":
                to_delete = jobs[int(action["content"])]
                await executor.delete_graph(message.author.id, to_delete["id"])
                await message.reply(
                    content=f"Deleted graph `{action['content']}`.",
                )


print("Starting bot...")
bot.start(getenv("DISCORD_TOKEN"))
