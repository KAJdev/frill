from typing import Optional
import openai


MEMORY = {}


class LimitedList(list):
    def __init__(self, limit):
        self.limit = limit
        super().__init__()

    def append(self, item):
        super().insert(0, item)
        if len(self) > self.limit:
            super().pop()


def parse_msg(msg: str) -> tuple[str, list[dict]]:
    actions = []

    # there can be actions in the form of [[ACTION: ...]] in the message. we need to parse them out.
    while "[[" in msg:
        start = msg.find("[[")
        end = msg.find("]]")

        if -1 not in (start, end):
            action_type, action = msg[start + 2 : end].split(": ")
            actions.append({"type": action_type, "content": action})
            msg = msg[:start] + msg[end + 2 :]

    return msg, actions


async def talk(prompt: str, user: str = None, jobs: list[dict] = []) -> Optional[str]:
    history = MEMORY.get(user, LimitedList(10))

    jobs_str = (
        "\n\n".join(
            f"{i}. {job.get('manifest', {}).get('name')} ({job.get('manifest', {}).get('cron')})\n{job.get('manifest', {}).get('description')}"
            for i, job in enumerate(jobs)
        )
        or "No jobs."
    )

    msg = await openai.text(
        prompt, "frill", user, {"jobs": jobs_str}, history, temperature=1
    )
    if not msg:
        print("Failed to generate frill message.")
        return None

    history.append(
        {
            "role": "user",
            "content": prompt,
        }
    )
    history.append(msg)
    MEMORY[user] = history

    return parse_msg(msg.get("content", ""))
