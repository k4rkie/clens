import signal

import requests
from pathlib import Path
import logging
import os
import subprocess
import sys
import time

logger = logging.getLogger(__name__)


def cmd_start_server(config, config_path: Path, host: str, port: int, detach: bool):
    import uvicorn

    config.runtime.active_host = host
    config.runtime.active_port = port

    if config.runtime.pid:
        try:
            os.kill(config.runtime.pid, 0)
            logger.warning("Clens server is already running!")
            return
        except ProcessLookupError, OSError:
            config.runtime.pid = None
            config.runtime.active_host = None
            config.runtime.active_port = None

    if not detach:
        try:
            logger.info(f"Server running at http://{host}:{port}")
            config.runtime.pid = os.getpid()
            config.save_to_file(config_path)
            uvicorn.run(
                "clens.server:clens_server",
                host=host,
                port=port,
                log_level=logging.WARN,
                reload=True,
                access_log=False,
            )

        finally:
            logger.info(f"Server shutting down....")
            config.runtime.active_host = None
            config.runtime.active_port = None
            config.runtime.pid = None
            config.save_to_file(config_path)
            logger.info(f"Server shutdown successfully.")
    else:
        log_dir = Path.home() / ".cache" / "clens"
        log_file = log_dir / "clens.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)

        output = open(log_file, "a")

        start_cmd = [
            sys.executable,
            "-m",
            "uvicorn",
            "clens.server:clens_server",
            "--host",
            host,
            "--port",
            str(port),
            "--log-level",
            "warning",
        ]

        process = subprocess.Popen(
            start_cmd, stdout=output, stderr=output, start_new_session=True
        )
        output.close()

        # Check if server is actually up
        health_url = f"http://{host}:{port}/api/health"
        server_started = False
        timeout = 3.0
        start_time = time.time()

        while time.time() - start_time < timeout:
            exit_code = process.poll()
            if exit_code is not None:
                break  # Process died!

            try:
                res = requests.get(health_url, timeout=0.2)
                if res.status_code == 200:
                    server_started = True
                    break
            except requests.RequestException:
                time.sleep(0.1)

        if server_started:
            config.runtime.pid = process.pid
            config.save_to_file(config_path)
            logger.info(
                f"Server started in background on http://{host}:{port} (PID: {process.pid})"
            )
            logger.info(f"Logs available at: {log_file}")
        else:
            # if server didnt respond check if the subprocess is still up

            # if not timeout and kill the process
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=1.0)
                logger.error("Server start failed! Clens server timed out.")

            logger.error("Failed to start clens server!")


def cmd_stop_server(config, config_path: Path):
    if not config.runtime.pid:
        logger.error("No running clens server found.")
        return
    try:
        os.kill(config.runtime.pid, signal.SIGTERM)
        logger.info(f"Clens server stopped successfully (PID: {config.runtime.pid})")
    except ProcessLookupError:
        logger.info(f"Clens server was already stopped")

    config.runtime.active_host = None
    config.runtime.active_port = None
    config.runtime.pid = None
    config.save_to_file(config_path)


def cmd_server_status(config):
    if config.runtime.pid and config.runtime.active_host and config.runtime.active_port:
        try:
            os.kill(config.runtime.pid, 0)
            print(
                f"Clens server is running on http://{config.runtime.active_host}:{config.runtime.active_port} (PID: {config.runtime.pid}) "
            )
            return
        except ProcessLookupError, OSError:
            config.runtime.active_host = None
            config.runtime.active_port = None
            config.runtime.pid = None
    else:
        print("Clens server isnt running!! Start the server with: clens server start")


def cmd_index_images(config, path: str):
    root_dir = Path(path).absolute()
    url = f"http://{config.runtime.active_host}:{config.runtime.active_port}/api/index"

    logger.info(f"Indexing the directory: {str(root_dir)}...")
    logger.info(f"This may take a few moments...")

    try:
        response = requests.post(
            url,
            json={"path": str(root_dir)},
        )
        response.raise_for_status()
        try:
            data = response.json()
        except ValueError:
            data = response.text

        logger.info(f"{data['message']}")

    except requests.exceptions.ConnectionError:
        logger.error(f"Could not connect to {url}")
    except requests.exceptions.Timeout:
        logger.error(f"Request to {url} timed out")
    except requests.exceptions.HTTPError:
        logger.error(f"{response.json()['detail']}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")

    return None


def cmd_find_images(config, query: str, plain: bool, count: int):
    url = f"http://{config.runtime.active_host}:{config.runtime.active_port}/api/find"

    logger.info(f"Finding matches for {query}...")
    logger.info(f"This may take a few moments...")

    try:
        response = requests.post(
            url,
            json={"query_term": str(query), "count": count},
        )
        response.raise_for_status()
        try:
            data = response.json()
        except ValueError:
            data = response.text

        logger.info(f"Found results for {query}")
        if not plain:
            display_find_results_table(data)
            return
        display_find_results_plain(data)

    except requests.exceptions.ConnectionError:
        logger.error(f"Connection: Could not connect to {url}")
    except requests.exceptions.Timeout:
        logger.error(f"Timeout: Request to {url} timed out")
    except requests.exceptions.HTTPError:
        logger.error(f"HTTP {response.json()['detail']}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
    return None


def display_find_results_table(res) -> None:
    results = res.get("message", res)
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


def display_find_results_plain(res) -> None:
    results = res.get("message", res)
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
