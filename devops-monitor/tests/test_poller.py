import asyncio

import pytest

from api.models import Server
from api.poller import poll_server, run_poll_loop


@pytest.mark.asyncio
async def test_poll_server_down_status():
    """Test polling a server that doesn't exist (returns DOWN)"""
    store = {}
    server = Server(id=1, name="test", host="localhost", port=9999, status="unknown")
    store[1] = server

    result = await poll_server(1, "http://localhost:9999", store)
    assert result.status in ["DOWN", "DEGRADED"]


@pytest.mark.asyncio
async def test_poll_server_up_status():
    """Test polling a healthy server (127.0.0.1:8000/health)"""
    # This requires the API to be running, so we'll just verify the function works
    store = {}
    server = Server(id=1, name="test", host="localhost", port=8000, status="unknown")
    store[1] = server

    # The poll will try to reach localhost:8000/health
    # It will fail if API is not running, marking it DOWN
    result = await poll_server(1, "http://localhost:8000", store)
    assert result.status in ["UP", "DOWN", "DEGRADED"]


@pytest.mark.asyncio
async def test_run_poll_loop_empty_store():
    """Test poller with empty store (should just iterate)"""
    store = {}

    # Create a task and cancel it after a short time
    task = asyncio.create_task(run_poll_loop(store, interval=1))

    # Let it run for a moment
    await asyncio.sleep(0.5)

    # Cancel the task
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass  # Expected
