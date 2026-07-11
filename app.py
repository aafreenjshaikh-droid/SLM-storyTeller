import os
import requests
import streamlit as st
from gtts import gTTS  # Fixed import syntax and casing

# Streamlit UI configuration
st.set_page_config(page_title="AI Audio Storyteller", page_icon="📖")
st.title("📖 SLM Audio Storyteller")
st.write("Enter a simple prompt, and watch an SLM spin a tale and narrate it out loud!")

# User input prompt
user_prompt = st.text_input("Enter a theme or idea:", "A brave drone exploring a hidden valley")

# 1. SLM configuration using Hugging Face Serverless API
api_url = "https://api-inference.huggingface.co/models/microsoft/Phi-3-mini-4k-instruct"
hf_token = st.secrets.get("hf_token", os.getenv("hf_token", ""))

def generate_story(prompt):
    if not hf_token:
        return "⚠️ Error: Please configure your Hugging Face token in Streamlit secrets."
    
    headers = {"Authorization": f"bearer {hf_token}"}
    payload = {
        "inputs": f"<|user|>\nWrite a very short, engaging, 3-sentence children's story based on this prompt: {prompt}<|end|>\n<|assistant|>",
        "parameters": {"max_new_tokens": 150, "temperature": 0.7}
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload)
        if response.status_code == 200:
            res_json = response.json()
            if isinstance(res_json, list) and "generated_text" in res_json[0]:
                full_text = res_json[0]["generated_text"]
                # Clean up Phi-3 prompt templates if they are returned in the text
                if "<|assistant|>" in full_text:
                    return full_text.split("<|assistant|>")[-1].strip()
                return full_text.strip()
            return str(res_json)
        else:
            return f"Error connecting to SLM model: {response.text}"
    except Exception as e:
        return f"Request failed: {str(e)}"

# 2. Execution button
if st.button("Generate & Narrate Story"):
    if user_prompt.strip() == "":
        st.warning("Please provide a prompt first!")
    else:
        with st.spinner("The SLM is composing your story..."):
            story_text = generate_story(user_prompt)
        
        # Display story text
        st.subheader("📜 The Story")
        st.write(story_text)
        
        # Skip audio if text generation failed with an error message
        if not story_text.startswith("⚠️") and not story_text.startswith("Error"):
            with st.spinner("Synthesizing audio narration..."):
                try:
                    # Convert generated text to audio speech using correct casing
                    tts = gTTS(text=story_text, lang='en', slow=False)
                    audio_path = "story_narration.mp3"
                    tts.save(audio_path)
                    
                    # Render native web audio player (Fixed cut-off code)
                    st.audio(audio_path, format="audio/mp3")
                except Exception as e:
                    st.error(f"Audio generation failed: {e}")
