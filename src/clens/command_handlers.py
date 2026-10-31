import signal
import socket
import requests
from pathlib import Path
import logging
import os
import subprocess
import sys
import time
from clens.data_schemas import ResponseBody
from pydantic import ValidationError
from urllib.parse import urljoin, quote
from clens.paths import LOG_FILE
from clens.runtime import RuntimeState, LOCAL_HOST
from clens.exceptions import NoImagesFoundError
from clens.logger_config import configure_logging

logger = logging.getLogger(__name__)

STARTUP_TIMEOUT = 300.0
STATUS_TIMEOUT = 1.0
STOP_TIMEOUT = 5.0


def cmd_start_server(port: int, detach: bool):

    if RuntimeState.load_runtime().is_running(timeout=STATUS_TIMEOUT):
        logger.warning("Clens server is already running!")
        return

    os.environ["CLENS_RUNTIME_PORT"] = str(port)

    if is_port_in_use(port):
        logger.error(f"The port: {port} is already in use! Try another port instead")
        sys.exit(1)

    if not detach:
        try:
            configure_logging(server=True)
            logger.info(f"Starting clens server at http://{LOCAL_HOST}:{port}")
            import uvicorn

            uvicorn.run(
                "clens.server:clens_server",
                host=LOCAL_HOST,
                port=port,
                log_level="info",
                access_log=False,
                log_config=None,
            )

        finally:
            logger.info(f"Server shutting down....")
            logger.info(f"Server shutdown successfully.")
    else:
        logger.info(f"Starting clens server...")
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

        output = open(LOG_FILE, "a", buffering=1, encoding="utf-8")

        start_cmd = [
            sys.executable,
            "-m",
            "clens.server",
        ]

        process = subprocess.Popen(
            start_cmd, stdout=subprocess.DEVNULL, stderr=output, start_new_session=True
        )
        output.close()

        started_state = RuntimeState(active_port=port, pid=process.pid)

        if started_state.wait_until_running(deadline=STARTUP_TIMEOUT):
            logger.info(
                f"Server started in background on http://{LOCAL_HOST}:{port} (PID: {process.pid})"
            )
            logger.info(f"Logs available at: {LOG_FILE}")
        else:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=1.0)
                except subprocess.TimeoutExpired:
                    process.kill()
                logger.error("Server start failed! Clens server timed out.")
            else:
                logger.error("Failed to start clens server!")
            sys.exit(1)


def cmd_stop_server():
    state = RuntimeState.load_runtime()
    pid = state.pid

    if pid is None or not state.is_pid_running():
        state.clear_runtime()
        logger.error("No running clens server found.")
        return

    try:
        os.kill(pid, signal.SIGTERM)
    except OSError:
        state.clear_runtime()
        logger.info("Clens server was already stopped")
        return

    deadline = time.monotonic() + STOP_TIMEOUT
    while time.monotonic() < deadline and state.is_pid_running():
        time.sleep(0.1)

    if state.is_pid_running():
        logger.warning(f"Clens server is still shutting down (PID: {pid})")
    else:
        state.clear_runtime()
        logger.info(f"Clens server stopped successfully (PID: {pid})")


def cmd_server_status():
    state = RuntimeState.load_runtime()

    if not state.is_pid_running():
        state.clear_runtime()
        print("Clens server isnt running!! Start the server with: clens server start")
        return

    if state.is_healthy(timeout=STATUS_TIMEOUT):
        print(
            f"Clens server is running on http://{LOCAL_HOST}:{state.active_port} (PID: {state.pid})"
        )
        return

    print(
        f"Clens server process is running (PID: {state.pid}) but is not responding on http://{LOCAL_HOST}:{state.active_port}"
    )


def cmd_index_images(path: str) -> None:
    state = RuntimeState.load_runtime()
    root_dir = Path(path).absolute()
    url = f"http://{LOCAL_HOST}:{state.active_port}/api/index"

    logger.info(f"Indexing the directory: {str(root_dir)}...")
    logger.info(f"This may take a few moments...")

    try:
        response = requests.post(
            url,
            json={"path": str(root_dir)},
        )
        response.raise_for_status()

        data = ResponseBody.model_validate_json(response.text)

        logger.info(f"{data.message}")

    except ValidationError as VE:
        logger.error(f"API contract violation (Invalid response schema): {VE}")
    except requests.exceptions.ConnectionError:
        logger.error(f"Could not connect to {url}")
    except requests.exceptions.Timeout:
        logger.error(f"Request to {url} timed out")
    except requests.exceptions.HTTPError:
        data = ResponseBody.model_validate_json(response.text)
        logger.error(f"{data.message}")
        if data.error_type == NoImagesFoundError.error_type:
            logger.info("Make sure the directory contains .jpg or .png images.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")

    return None


def cmd_find_images(query: str, count: int, plain: bool) -> None:

    if count <= 0:
        logger.error(f"count must be greater than 0: got -c, --count: {count}")
        sys.exit(1)

    state = RuntimeState.load_runtime()
    url = urljoin(
        f"http://{LOCAL_HOST}:{state.active_port}/api/find/",
        quote(query),
    )

    logger.info(f"Finding results for {query}...")
    logger.info(f"This may take a few moments...")

    try:
        response = requests.get(
            url,
            params={"count": count},
        )
        response.raise_for_status()
        data = ResponseBody.model_validate_json(response.text)

        logger.info(f"{data.message}")
        if not plain:
            display_results_table(data.body)
            return
        display_results_plain(data.body)

    except ValidationError as VE:
        logger.error(f"API contract violation (Invalid response schema): {VE}")
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection: Could not connect to {url}")
    except requests.exceptions.Timeout:
        logger.error(f"Timeout: Request to {url} timed out")
    except requests.exceptions.HTTPError:
        data = ResponseBody.model_validate_json(response.text)
        logger.error(f"{data.message}")
        if data.error_type == "ChromaNotFoundError":
            logger.info(f"Index a directory first! Try: clens index <path>")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
    return None


def cmd_match_image(img_path: str, count: int, plain: bool) -> None:
    image_to_match = Path(img_path).absolute()

    if count <= 0:
        logger.error(f"count must be greater than 0: got -c/--count: {count}")
        sys.exit(1)

    state = RuntimeState.load_runtime()
    url = f"http://{LOCAL_HOST}:{state.active_port}/api/match"

    logger.info(f"Finding matches for {os.path.basename(img_path)}...")
    logger.info(f"This may take a few moments...")

    try:
        response = requests.get(
            url,
            params={"image_path": img_path, "count": count},
        )
        response.raise_for_status()
        data = ResponseBody.model_validate_json(response.text)

        logger.info(f"{data.message}")
        if not plain:
            display_results_table(data.body)
            return
        display_results_plain(data.body)

    except ValidationError as VE:
        logger.error(f"API contract violation (Invalid response schema): {VE}")
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection: Could not connect to {url}")
    except requests.exceptions.Timeout:
        logger.error(f"Timeout: Request to {url} timed out")
    except requests.exceptions.HTTPError:
        data = ResponseBody.model_validate_json(response.text)
        logger.error(f"{data.message}")
        if data.error_type == "ChromaNotFoundError":
            logger.info(f"Index a directory first! Try: clens index <path>")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
    return None


def display_results_table(response) -> None:
    results = response.get("message", response)
    metadatas = results.get("metadatas", [[]])
    distances = results.get("distances", [[]])

    if not metadatas or not metadatas[0]:
        print("\n\033[33mNo matching images found.\033[0m\n")
        return

    items_meta = metadatas[0]
    items_dist = distances[0] if distances else [0.0] * len(items_meta)

    headers = ["RANK", "SCORE", "FILENAME", "PATH"]
    rows = []

    for i, (meta, dist) in enumerate(zip(items_meta, items_dist), start=1):
        path_str = meta.get("path", "")
        filename = Path(path_str).name or "Unknown"

        # In ChromaDB cosine space: distance = 1 - cosine_similarity
        # So: similarity = (1 - distance) * 100%
        similarity = max(0.0, min(1.0, 1.0 - dist)) * 100

        rows.append([f"#{i}", f"{similarity:.1f}%", filename, path_str])

    # 1. Compute dynamic column widths so nothing wraps awkwardly
    widths = [len(h) for h in headers]
    for row in rows:
        for idx, col in enumerate(row):
            widths[idx] = max(widths[idx], len(col))

    # 2. Build dividers and format strings
    divider = "─" * (sum(widths) + 2 * (len(widths) - 1))

    # 3. Print table with clean ANSI styling (hardcoded bright white base)
    print()
    header_str = "  ".join(f"{h:<{widths[i]}}" for i, h in enumerate(headers))
    print(f"\033[1;97m{header_str}\033[0m")
    print(f"\033[97m{divider}\033[0m")

    for rank, score, fname, pth in rows:
        # Green score accent, clickable OSC 8 hyperlink on path, white base colors
        # get file path with file:// prefixed
        uri = Path(pth).resolve().as_uri()
        # turn that into a hyprlink with OSC 8 esc sequence
        linked_pth = f"\033]8;;{uri}\033\\{pth}\033]8;;\033\\"
        print(
            f"\033[97m{rank:<{widths[0]}}\033[0m  "
            f"\033[1;32m{score:<{widths[1]}}\033[0m  "
            f"\033[1;97m{fname:<{widths[2]}}\033[0m  "
            f"\033[97m{linked_pth}\033[0m"
        )

    print(f"\033[97m{divider}\033[0m")
    print(f"\033[97mFound {len(rows)} matching results\033[0m\n")


def display_results_plain(response) -> None:
    results = response.get("message", response)
    metadatas = results.get("metadatas", [[]])
    distances = results.get("distances", [[]])

    if not metadatas or not metadatas[0]:
        return

    items_meta = metadatas[0]
    items_dist = distances[0] if distances else [0.0] * len(items_meta)

    headers = ["RANK", "SCORE", "FILENAME", "PATH"]
    print("\t".join(headers))

    for i, (meta, dist) in enumerate(zip(items_meta, items_dist), start=1):
        path_str = meta.get("path", "")
        filename = Path(path_str).name or "Unknown"
        similarity = max(0.0, min(1.0, 1.0 - dist)) * 100
        print(f"{i}\t{similarity:.1f}%\t{filename}\t{path_str}")


def is_port_in_use(port: int) -> bool:
    try:
        with socket.create_connection((LOCAL_HOST, port), timeout=0.5):
            return True
    except OSError:
        return False
