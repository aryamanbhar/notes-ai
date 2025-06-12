import requests
api_key = "HF_API_KEY"
headers = {"Authorization": f"Bearer {api_key}"}
payload = {"inputs": "diagram of water molecule"}
response = requests.post(
    "https://api-inference.huggingface.co/models/CompVis/stable-diffusion-v1-4",
    headers=headers,
    json=payload,
    timeout=90,
)
print(response.status_code)
print(response.headers.get("content-type"))
if response.status_code == 200 and response.headers.get("content-type", "").startswith("image"):
    with open("test_output.png", "wb") as f:
        f.write(response.content)
else:
    print(response.text)