# ComfyUI Integration

This directory is reserved for ComfyUI workflows and custom nodes.

## Setup
1. Clone ComfyUI into this directory (or link to an external installation).
2. Install dependencies: `pip install -r requirements.txt` (inside ComfyUI folder).
3. Place custom workflows in `workflows/`.

## Structure
- `workflows/`: JSON workflow files.
- `custom_nodes/`: Custom Python nodes.
- `models/`: Checkpoints and LoRAs (symlinked if large).

## Usage
Run ComfyUI normally:
```bash
python main.py
```
