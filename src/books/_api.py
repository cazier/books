import httpx
import pathlib
import json
import os

class Libby:
    token: str
    client: httpx.AsyncClient = None

    @staticmethod
    async def get_identity() -> dict[str, str | bool]:
        if os.getenv("LIBBY_BEARER_TOKEN"):
            return {'identity': os.environ['LIBBY_BEARER_TOKEN'], 'syncable': True}
        
        if pathlib.Path(".libby.json").exists():
            try:
                return json.loads(pathlib.Path(".libby.json").read_text(encoding='utf8'))
            
            except json.JSONDecodeError:
                pass

        async with httpx.AsyncClient() as client:
            resp = await client.post("https://sentry.libbyapp.com/chip")
            resp = resp.raise_for_status()
        
        return resp.json()


    async def setup_sync_code(self) -> str:
        async with self.client as client:
            resp = await client.get("https://sentry.libbyapp.com/chip/clone/code")
            resp = resp.raise_for_status()

            print(resp.json()['code'])

            return resp.json()['code']


    async def __init__(self) -> None:
        identity = await self.get_identity()

        self.token = identity['identity']
        self.client = httpx.AsyncClient(headers={'Authorization': f'Bearer {self.token}'})
        
        if not identity['syncable']:
            self.setup_sync_code()



# def get(url: str) -> httpx.Response:
#     auth = httpx.
#     with httpx.AsyncClient(base_url="https://vandal.libbyapp.com", )