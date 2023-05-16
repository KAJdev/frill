from . import Action
import aiohttp


class Http(Action):
    def __init__(self, action: dict) -> None:
        super().__init__(action)
        self.url = action.get("url", "")
        self.method = action.get("method", "GET")
        self.headers = action.get("headers", {})
        self.body = action.get("body", b"")
        self.timeout = action.get("timeout", 30)
        self.output = action.get("output", "")

    async def run(self, runner):
        await super().run(runner)

        # template all the headers
        headers = {}
        for k, v in self.headers.items():
            headers[runner.template_string(k)] = runner.template_string(v)

        # template the body
        body = runner.template_string(self.body)

        # template the url
        url = runner.template_string(self.url)

        # make the request
        async with aiohttp.ClientSession(
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=self.timeout),
        ) as session:
            async with session.request(
                method=self.method,
                url=url,
                data=body,
            ) as response:
                if self.output:
                    await runner.assign(self.output, str(await response.text()))
                else:
                    print(await response.text())
