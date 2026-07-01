from __future__ import annotations

import os
import time

import httpx
import pandas as pd
import streamlit as st

API_BASE = os.getenv("API_BASE", "http://localhost:8000")
API_KEY = os.getenv("API_KEY", "dev-secret-key")

st.set_page_config(
    page_title="DevOps Monitoring Dashboard", page_icon="📡", layout="wide"
)


@st.cache_data(ttl=2)
def fetch_metrics() -> dict:
    response = httpx.get(f"{API_BASE}/metrics", timeout=3.0)
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=5)
def fetch_servers() -> list[dict]:
    response = httpx.get(f"{API_BASE}/servers", timeout=3.0)
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=5)
def fetch_server(server_id: int) -> dict:
    response = httpx.get(f"{API_BASE}/servers/{server_id}", timeout=3.0)
    response.raise_for_status()
    return response.json()


if "metrics_history" not in st.session_state:
    st.session_state.metrics_history = []

st.title("📡 DevOps Monitoring Dashboard")

metrics_tab, servers_tab = st.tabs(["Metrics", "Servers"])

with metrics_tab:
    metrics = fetch_metrics()
    st.session_state.metrics_history.append({"ts": time.time(), **metrics})
    st.session_state.metrics_history = st.session_state.metrics_history[-60:]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("CPU", f"{metrics['cpu_percent']:.1f}%")
    col2.metric(
        "Memory",
        f"{metrics['memory_percent']:.1f}%",
        f"{metrics['memory_used_gb']:.1f} / {metrics['memory_total_gb']:.1f} GB",
    )
    col3.metric("Disk", f"{metrics['disk_percent']:.1f}%")
    col4.metric("API", "Online")

    history = pd.DataFrame(st.session_state.metrics_history)
    if not history.empty:
        history["time"] = pd.to_datetime(history["ts"], unit="s")
        chart_data = history.set_index("time")[["cpu_percent", "memory_percent"]]
        st.line_chart(chart_data, height=260)

with servers_tab:
    try:
        servers = fetch_servers()
    except Exception as exc:
        st.error(f"Cannot load servers: {exc}")
        servers = []

    if servers:
        df = pd.DataFrame(servers)

        def highlight_row(row):  # noqa: F841
            colors = {
                "UP": "background-color: #dcfce7",
                "DEGRADED": "background-color: #fef3c7",
                "DOWN": "background-color: #fee2e2",
            }
            style = colors.get(row.get("status"), "")
            return [style] * len(row)

        st.dataframe(
            df.style.apply(highlight_row, axis=1),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No servers registered yet.")

    with st.form("add_server_form", clear_on_submit=True):
        st.subheader("Add a server")
        name = st.text_input("Name")
        host = st.text_input("Host")
        port = st.number_input("Port", min_value=1, max_value=65535, value=8080)
        submitted = st.form_submit_button("Register")

    if submitted:
        response = httpx.post(
            f"{API_BASE}/servers",
            json={"name": name, "host": host, "port": int(port)},
            headers={"X-API-Key": API_KEY},
            timeout=5.0,
        )
        if response.status_code == 201:
            fetch_servers.clear()
            st.success(f"Registered {name}")
            st.rerun()
        else:
            st.error(f"Error {response.status_code}: {response.text}")

    if servers:
        selected_id = st.selectbox(
            "Select server to check", [server["id"] for server in servers]
        )
        if st.button("Run health check"):
            response = httpx.post(
                f"{API_BASE}/servers/{selected_id}/check", timeout=5.0
            )
            if response.status_code == 200:
                fetch_servers.clear()
                st.success("Health check completed")
                st.rerun()
            else:
                st.error(f"Error {response.status_code}: {response.text}")

placeholder = st.empty()
with placeholder.container():
    st.caption("Auto-refresh every 2 seconds")
time.sleep(2)
st.rerun()
