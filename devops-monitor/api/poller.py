from __future__ import annotations

import asyncio

import httpx

from api.models import Server


async def poll_server(server_id: int, url: str, store: dict[int, Server]) -> Server:
    server = store[server_id]
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{url}/health")
        server.status = "UP" if response.status_code == 200 else "DEGRADED"
    except Exception:
        server.status = "DOWN"
    return server


async def run_poll_loop(store: dict[int, Server], interval: int = 10) -> None:
    while True:
        if store:
            tasks = [poll_server(server_id, server.base_url(), store) for server_id, server in list(store.items())]
            await asyncio.gather(*tasks)
        await asyncio.sleep(interval)
