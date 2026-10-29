<div align="center">
  <div style="display: flex; align-items: center; justify-content: center; gap: 8px;">
    <img src="assets/clens.webp" alt="Clens" width="60" style="margin: 0; display: block;" />
    <h1 style="margin: 0; line-height: 1; display: flex; align-items: center; border-bottom: none">Clens</h1>
  </div>

  <b>Local semantic image search tool</b>

  <video width="80%" controls muted>
    <source src="assets/demo.mp4" type="video/mp4">
  </video>

  <p>
    Clens is a semantic image search tool that allows users 
    to index a given directory of images and search through it 
    using natural language, search for matching images using 
    another image etc. locally on their device.
  </p>
</div>

## Installation

Clens currently requires Python 3.14 or newer. The recommended installation
uses the CPU-only PyTorch packages, so it does not download NVIDIA/CUDA
libraries on CPU machines.

### Install with uv

Install the published package as an isolated command-line tool. The extra
PyTorch index is needed because CPU-only PyTorch wheels are published there:

```bash
uv tool install \
  --index https://download.pytorch.org/whl/cpu \
  --default-index https://pypi.org/simple \
  clens-cli
```

### Install with pipx

`pipx` also installs command-line applications into an isolated environment:

```bash
pipx install \
  --pip-args="--index-url https://download.pytorch.org/whl/cpu --extra-index-url https://pypi.org/simple" \
  clens-cli
```

After installation, verify the command:

```bash
clens version
clens --help
```

The first indexing or search operation downloads the local CLIP model so may take a few minutes. It is
cached locally and reused for later runs.

## Usage

Clens uses a local background server (FastAPI + ChromaDB + CLIP) to keep embeddings loaded in memory for faster indexing and search.

### 1. Server

Before indexing or searching, make sure the clens server is running.

Start the server:
```bash
# Start in current shell
clens server start

# Or detach to run in background
clens server start --detach
```

> Defaults to `127.0.0.1:6969`. You can pass custom host/port:
> ```bash
> clens server start --port 6969 --detach
> ```

Check status or stop:
```bash
# Check if server is running
clens server status

# Stop running server
clens server stop
```

---

### 2. Index a Directory

Recursively indexes `.png` and `.jpg` images from a directory and stores embeddings in local ChromaDB:

```bash
clens index ./Pictures
```
*Indexing may take a few moments depending on the number of images in the directory and your hardware.*

---

### 3. Find Images with Text (`find`)

Search indexed images with natural language:

```bash
clens find "a dog with a hat"
```

Change number of results with `-c` / `--count` (default is 5):
```bash
clens find "a dog with a hat" -c 10
```

---

### 4. Find Matching Images (`match`)

Pass an image to find visually and semantically matching images in your indexed directories:

```bash
clens match ./sample_images/dog.png
```

Specify number of matches:
```bash
clens match ./sample_images/dog.png -c 3
```

---

### 5. Plain Output for Scripts & Piping (`-p`)

By default, clens renders an ANSI table with match percentage and clickable file paths. Use `-p` / `--plain` to get raw tab-separated output (`RANK`, `SCORE`, `FILENAME`, `PATH`):

```bash
# Tab-separated output
clens find "sunset" -p

# Example: pipe top result to xdg-open
clens find "cat sleeping" -c 1 -p | awk 'NR==2 {print $4}' | xargs xdg-open
```

---

### Configuration

Clens automatically generates a config file at `~/.config/clens/config.json` (or `$XDG_CONFIG_HOME/clens/config.json`):

```json
{
  "preferences": {
    "default_host": "127.0.0.1",
    "default_port": 6969
  }
}
```

Currently available options:
* `preferences.default_host`: Default host the server binds to and client commands connect to (default: `"127.0.0.1"`).
* `preferences.default_port`: Default port used by the server and CLI (default: `6969`).

---

## Commands 

```
clens server start [-H HOST] [-p PORT] [-d]   Start clens server (-d to detach)
clens server status                            Get server status
clens server stop                              Stop running server
clens index <path>                             Index a directory of images
clens find <query_term> [-c COUNT] [-p]        Find images by text description
clens match <image_path> [-c COUNT] [-p]       Find images matching an existing image
clens version                                  Print current version
```

For indepth info about the program
```bash
clens -h/-help
```
