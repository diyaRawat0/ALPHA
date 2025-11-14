import os
import sys
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import play, VoiceSettings

# Load environment variables from .env file
load_dotenv()

# --- Initialize ElevenLabs Client ---
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not ELEVENLABS_API_KEY:
    print("Error: ELEVENLABS_API_KEY not found in environment variables or .env file.")
    print("Please create a .env file in the same directory as this script with: ELEVENLABS_API_KEY=YOUR_API_KEY_HERE")
    sys.exit(1)

elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# --- Configuration for ElevenLabs Voice ---
# IMPORTANT: Use a Voice ID that is available to your ElevenLabs account.
# You previously identified 'Kumar' with ID 'LQMC3j3fn1LA9ZhI4o8g'.
# If you want to use a different voice, replace this ID.
DEFAULT_VOICE_ID = "Xb7hH8MSUJpSbSDYk0k2" # Kumar's Voice ID


# --- Eleven Labs Text-to-Speech Function ---
def eleven_labs_text_to_speech(text_to_convert, voice_id=DEFAULT_VOICE_ID, model_id="eleven_multilingual_v2",
                               stability=0.7, similarity_boost=0.75):
    """
    Converts text to speech using the Eleven Labs API and plays it directly.

    Args:
        text_to_convert (str): The text you want to convert to speech.
        voice_id (str): The ID of the voice to use.
        model_id (str): The model ID to use (e.g., "eleven_multilingual_v2", "eleven_turbo_v2_5").
        stability (float): Controls the voice consistency (0.0-1.0).
        similarity_boost (float): Adjusts similarity to reference voice (0.0-1.0).
    """
    if not text_to_convert:
        print("[TTS]: No text to speak provided.")
        return

    print(f"\n[ElevenLabs TTS]: Generating speech for voice ID: {voice_id}")
    print(f"[ElevenLabs TTS]: Text: \"{text_to_convert}\"")

    try:
        audio = elevenlabs_client.text_to_speech.convert(
            text=text_to_convert,
            voice_id=voice_id,
            model_id=model_id,
            voice_settings=VoiceSettings(
                stability=stability,
                similarity_boost=similarity_boost,
                style=0.0,
                use_speaker_boost=True
            ),
            output_format="mp3_44100_128" # High quality MP3 format
        )

        print("[ElevenLabs TTS]: Playing audio...")
        play(audio) # Requires FFmpeg's ffplay in your system PATH
        print("[ElevenLabs TTS]: Audio playback finished.")

    except Exception as e:
        print(f"[ElevenLabs TTS Error]: An error occurred during TTS generation or playback: {e}")
        if "Authentication failed" in str(e) or "invalid API key" in str(e):
            print("Please check your ELEVENLABS_API_KEY in the .env file.")
        elif "usage limit" in str(e):
            print("You might have reached your ElevenLabs usage limit. Check your dashboard.")
        elif "voice_not_found" in str(e):
            print(f"Voice ID '{voice_id}' might not exist or is not available for your account.")
        elif "ffplay from ffmpeg not found" in str(e):
            print("FFmpeg (specifically ffplay) is required to play audio. Please install it and ensure it's in your system's PATH.")
        else:
            print("Ensure your internet connection is stable and the ElevenLabs service is available.")


# --- Main Execution ---
if __name__ == "__main__":
    print("--- Eleven Labs Text-to-Audio Converter ---")
    print("Type your text to convert to audio. Type 'quit' or 'exit' to stop.")

    try:
        print("\n--- Available ElevenLabs Voices ---")
        available_voices = elevenlabs_client.voices.get_all()
        for voice in available_voices.voices:
            print(f"Name: {voice.name}, ID: {voice.voice_id}, Category: {voice.category}")
        print("-----------------------------------\n")
    except Exception as e:
        print(f"Could not retrieve voices from ElevenLabs: {e}")
        print("Ensure your API key is correct and you have an internet connection.")


    while True:
        # Ask the user for text input in a loop
        user_input = input("Enter text: ").strip()

        if user_input.lower() in ['quit', 'exit']:
            print("Exiting program.")
            break
        elif user_input:
            # Call the function to convert and play the text
            eleven_labs_text_to_speech(user_input)
        else:
            print("No text entered. Please try again or type 'quit' to exit.")

    print("\n--- Program Finished ---")
