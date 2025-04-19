import io
import json
import urllib.request

import websocket
from PIL import Image

# Configuration - UPDATE THIS TO THE IP OF THE COMFYUI SERVER
server_address = "127.0.0.1:8000"


def load_workflow(filename="workflow.json"):
    with open(filename, "r") as file:
        return json.load(file)


def update_workflow_with_prompt(workflow, prompt, negative_prompt, steps):
    workflow["6"]["inputs"]["text"] = prompt
    workflow["7"]["inputs"]["text"] = negative_prompt
    workflow["3"]["inputs"]["steps"] = steps

    return workflow


def queue_prompt(prompt):
    data = json.dumps({"prompt": prompt}).encode("utf-8")
    req = urllib.request.Request(
        f"http://{server_address}/prompt",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}")
        print(f"Response body: {e.read().decode('utf-8')}")
        raise


def get_image(
    prompt_id,
    timeout=600,
):
    try:
        # Initialize websocket with proper error handling
        ws = websocket.WebSocket()
        ws.settimeout(timeout)
        ws.connect(f"ws://{server_address}/ws")

        print(f"Waiting for image data for prompt ID: {prompt_id}")

        while True:
            try:
                message = ws.recv()
                if isinstance(message, str):
                    data = json.loads(message)
                    print(f"Received message: {data}")
                    if data["type"] == "executing":
                        if (
                            data["data"]["node"] is None
                            and data["data"]["prompt_id"] == prompt_id
                        ):
                            print("Execution completed")
                            break
                elif isinstance(message, bytes):
                    print("Received binary data")
                    image = Image.open(
                        io.BytesIO(message[8:])
                    )  # Skip first 8 bytes (message type)
                    ws.close()
                    return image
            except websocket.WebSocketTimeoutException:
                print("WebSocket timeout occurred")
                break
            except websocket.WebSocketException as e:
                print(f"WebSocket error occurred: {e}")
                break
            except Exception as e:
                print(f"Unexpected error: {e}")
                break

    except Exception as e:
        print(f"Failed to initialize WebSocket connection: {e}")
    finally:
        try:
            ws.close()
        except:
            pass

    return None


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate an image using a text prompt"
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default="a dog running in the wild with a red hat",
        help="Text prompt for image generation",
    )
    parser.add_argument(
        "--neg-prompt",
        type=str,
        default="sun",
        help="Negative prompt to avoid certain elements",
    )
    parser.add_argument(
        "--steps", type=int, default=50, help="Number of inference steps"
    )

    args = parser.parse_args()
    prompt = args.prompt
    neg_prompt = args.neg_prompt
    steps = args.steps

    # Load workflow from JSON file
    workflow = load_workflow()
    print("Workflow loaded successfully.")

    # Update the workflow with the input image
    workflow = update_workflow_with_prompt(workflow, prompt, neg_prompt, steps)
    print("Workflow updated with input.")

    # Generate image
    response = queue_prompt(workflow)
    prompt_id = response["prompt_id"]
    print(f"Prompt queued with ID: {prompt_id}")

    image = get_image(prompt_id)
    if image:
        output_filename = "generated_image.png"
        image.save(output_filename)
        print(f"Image saved as {output_filename}")
        print(f"Image size: {image.size}")
        print(f"Image mode: {image.mode}")
    else:
        print("Failed to retrieve image")

    print("Script execution completed.")
