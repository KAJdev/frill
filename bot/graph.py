from typing import Optional
import openai
import toml


async def parse(prompt: str, user: str = None) -> Optional[dict]:
    msg = await openai.text(prompt, "graph", user, temperature=0.2)
    if not msg:
        print("Failed to create graph.")
        return None

    try:
        return toml.loads(msg.get("content", ""))
    except Exception as e:
        print(f"Failed to parse graph: {e}")
        return None
