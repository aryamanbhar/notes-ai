import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def load_model():
    api_key = os.getenv("HF_API_KEY")
    if not api_key:
        raise ValueError("HF_API_KEY not found in .env file")
    return api_key

def generate_creative_outputs(annotation, slide_context, slide_number, annot_type):
    try:
        api_key = load_model()
        headers = {"Authorization": f"Bearer {api_key}"}
        prompt = (
            f"You are an expert tutor creating engaging study aids for a student. "
            f"Slide {slide_number} content: '{slide_context[:500]}'.\n"
            f"Annotation ({annot_type}): '{annotation}'.\n"
            f"Return a JSON object with:\n"
            f"- 'el5': A concise, beginner-friendly explanation (max 100 words, simple language).\n"
            f"- 'mnemonic': A short, memorable phrase to recall the concept.\n"
            f"- 'analogy': A relatable analogy connecting the concept to daily life (max 100 words).\n"
            f"- 'diagram_prompt': A short, clear prompt for an AI image generator to create a diagram that visually explains the annotation and its context (max 30 words).\n"
            f"Ensure the JSON is valid and outputs are clear, creative, and accurate."
        )
        payload = {
            "inputs": prompt,
            "parameters": {"max_new_tokens": 350, "temperature": 0.7}
        }
        response = requests.post(
            "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1",
            headers=headers,
            json=payload
        )
        if response.status_code == 403:
            return {"error": "⚠️ API access denied. Check HF_API_KEY or rate limits."}
        elif response.status_code != 200:
            return {"error": f"⚠️ API error: {response.status_code} - {response.text}"}
        try:
            output = response.json()[0]["generated_text"]
            json_start = output.find("{")
            json_end = output.rfind("}") + 1
            if json_start != -1 and json_end != -1:
                outputs = json.loads(output[json_start:json_end])
            else:
                outputs = {
                    "el5": "Failed to generate ELI5",
                    "mnemonic": "Failed to generate mnemonic",
                    "analogy": "Failed to generate analogy",
                    "diagram_prompt": ""
                }
        except (json.JSONDecodeError, KeyError):
            outputs = {
                "el5": "Failed to generate ELI5",
                "mnemonic": "Failed to generate mnemonic",
                "analogy": "Failed to generate analogy",
                "diagram_prompt": ""
            }
        return outputs
    except Exception as e:
        return {"error": f"⚠️ Error: {str(e)}"}

def generate_diagram_image_sdxl(diagram_prompt):
    try:
        api_key = load_model()
        headers = {"Authorization": f"Bearer {api_key}"}
        payload = {"inputs": diagram_prompt}
        response = requests.post(
            "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0",
            headers=headers,
            json=payload,
            timeout=120,
        )
        if response.status_code == 200 and response.headers.get("content-type", "").startswith("image"):
            return response.content
        else:
            # The caller will handle warnings/errors
            return None
    except Exception:
        return None
