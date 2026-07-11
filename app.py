import os
import requests
import asyncio
import streamlit as st
import edge_tts

# Streamlit UI configuration
st.set_page_config(page_title="AI Audio Storyteller", page_icon="📖")
st.title("📖 SLM Audio Storyteller")
st.write("Enter an idea, and watch the SLM weave a tale narrated by a lifelike neural voice!")

# User input prompt
user_prompt = st.text_input("Enter a theme or idea:", "A brave drone exploring a hidden valley")

# Stable serverless routing endpoint
API_URL = "https://router.huggingface.co/v1/chat/completions"
HF_TOKEN = st.secrets.get("hf_token", os.getenv("hf_token", ""))

# Define a realistic, rich narrative voice
# Alternative premium options: "en-US-ChristopherNeural" (Male) or "en-US-EmmaNeural" (Female)
NEURAL_VOICE = "en-US-BrianNeural"

def generate_story(prompt):
    if not HF_TOKEN:
        return "⚠️ Error: Please configure your Hugging Face token in Streamlit secrets."
    
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }
    
    creative_instruction = (
        f"Write a highly creative, enchanting, and detailed children's story based on this theme: '{prompt}'. "
        f"Use vivid sensory details, magical descriptions, and a clear story arc (beginning, middle, and end). "
        f"Make it an engaging adventure spanning 3 to 4 distinct paragraphs."
    )
    
    payload = {
        "model": "Qwen/Qwen2.5-7B-Instruct",
        "messages": [{"role": "user", "content": creative_instruction}],
        "max_tokens": 800,
        "temperature": 0.8
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=20)
        if response.status_code == 200:
            res_json = response.json()
            if "choices" in res_json and len(res_json["choices"]) > 0:
                return res_json["choices"][0]["message"]["content"].strip()
            return str(res_json)
        else:
            return f"Error connecting to SLM model: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Network request failed: {str(e)}"

# Helper function to handle async neural speech generation
async def convert_text_to_neural_audio(text, output_path, voice):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

# Execution button
if st.button("Generate & Narrate Story"):
    if user_prompt.strip() == "":
        st.warning("Please provide a prompt first!")
    else:
        with st.spinner("The SLM is weaving a magical tale..."):
            story_text = generate_story(user_prompt)
        
        # Display story text
        st.subheader("📜 The Story")
        st.write(story_text)
        
        # Skip audio generation if text output indicates an error
        if not story_text.startswith("⚠️") and not story_text.startswith("Error") and not story_text.startswith("Network"):
            with st.spinner("Synthesizing human-like audio narration..."):
                try:
                    audio_path = "story_narration.mp3"
                    
                    # Run the async neural text-to-speech process inside Streamlit
                    asyncio.run(convert_text_to_neural_audio(story_text, audio_path, NEURAL_VOICE))
                    
                    # Render the native audio component
                    st.audio(audio_path, format="audio/mp3")
                except Exception as e:
                    st.error(f"Audio generation failed: {e}")