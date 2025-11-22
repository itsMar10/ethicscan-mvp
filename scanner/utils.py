import httpx

async def send_prompt(target_url: str, prompt: str) -> str:
    """
    Sends a prompt to the target URL and returns the response text.
    Assumes the target accepts a JSON payload with a 'prompt' key.
    """
    async with httpx.AsyncClient() as client:
        try:
            # Adjust the payload structure based on the expected target API.
            # For a generic LLM endpoint, it might be {"prompt": ...} or {"messages": ...}
            # We'll assume a simple {"prompt": prompt} for this MVP.
            response = await client.post(target_url, json={"prompt": prompt}, timeout=10.0)
            response.raise_for_status()
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"
