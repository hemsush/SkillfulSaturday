import os
import json
import textwrap
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont

# -----------------------------
# Load env
# -----------------------------
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found. Put it in a .env file.")

client = OpenAI(api_key=api_key)

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="Inner Child Cartoon", page_icon="🧒", layout="centered")
st.title("🧒 Inner Child Cartoon")
st.caption("A wholesome AI app: name + childhood favorite → cartoon persona + happy predictions + a shareable card.")

name = st.text_input("Your name / nickname", placeholder="Hema")
favorite = st.text_input(
    "Your childhood favorite (toy / food / game / cartoon / memory)",
    placeholder="e.g., teddy bear, dosa, cricket, Tom & Jerry, hide-and-seek"
)

tone = st.selectbox(
    "Style",
    ["Sweet & Wholesome", "Funny & Playful", "Super Heroic", "Poetic & Warm"],
    index=1
)

kid_safe = st.toggle("Extra kid-safe mode", value=True)

# -----------------------------
# Helpers
# -----------------------------
def safe_json_parse(text: str):
    """Best-effort JSON parser."""
    text = text.strip()
    # If the model adds extra text, try to extract JSON block
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        text = text[start:end+1]
    return json.loads(text)

def make_card_image(card: dict, out_path: str) -> None:
    """
    Generate a simple 'cartoon card' image locally using PIL.
    No external images needed (demo-safe).
    """
    W, H = 1024, 1024
    img = Image.new("RGB", (W, H), (250, 250, 255))
    d = ImageDraw.Draw(img)

    # Fonts (fallback to default if fonts not found)
    def load_font(size: int):
        for f in ["arial.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf"]:
            try:
                return ImageFont.truetype(f, size)
            except Exception:
                continue
        return ImageFont.load_default()

    font_title = load_font(64)
    font_sub = load_font(36)
    font_body = load_font(30)
    font_small = load_font(26)

    # Background shapes
    d.rounded_rectangle([40, 40, W-40, H-40], radius=40, fill=(255, 255, 255))
    d.rounded_rectangle([70, 90, W-70, 240], radius=30, fill=(230, 245, 255))
    d.ellipse([90, 280, 420, 610], fill=(255, 245, 220), outline=(200, 200, 200), width=4)  # "face" placeholder
    d.rounded_rectangle([460, 280, W-90, 610], radius=25, fill=(245, 235, 255), outline=(220, 210, 240), width=3)

    # Cute doodles
    d.ellipse([150, 360, 200, 410], fill=(0, 0, 0))
    d.ellipse([300, 360, 350, 410], fill=(0, 0, 0))
    d.arc([200, 420, 320, 520], start=10, end=170, fill=(0, 0, 0), width=6)  # smile
    d.text((130, 620), "🙂", font=font_title, fill=(0, 0, 0))
    d.text((210, 630), "Inner Child Mode: ON", font=font_sub, fill=(40, 40, 60))

    # Title
    d.text((90, 115), f"{card.get('card_title','Inner Child Cartoon')}", font=font_title, fill=(20, 40, 80))

    # Right block info
    x0, y0 = 490, 300
    d.text((x0, y0), f"Name: {card.get('name','')}", font=font_sub, fill=(60, 30, 90))
    d.text((x0, y0+55), f"Favorite: {card.get('favorite','')}", font=font_body, fill=(60, 30, 90))

    persona = card.get("persona_name", "The Joy Keeper")
    tagline = card.get("tagline", "Smiles in small moments.")
    superpower = card.get("superpower", "Warmth Boost")
    comfort = card.get("comfort_snack", "Hot chocolate")
    catchphrase = card.get("catchphrase", "We got this!")

    # Wrap helper
    def draw_wrapped(label, text, y, max_width_chars=34):
        d.text((x0, y), label, font=font_small, fill=(90, 70, 120))
        wrapped = "\n".join(textwrap.wrap(text, width=max_width_chars))
        d.text((x0, y+32), wrapped, font=font_body, fill=(40, 20, 70))
        return y + 32 + (len(wrapped.splitlines()) * 34) + 18

    y = 380
    y = draw_wrapped("Persona:", persona, y)
    y = draw_wrapped("Tagline:", tagline, y)
    y = draw_wrapped("Superpower:", superpower, y)
    y = draw_wrapped("Comfort snack:", comfort, y)
    y = draw_wrapped("Catchphrase:", catchphrase, y)

    # Predictions at bottom
    preds = card.get("predictions", [])
    d.rounded_rectangle([70, 700, W-70, 930], radius=30, fill=(235, 255, 240), outline=(190, 230, 200), width=3)
    d.text((95, 720), "🔮 Happy Predictions", font=font_sub, fill=(10, 80, 40))

    py = 780
    for i, p in enumerate(preds[:3], start=1):
        line = f"{i}. {p}"
        wrapped = "\n".join(textwrap.wrap(line, width=60))
        d.text((95, py), wrapped, font=font_body, fill=(10, 60, 30))
        py += 42 + (len(wrapped.splitlines()) * 32)

    # Footer
    footer = f"Generated on {datetime.now().strftime('%d %b %Y')}  •  Just for fun ✨"
    d.text((90, 955), footer, font=font_small, fill=(120, 120, 140))

    img.save(out_path)

# -----------------------------
# Generate
# -----------------------------
if st.button("✨ Reveal My Inner Child", use_container_width=True, disabled=not (name and favorite)):
    style = tone
    safety = "Very kid-safe, wholesome, no insults, no sensitive topics." if kid_safe else "Playful and funny, still respectful."

    prompt = f"""
You are a warm, funny, family-friendly storyteller.
Create an "Inner Child Cartoon" persona for a participant.

Participant:
- Name: {name}
- Childhood favorite: {favorite}
- Style: {style}
Safety: {safety}

Rules:
- This is purely playful, not real psychological analysis.
- Keep it uplifting.
- Make it feel like a cute cartoon character profile.

Return ONLY valid JSON with these keys:
{{
  "card_title": "Inner Child Cartoon Card",
  "name": "{name}",
  "favorite": "{favorite}",
  "persona_name": "",
  "tagline": "",
  "superpower": "",
  "comfort_snack": "",
  "catchphrase": "",
  "why_it_matches": "",
  "predictions": ["", "", ""]
}}

Predictions should be short, joyful, and relatable (not spooky).
"""

    with st.spinner("🧒 Talking to your inner child..."):
        res = client.responses.create(
            model="gpt-5",
            input=prompt
        )

    try:
        card = safe_json_parse(res.output_text)
    except Exception:
        st.error("AI returned an unexpected format. Click again once.")
        st.code(res.output_text)
        st.stop()

    # Show results (text)
    st.success("🎉 Inner Child Revealed!")
    st.subheader(f"🎭 Persona: {card.get('persona_name','')}")
    st.write(card.get("why_it_matches", ""))

    st.markdown(f"**✨ Tagline:** _{card.get('tagline','')}_")
    st.markdown(f"**🦸 Superpower:** {card.get('superpower','')}")
    st.markdown(f"**🍪 Comfort snack:** {card.get('comfort_snack','')}")
    st.markdown(f"**🗣️ Catchphrase:** “{card.get('catchphrase','')}”")

    st.markdown("### 🔮 Happy Predictions")
    for i, p in enumerate(card.get("predictions", [])[:3], start=1):
        st.write(f"{i}. {p}")

    # Generate local image card (no OpenAI image model needed)
    out_path = "inner_child_card.png"
    make_card_image(card, out_path)

    st.divider()
    st.image(out_path, caption="🖼️ Your Inner Child Cartoon Card", use_container_width=True)

    with open(out_path, "rb") as f:
        st.download_button(
            "⬇️ Download My Card",
            data=f.read(),
            file_name=f"{name}_inner_child_card.png",
            mime="image/png",
            use_container_width=True
        )

    st.caption("Just for fun ✨ Built with Python + OpenAI text + local card renderer (PIL).")
