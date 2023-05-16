import asyncio
import toml
import interactions
import frill, executor, graph
from os import getenv
from redis import asyncio as aioredis
import async_timeout

from interactions.api.events import MessageCreate

print("Loading bot...")

bot = interactions.Client(
    intents=interactions.Intents.MESSAGES | interactions.Intents.DEFAULT
)


async def pubsub_listener(channel):
    while True:
        try:
            async with async_timeout.timeout(1):
                if channel is None:
                    return

                message = await channel.get_message(ignore_subscribe_messages=True)
                if message is not None:
                    print(f"(Reader) Message Received: {message}")

                    user, content = message["data"].decode().split(":", 1)

                    # try to send the message to the user
                    try:
                        user = await bot.fetch_user(user)
                        await user.send(content)
                    except:
                        print("Failed to send message to user.")
                await asyncio.sleep(0.01)
        except asyncio.TimeoutError:
            pass


@interactions.listen()
async def on_startup():
    print("logged in as", bot.user)

    print("starting redis...")
    bot.redis = await aioredis.from_url(
        f"redis://{getenv('REDIS_HOST')}:{getenv('REDIS_PORT')}"
    )

    print("starting pubsub listener...")
    pubsub = bot.redis.pubsub()
    await pubsub.subscribe("discord:send")
    print("started pubsub listener on channel", pubsub)
    asyncio.create_task(pubsub_listener(pubsub))


@interactions.listen()
async def on_message_create(event: MessageCreate):
    message = event.message

    if not message.content or message.author.bot:
        return

    # publish message
    x = await bot.redis.publish(f"discord:{message.author.id}", f"{message.content}")
    if x > 0:
        print(f"Published message to {x} listeners.")

    if (
        f"<@!{bot.user.id}>" not in message.content
        and f"<@{bot.user.id}>" not in message.content
    ) and message.guild:
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
                to_delete = jobs[int(action["content"]) - 1]
                await executor.delete_graph(message.author.id, to_delete["id"])
                await message.reply(
                    content=f"Deleted graph `{action['content']}`.",
                )


print("Starting bot...")
bot.start(getenv("DISCORD_TOKEN"))
