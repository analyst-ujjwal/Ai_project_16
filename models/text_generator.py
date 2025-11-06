import os, json, re
from langchain_groq import ChatGroq

def generate_presentation_content(topic, num_slides=5, use_groq=True):
    """
    Generates structured slide content for a given topic using Groq or fallback.
    Repairs malformed JSON outputs automatically.
    """
    if not use_groq:
        return [{"title": f"Slide {i+1}", "points": [f"Point {j+1}" for j in range(3)]} for i in range(num_slides)]

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return [{"title": "Error", "points": ["Missing GROQ_API_KEY in environment."]}]

    chat = ChatGroq(api_key=api_key, model="llama-3.3-70b-versatile")

    prompt = (
        f"Create a professional {num_slides}-slide presentation on '{topic}'. "
        "For each slide, provide:\n"
        "1. A short, clear title\n"
        "2. 3–5 concise bullet points\n"
        "Respond ONLY with valid JSON array format:\n"
        "[{\"title\": \"Slide Title\", \"points\": [\"point1\", \"point2\", ...]}]"
    )

    response = chat.invoke(prompt)
    raw = response.content.strip()
    print("RAW OUTPUT:\n", raw)

    # --- Repair Stage 1: Basic cleanup ---
    cleaned = raw
    cleaned = re.sub(r',\s*}', '}', cleaned)          # remove stray trailing commas
    cleaned = re.sub(r'}\s*{', '}, {', cleaned)       # ensure commas between objects
    cleaned = re.sub(r'}}', '}]', cleaned)            # fix double braces
    cleaned = re.sub(r']\s*\[', '], [', cleaned)      # join multiple arrays

    # Wrap if not properly enclosed
    if not cleaned.strip().startswith('['):
        cleaned = '[' + cleaned
    if not cleaned.strip().endswith(']'):
        cleaned = cleaned + ']'

    # --- Attempt JSON parse ---
    try:
        slides = json.loads(cleaned)
        if isinstance(slides, list):
            return slides
    except json.JSONDecodeError as e:
        print("JSON failed, fallback:", e)

    # --- Repair Stage 2: Regex salvage ---
    titles = re.findall(r'"title"\s*:\s*"([^"]+)"', raw)
    bullets = re.findall(r'"points"\s*:\s*\[(.*?)\]', raw, re.DOTALL)
    slides = []
    for i, t in enumerate(titles):
        pts = re.findall(r'"([^"]+)"', bullets[i]) if i < len(bullets) else []
        slides.append({"title": t, "points": pts})

    if slides:
        return slides

    # --- Fallback: just return text lines ---
    return [{
        "title": f"{topic} Overview",
        "points": [line.strip("-• ") for line in raw.splitlines() if line.strip()]
    }]
