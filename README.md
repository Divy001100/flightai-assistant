# ✈️ FlightAI - Airline AI Assistant

Modern multi-modal AI customer support assistant built with Gradio + OpenAI.

**Portfolio-ready • Clean • Beautiful UI • Tool calling + Image + Voice**

## Features
- Real tool calling (prices + fake booking)
- DALL·E 3 destination images
- OpenAI TTS voice replies (autoplay)
- Stunning custom Gradio UI
- Auto SQLite database (20 destinations)
- One-click examples

## Tech Stack
- Python • OpenAI (GPT-4o-mini + DALL·E 3 + TTS-1)
- Gradio 5 (Blocks + custom theme)
- SQLite

## Quick Start
```bash
cd flightai-assistant
pip install -r requirements.txt
cp .env.example .env
# ← Add your OpenAI key in .env
python app.py