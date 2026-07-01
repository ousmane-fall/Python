from __future__ import annotations

import asyncio
import json
import os
from contextlib import asynccontextmanager

from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    Query,
    WebSocket,
    WebSocketDisconnect,
)

from api.auth import verify_api_key
from api.metrics import get_system_metrics
from api.models import Server, ServerIn, ServerOut
from api.poller import poll_server, run_poll_loop

STORE: dict[int, Server] = {}
NEXT_ID = 1


def reset_store() -> None:
    global NEXT_ID
    STORE.clear()
    NEXT_ID = 1


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = None
    if os.getenv("DISABLE_POLL_LOOP") != "1":
        task = asyncio.create_task(run_poll_loop(STORE))
    try:
        yield
    finally:
        if task is not None:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass


app = FastAPI(title="DevOps Monitoring API", lifespan=lifespan)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/metrics")
async def metrics() -> dict:
    return get_system_metrics()


@app.websocket("/ws/metrics")
async def ws_metrics(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await websocket.send_text(json.dumps(get_system_metrics()))
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        return


@app.post("/servers", response_model=ServerOut, status_code=201)
async def register_server(server: ServerIn, _: str = Depends(verify_api_key)):
    global NEXT_ID
    record = Server(id=NEXT_ID, **server.model_dump())
    STORE[NEXT_ID] = record
    NEXT_ID += 1
    return record


@app.get("/servers", response_model=list[ServerOut])
async def list_servers(status: str | None = Query(default=None)):
    servers = list(STORE.values())
    if status:
        servers = [server for server in servers if server.status == status]
    return servers


@app.get("/servers/{server_id}", response_model=ServerOut)
async def get_server(server_id: int):
    if server_id not in STORE:
        raise HTTPException(status_code=404, detail="Server not found")
    return STORE[server_id]


@app.delete("/servers/{server_id}", status_code=204)
async def delete_server(server_id: int, _: str = Depends(verify_api_key)):
    if server_id not in STORE:
        raise HTTPException(status_code=404, detail="Server not found")
    del STORE[server_id]


@app.post("/servers/{server_id}/check", response_model=ServerOut)
async def check_server_now(server_id: int):
    if server_id not in STORE:
        raise HTTPException(status_code=404, detail="Server not found")
    server = STORE[server_id]
    updated = await poll_server(server_id, server.base_url(), STORE)
    return updated
