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

        print(f"{data}")

    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Could not connect to {url}")
    except requests.exceptions.Timeout:
        print(f"[ERROR] Request to {url} timed out")
    except requests.exceptions.HTTPError:
        print(f"[ERROR] {response.json()['detail']}")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Request failed: {e}")

    return None


def cmd_find_images(config, query: str):
    pass
