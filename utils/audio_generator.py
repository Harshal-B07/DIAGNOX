from gtts import gTTS
from io import BytesIO

def generate_audio_summary(text):
    """
    Converts text to audio bytes using Google Text-to-Speech.
    """
    if not text:
        return None
        
    try:
        # Create TTS object
        tts = gTTS(text=text, lang='en', slow=False)
        
        # Save to memory buffer instead of disk
        audio_buffer = BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        
        return audio_buffer
    except Exception as e:
        print(f"Error generating audio: {e}")
        return None