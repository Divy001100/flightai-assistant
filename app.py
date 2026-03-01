import gradio as gr
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

from prompts import SYSTEM_PROMPT, IMAGE_PROMPT
from tools import get_ticket_price, start_booking_process, init_database

load_dotenv()
client = OpenAI()

MODEL = "gpt-4o-mini"
init_database()

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_ticket_price",
            "description": "Get approximate return ticket price to a city.",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "start_booking_process",
            "description": "ONLY call this when you have collected: destination, date (YYYY-MM-DD), number of passengers, lead passenger full name, email address. Optional: travel class.",
            "parameters": {
                "type": "object",
                "properties": {
                    "destination": {"type": "string"},
                    "date": {"type": "string"},
                    "passengers": {"type": "integer"},
                    "lead_passenger_name": {"type": "string"},
                    "email": {"type": "string"},
                    "travel_class": {"type": "string", "enum": ["Economy", "Premium Economy", "Business"], "default": "Economy"}
                },
                "required": ["destination", "date", "passengers", "lead_passenger_name", "email"]
            }
        }
    }
]

def generate_image(city: str):
    try:
        resp = client.images.generate(
            model="dall-e-3",
            prompt=IMAGE_PROMPT.format(city=city),
            n=1, size="1024x1024", response_format="url"
        )
        return resp.data[0].url
    except:
        return None

def generate_voice(text: str):
    try:
        resp = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text[:4096]
        )
        return resp.content
    except:
        return None

def chat_with_tools(history):
    if not history:
        return history, None, None

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)

    image_url = None
    audio = None
    last_reply = ""

    while True:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.65,
            max_tokens=600
        )

        choice = resp.choices[0]
        msg = choice.message
        messages.append(msg)

        if not msg.tool_calls:
            last_reply = msg.content or ""
            break

        for tool_call in msg.tool_calls:
            args = json.loads(tool_call.function.arguments or "{}")
            name = tool_call.function.name

            if name == "get_ticket_price":
                result = get_ticket_price(args.get("city", ""))
            elif name == "start_booking_process":
                result = start_booking_process(
                    destination=args.get("destination", ""),
                    date=args.get("date", ""),
                    passengers=args.get("passengers", 1),
                    lead_passenger_name=args.get("lead_passenger_name", ""),
                    email=args.get("email", ""),
                    travel_class=args.get("travel_class", "Economy")
                )
            else:
                result = "Tool not implemented."

            messages.append({
                "role": "tool",
                "content": result,
                "tool_call_id": tool_call.id
            })

    new_history = history + [{"role": "assistant", "content": last_reply}]

    # Try to find city for image (simple keyword match)
    last_text = (last_reply or "").lower() + " " + (history[-1]["content"] or "").lower() if history else ""
    possible_cities = ["paris", "london", "tokyo", "dubai", "santorini", "bali", "rome", "sydney"]
    for city in possible_cities:
        if city in last_text:
            image_url = generate_image(city.title())
            break

    if last_reply:
        audio = generate_voice(last_reply)

    return new_history, audio, image_url

# ──────────────────────────────────────────────── UI ────────────────────────────────────────────────

with gr.Blocks(
    theme=gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="sky",
        neutral_hue="slate",
        radius_size="lg",
        spacing_size="md"
    ),
    css="""
    .gradio-container {
        background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
    }
    h1, h2, h3, strong, p {
        color: #0f172a !important;  /* dark navy - visible on light bg */
    }
    .markdown {
        text-align: center;
        padding: 1.5rem 1rem;
    }
    .developer {
        font-size: 1rem;
        color: #334155;
        margin: 0.5rem 0 1.5rem 0;
    }
    """
) as demo:
    gr.Markdown(
        """
        # ✈️ FlightAI – Your Travel Assistant
        """,
        elem_classes="markdown"
    )
    
    gr.Markdown(
        "Developed by Divyanshu Singh",
        elem_classes="developer"
    )
    
    gr.Markdown(
        "Ask about prices, book flights, get travel inspiration",
        elem_classes="markdown"
    )

    with gr.Row(equal_height=True):
        chatbot = gr.Chatbot(
            height=580,
            label="💬 Chat with FlightAI"
        )
        image_out = gr.Image(label="Destination Inspiration", height=400)

    audio_out = gr.Audio(
        label="🔊 Voice Response",
        autoplay=True,
        interactive=False
    )

    msg = gr.Textbox(
        placeholder="Example: Book a flight to Paris next summer",
        label="Your message",
        autofocus=True
    )

    gr.Examples(
        examples=[
            ["How much to fly to Dubai?"],
            ["I want to book to Tokyo for 2 people in July 2026"],
            ["Show me Santorini"],
            ["Book flight to Paris June 15 2026, 3 passengers"]
        ],
        inputs=msg
    )

    msg.submit(
        lambda m, h: ("", h + [{"role": "user", "content": m}]),
        [msg, chatbot],
        [msg, chatbot]
    ).then(
        chat_with_tools,
        chatbot,
        [chatbot, audio_out, image_out]
    )

if __name__ == "__main__":
   demo.launch(ssr_mode=False)