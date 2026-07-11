import os
import requests
import streamlit as st
from gtts import gTTS

# Streamlit UI configuration
st.set_page_config(page_title="AI Audio Storyteller", page_icon="📖")
st.title("📖 SLM Audio Storyteller")
st.write("Enter a simple prompt, and watch an SLM spin a tale and narrate it out loud!")

# User input prompt
user_prompt = st.text_input("Enter a theme or idea:", "A brave drone exploring a hidden valley")

# New stable serverless routing endpoint
API_URL = "https://router.huggingface.co/v1/chat/completions"
HF_TOKEN = st.secrets.get("hf_token", os.getenv("hf_token", ""))

def generate_story(prompt):
    if not HF_TOKEN:
        return "⚠️ Error: Please configure your Hugging Face token in Streamlit secrets."
    
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Using the standard structured chat format compatible with the updated router
    payload = {
        "model": "microsoft/Phi-3-mini-4k-instruct",
        "messages": [
            {
                "role": "user",
                "content": f"Write a very short, engaging, exactly 3-sentence children's story based on this prompt: {prompt}"
            }
        ],
        "max_tokens": 150,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=15)
        
        if response.status_code == 200:
            res_json = response.json()
            # Extract content from the structured chat completion structure
            if "choices" in res_json and len(res_json["choices"]) > 0:
                return res_json["choices"][0]["message"]["content"].strip()
            return str(res_json)
        else:
            return f"Error connecting to SLM model: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"Network request failed: {str(e)}"

# Execution button
if st.button("Generate & Narrate Story"):
    if user_prompt.strip() == "":
        st.warning("Please provide a prompt first!")
    else:
        with st.spinner("The SLM is composing your story..."):
            story_text = generate_story(user_prompt)
        
        # Display story text
        st.subheader("📜 The Story")
        st.write(story_text)
        
        # Skip audio generation if text output indicates an error
        if not story_text.startswith("⚠️") and not story_text.startswith("Error") and not story_text.startswith("Network"):
            with st.spinner("Synthesizing audio narration..."):
                try:
                    # Convert generated text to audio speech using gTTS
                    tts = gTTS(text=story_text, lang='en', slow=False)
                    audio_path = "story_narration.mp3"
                    tts.save(audio_path)
                    
                    # Render the native audio component
                    st.audio(audio_path, format="audio/mp3")
                except Exception as e:
                    st.error(f"Audio generation failed: {e}")