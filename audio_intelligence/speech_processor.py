import speech_recognition as sr
import io

class SpeechProcessor:
    """
    Handles conversion of audio bytes to text.
    """

    @staticmethod
    def transcribe_audio(audio_bytes):
        """
        Converts WAV audio bytes (from Streamlit) to text.
        
        Args:
            audio_bytes (bytes): The raw audio data.
            
        Returns:
            str: The transcribed text, or None if failed.
        """
        recognizer = sr.Recognizer()
        
        try:
            # Wrap bytes in BytesIO to make it look like a file
            audio_file = io.BytesIO(audio_bytes)
            
            # Use SpeechRecognition to read the WAV data
            with sr.AudioFile(audio_file) as source:
                # Record the audio from the file
                audio_data = recognizer.record(source)
                
                # Recognize using Google's free API
                text = recognizer.recognize_google(audio_data)
                return text
                
        except sr.UnknownValueError:
            return "Error: Could not understand audio."
        except sr.RequestError as e:
            return f"Error: Could not request results; {e}"
        except Exception as e:
            return f"Error: {str(e)}"

# --- Quick Test ---
if __name__ == "__main__":
    print("SpeechProcessor is ready.")