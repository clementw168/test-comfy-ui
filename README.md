# test-comfy-ui
Using comfy with python rather than the Web UI.


## Usage

This repository uses `uv` to manage dependencies.

```bash
uv sync
```

Before running the script, make sure that the `ComfyUI` server is running and modify the `server_address` in `comfy2py.py` to the IP of the server.

Then run the script with the following command:
```bash
uv run comfy2py.py --prompt "a dog running in the wild with a red hat" --neg-prompt "sun" --steps 50
```

This will generate an image based on the prompt and save it as `generated_image.png`.


![Photo of a dog running in the wild with a red hat](generated_image.png)
