import os
import streamlit as st
from gtts import gTTS
from huggingface_hub import InferenceClient  # <-- Use the official client

# Streamlit UI configuration
st.set_page_config(page_title="AI Audio Storyteller", page_icon="📖")
st.title("📖 SLM Audio Storyteller")
st.write("Enter a simple prompt, and watch an SLM spin a tale and narrate it out loud!")

# User input prompt
user_prompt = st.text_input("Enter a theme or idea:", "A brave drone exploring a hidden valley")

# Fetch Hugging Face Token
hf_token = st.secrets.get("hf_token", os.getenv("hf_token", ""))

def generate_story(prompt):
    if not hf_token:
        return "⚠️ Error: Please configure your Hugging Face token in Streamlit secrets."
    
    try:
        # Initialize client with token and specific model
        client = InferenceClient(model="microsoft/Phi-3-mini-4k-instruct", token=hf_token)
        
        # Format prompt
        formatted_prompt = f"<|user|>\nWrite a very short, engaging, 3-sentence children's story based on this prompt: {prompt}<|end|>\n<|assistant|>"
        
        # Generate text
        response = client.text_generation(
            formatted_prompt,
            max_new_tokens=150,
            temperature=0.7
        )
        
        return response.strip()
        
    except Exception as e:
        return f"Request failed: {str(e)}"

# Execution button
if st.button("Generate & Narrate Story"):
    if user_prompt.strip() == "":
        st.warning("Please provide a prompt first!")
    else:
        with st.spinner("The SLM is composing your story..."):
            story_text = generate_story(user_prompt)
        
        st.subheader("📜 The Story")
        st.write(story_text)
        
        if not story_text.startswith("⚠️") and not story_text.startswith("Request failed"):
            with st.spinner("Synthesizing audio narration..."):
                try:
                    tts = gTTS(text=story_text, lang='en', slow=False)
                    audio_path = "story_narration.mp3"
                    tts.save(audio_path)
                    st.audio(audio_path, format="audio/mp3")
                except Exception as e:
                    st.error(f"Audio generation failed: {e}")