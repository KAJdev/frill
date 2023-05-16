from os import getenv
from typing import Optional
import aiohttp

PROMPTS = {}


def get_system_prompt(name: str, vars: dict) -> str:
    global PROMPTS
    if name not in PROMPTS:
        with open(f"prompts/{name}.txt", "r") as f:
            PROMPTS[name] = f.read()
    p = PROMPTS[name]

    if vars:
        p = p.format_map(vars)

    return p


async def text(
    prompt: str,
    system_prompt: str,
    user: str = None,
    system_vars: dict = {},
    context: list[dict] = {},
    temperature: float = 0.25,
) -> Optional[dict]:
    try:
        async with aiohttp.ClientSession(
            headers={"Authorization": f'Bearer {getenv("OPENAI_TOKEN")}'}
        ) as session:
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                json={
                    "model": "gpt-4",
                    "messages": [
                        {
                            "role": "system",
                            "content": get_system_prompt(system_prompt, system_vars),
                        },
                        *context,
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": temperature,
                    "user": f"{user}" if user else None,
                    "max_tokens": 2048,
                },
            ) as response:
                json = await response.json()
                return json["choices"][0]["message"]
    except Exception as e:
        print(f"Failed to create completion: {e}")
        return None
