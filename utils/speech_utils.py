import os
import logging
import tempfile
from gtts import gTTS
import speech_recognition as sr

def text_to_speech(text, lang='en'):
    """
    Convert text to speech using gTTS.
    
    Args:
        text (str): Text to convert to speech
        lang (str): Language code
        
    Returns:
        bytes: Audio data in MP3 format
    """
    try:
        # Create a temporary file to store the audio
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            temp_filename = temp_file.name
        
        # Generate the speech
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(temp_filename)
        
        # Read the file content
        with open(temp_filename, 'rb') as f:
            audio_data = f.read()
        
        # Clean up the temporary file
        os.unlink(temp_filename)
        
        return audio_data
    
    except Exception as e:
        logging.error(f"Error in text_to_speech: {str(e)}")
        return None

def speech_to_text(audio_data):
    """
    Convert speech to text using SpeechRecognition.
    
    Args:
        audio_data (bytes): Audio data in WAV format
        
    Returns:
        str: Recognized text
    """
    try:
        recognizer = sr.Recognizer()
        
        # Create a temporary file to store the audio
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            temp_file.write(audio_data)
            temp_filename = temp_file.name
        
        # Recognize the speech
        with sr.AudioFile(temp_filename) as source:
            audio = recognizer.record(source)
            
        # Use Google's speech recognition
        text = recognizer.recognize_google(audio)
        
        # Clean up the temporary file
        os.unlink(temp_filename)
        
        return text
    
    except sr.UnknownValueError:
        return "Speech Recognition could not understand audio"
    except sr.RequestError as e:
        return f"Could not request results from Speech Recognition service; {e}"
    except Exception as e:
        logging.error(f"Error in speech_to_text: {str(e)}")
        return "Error processing audio"

def analyze_speech_characteristics(audio_data):
    """
    Analyze speech characteristics (fluency, pauses, etc.)
    
    Args:
        audio_data (bytes): Audio data
        
    Returns:
        dict: Analysis results
    """
    # This is a simplified placeholder for speech analysis
    # In a real implementation, this would use more sophisticated audio processing
    
    try:
        text = speech_to_text(audio_data)
        word_count = len(text.split())
        
        analysis = {
            "word_count": word_count,
            "estimated_duration": len(audio_data) / 16000,  # Rough estimate
            "fluency_score": min(10, max(1, word_count / 20)),  # Simple heuristic
            "feedback": "Speak clearly and at a moderate pace for best results."
        }
        
        return analysis
    
    except Exception as e:
        logging.error(f"Error in analyze_speech_characteristics: {str(e)}")
        return {
            "error": str(e),
            "feedback": "Unable to analyze speech characteristics."
        }
