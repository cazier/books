import asyncio
import os
import pathlib
import typing

import httpx
import pydantic


class Identity(pydantic.BaseModel):
    chip: pydantic.UUID4
    identity: str
    syncable: bool


class Libby:
    client: httpx.AsyncClient
    identity: Identity

    identity_path: pathlib.Path = pathlib.Path.cwd().joinpath(".libby.json")

    @classmethod
    async def get_identity(cls) -> Identity:
        if os.getenv("LIBBY_BEARER_TOKEN") and os.getenv("LIBBY_CHIP_UUID"):
            return Identity.model_validate(
                {"chip": os.environ["LIBBY_CHIP_UUID"], "identity": os.environ["LIBBY_BEARER_TOKEN"], "syncable": True}
            )

        if cls.identity_path.exists():
            return Identity.model_validate_json(cls.identity_path.read_text(encoding="utf8"))

        async with httpx.AsyncClient() as client:
            resp = await client.post("https://sentry.libbyapp.com/chip")
            resp = resp.raise_for_status()

        return Identity.model_validate_json(resp.text)

    async def set_identity(self) -> None:
        self.identity_path.write_text(self.identity.model_dump_json(), encoding="utf8")

    async def setup_sync_code(self, headers: dict[str, str]) -> str:
        async with httpx.AsyncClient(headers=headers) as client:
            resp = await client.get("https://sentry.libbyapp.com/chip/clone/code")
            resp = resp.raise_for_status()

            print(resp.json()["code"])

            return typing.cast(str, resp.json()["code"])

    def __init__(self) -> None:
        async def _init_() -> None:
            self.identity = await self.get_identity()

            breakpoint()
            if not self.identity.syncable:
                await self.setup_sync_code(headers={"Authorization": f"Bearer {self.identity.identity}"})

            await self.set_identity()

            self.client = httpx.AsyncClient(
                headers={"Authorization": f"Bearer {self.identity.identity}"}, base_url="https://vandal.libbyapp.com"
            )

        return asyncio.run(_init_())

    async def _request(self, method: str, endpoint: str, **kwargs: typing.Any) -> httpx.Response:
        async with self.client as client:
            return await client.request(method=method, url=endpoint, **kwargs)
