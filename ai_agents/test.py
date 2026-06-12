import json
import requests


def stream_post_request(url, payload):
    """Sends a POST request with a body and streams the response."""
    # Headers indicating we are sending JSON
    headers = {"Content-Type": "application/json"}

    try:
        # Set stream=True in the requests.post call
        with requests.post(
            url, data=json.dumps(payload), headers=headers) as response:

            # Check if the request was successful
            response.raise_for_status()

            print(f"Streaming response from {url}...\n")

            # Iterate over the response lines/chunks
            # decode_unicode=True automatically converts bytes to strings
            for chunk in response.iter_lines(decode_unicode=True):
                if chunk:
                    # Process each line of the stream
                    print(chunk)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


# --- Example Usage ---
if __name__ == "__main__":
    # Replace with your actual endpoint
    target_url = "http://localhost:8002/teams/workload-dna-orchestrator-core/runs/"

    # Replace with your actual request body
    body_message = {
            "message": "Initiate comprehensive live telemetry evaluation sequence for current port 8050 systems.",
            "stream": True,  # Often required by APIs to trigger streaming mode
    }

    stream_post_request(target_url, body_message)
