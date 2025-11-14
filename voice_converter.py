import sys
import os
import pyttsx3  # pyttsx3 for local feedback like "Listening..."
import speech_recognition as sr
import threading
import time  # For simulating delay if needed, though less critical now
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import play, VoiceSettings # Removed GenerationOptions
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QMessageBox, QLineEdit,
    QTextBrowser, QStackedWidget
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtGui import QFont, QColor, QPalette, QMovie, QIcon

# Import the corrected backend GeminiAssistant
from backend.assistant_core import GeminiAssistant
# Load environment variables from .env file (for ElevenLabs API Key)
load_dotenv()
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not ELEVENLABS_API_KEY:
    print("WARNING: ELEVENLABS_API_KEY not found. ElevenLabs TTS will not function.")

# --- Global ElevenLabs Client (initialized once) ---
elevenlabs_client = None
DEFAULT_ELEVENLABS_VOICE_ID = None
if ELEVENLABS_API_KEY:
    try:
        elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        # Kumar's Voice ID - Make sure this is available on your plan!
        DEFAULT_ELEVENLABS_VOICE_ID = "LQMC3j3fn1LA9ZhI4o8g"
    except Exception as e:
        print(f"ERROR: Failed to initialize ElevenLabs client: {e}")
        elevenlabs_client = None


# --- Utility Function for Dark Theme Palette ---
def _create_dark_palette():
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(20, 20, 20))
    palette.setColor(QPalette.WindowText, QColor(220, 220, 220))
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(40, 40, 40))
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 220))
    palette.setColor(QPalette.ToolTipText, QColor(0, 0, 0))
    palette.setColor(QPalette.Text, QColor(220, 220, 220))
    palette.setColor(QPalette.Button, QColor(50, 50, 50))
    palette.setColor(QPalette.ButtonText, QColor(220, 220, 220))
    palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.Link, QColor(80, 180, 255))
    palette.setColor(QPalette.Highlight, QColor(60, 140, 220))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    return palette


# --- Speech Recognition Worker Thread (STT) ---
class SpeechRecognitionThread(QThread):
    recognized_text = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    listening_status = pyqtSignal(str)

    def __init__(self, recognizer_instance, parent=None):
        super().__init__(parent)
        self.recognizer = recognizer_instance
        self._is_running = True # Keep for potential future stop mechanism, though listen() blocks

    def run(self):
        with sr.Microphone() as source:
            self.listening_status.emit("Adjusting for ambient noise...")
            try:
                # Add a local TTS feedback "Listening..." before blocking operation
                # This needs to be done on a separate thread or use pyttsx3.say directly
                # However, for simplicity here, we'll rely on the GUI status update.
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                self.listening_status.emit("Listening...")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=8)
                self.listening_status.emit("Processing speech...")
                text = self.recognizer.recognize_google(audio)
                self.recognized_text.emit(text)
            except sr.UnknownValueError:
                self.error_occurred.emit("Could not understand audio.")
            except sr.RequestError as e:
                self.error_occurred.emit(f"Speech service error: {e}")
            except sr.WaitTimeoutError:
                self.error_occurred.emit("No speech detected.")
            except Exception as e:
                self.error_occurred.emit(f"STT unexpected error: {e}")
        self.listening_status.emit("Ready.")

    def stop(self):
        # Stopping sr.Recognizer.listen() is tricky as it's blocking.
        # This method is primarily for conceptual completeness if you were to use
        # a non-blocking audio input stream. For now, listen() will run to timeout/detection.
        self._is_running = False


# --- Assistant Response Thread (Non-Streaming LLM + Non-Streaming TTS) ---
class AssistantResponseThread(QThread):
    response_complete = pyqtSignal(str) # Emits the final text response
    error_occurred = pyqtSignal(str)
    thinking_status = pyqtSignal(bool) # To show/hide spinner

    def __init__(self, assistant_instance, user_query, elevenlabs_client_instance, voice_id, parent=None):
        super().__init__(parent)
        self.assistant = assistant_instance
        self.user_query = user_query
        self.elevenlabs_client = elevenlabs_client_instance
        self.voice_id = voice_id

    def run(self):
        self.thinking_status.emit(True) # Show spinner
        full_response_text = ""
        try:
            # Call the non-streaming send_prompt from GeminiAssistant
            # This yields a (type, content) tuple from backend/assistant_core.py
            # So, we iterate to get the single result.
            response_generator = self.assistant.send_prompt(self.user_query)
            for response_type, content in response_generator:
                if response_type == "final_text":
                    full_response_text = content
                elif response_type == "error":
                    self.error_occurred.emit(f"LLM processing error: {content}")
                    full_response_text = f"LLM Error: {content}" # Use error as response text
                break # Expecting only one (type, content) pair

            if full_response_text and self.elevenlabs_client and self.voice_id:
                try:
                    # Use text_to_speech.convert() for non-streaming TTS
                    audio = self.elevenlabs_client.text_to_speech.convert(
                        text=full_response_text,
                        voice_id=self.voice_id,
                        model_id="eleven_multilingual_v2",
                        voice_settings=VoiceSettings(stability=0.7, similarity_boost=0.75, style=0.0, use_speaker_boost=True),
                        output_format="mp3_44100_128"
                    )
                    play(audio) # This will block until the full audio is played
                except Exception as e:
                    self.error_occurred.emit(f"ElevenLabs TTS error: {e}")
                    # Continue with just text response if TTS fails
            elif not full_response_text:
                full_response_text = "No valid response generated by the assistant."

            self.response_complete.emit(full_response_text)

        except Exception as e:
            self.error_occurred.emit(f"An unexpected error occurred in response thread: {e}")
            self.response_complete.emit(f"An unexpected error occurred: {e}") # Ensure GUI gets a message
        finally:
            self.thinking_status.emit(False) # Hide spinner


# --- Welcome Screen Widget ---
class WelcomeScreen(QWidget):
    enter_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setPalette(_create_dark_palette())
        self.setAutoFillBackground(True)

        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(50, 50, 50, 50)

        welcome_label = QLabel("AI Assistant Ready! 🤖")
        welcome_label.setFont(QFont("Arial", 48, QFont.ExtraBold))
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet(
            "color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #61DAFB, stop:1 #FF69B4);"
            "text-shadow: 2px 2px 5px #000000;"
            "margin-bottom: 30px;"
        )
        layout.addWidget(welcome_label)

        self.description_browser = QTextBrowser()
        self.description_browser.setReadOnly(True)
        self.description_browser.setOpenExternalLinks(False)
        self.description_browser.setFont(QFont("Segoe UI", 12))
        self.description_browser.setStyleSheet(
            "background-color: #2D2D2D;"
            "color: #E0E0E0;"
            "border-radius: 12px;"
            "padding: 15px;"
            "border: 1px solid #444;"
        )

        html_content = """
        <p style="text-align: center; margin-top: 0; margin-bottom: 15px; font-size: 16pt;">
            <b>Welcome to your Model</b>
        </p>
        <p style="text-align: justify; margin-bottom: 10px;">
            I am an AI assistant designed to help you automate various tasks on your
            computer and online, simply by understanding your natural language
            commands. Think of me as your personal, highly capable script executor!
        </p>
        <p style="text-align: justify; margin-bottom: 10px;">
            I can manage files and folders, create Python scripts, interact with
            websites, and even perform specific web automation tasks.
        </p>
        <p style="font-size: 14pt; margin-top: 20px; margin-bottom: 10px;">
            <b>Here are a few examples of what I can do:</b>
        </p>
        <p style="margin-left: 20px; margin-bottom: 5px;">
            <b>📂 Folder & File Management:</b> Create, delete, move, and list files/folders.
        </p>
        <p style="margin-left: 20px; margin-bottom: 15px;">
            <b>🌐 Web & Automation Tasks:</b> Browse websites, fill forms, extract data, automate web interactions.
        </p>
        <p style="font-size: 14pt; margin-top: 20px; margin-bottom: 10px;">
            <b>How to use:</b>
        </p>
        <p style="margin-left: 20px;">
            - Simply type your command or request at the prompt.
        </p>
        """
        self.description_browser.setHtml(html_content)
        layout.addWidget(self.description_browser)

        enter_button = QPushButton("Enter Chat")
        enter_button.setFont(QFont("Arial", 24, QFont.Bold))
        enter_button.setStyleSheet(
            "background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #28A745, stop:1 #4CAF50);"
            "color: white;"
            "border-radius: 25px;"
            "padding: 20px 40px;"
            "border: 2px solid #1E88E5;"
            "box-shadow: 5px 5px 15px rgba(0, 0, 0, 0.5);"
            "QPushButton:hover { background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #218838, stop:1 #388E3C); }"
            "QPushButton:pressed { background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1E7E34, stop:1 #2E7D32); padding-top: 22px; padding-bottom: 18px; }"
        )
        enter_button.setFixedSize(300, 80)
        enter_button.clicked.connect(self.enter_clicked.emit)
        layout.addWidget(enter_button, alignment=Qt.AlignCenter)


# --- Chatbot Interface Widget ---
class ChatbotScreen(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.assistant = GeminiAssistant()  # The real GeminiAssistant now
        self.recognizer = sr.Recognizer()
        self.tts_engine_local = pyttsx3.init()

        # Threads
        self.stt_thread = SpeechRecognitionThread(self.recognizer)
        self.assistant_response_thread = None # Now uses a simpler thread

        self.initUI()
        self._connect_threads()

    def initUI(self):
        self.setPalette(_create_dark_palette())
        self.setAutoFillBackground(True)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        self.chat_history_display = QTextBrowser()
        self.chat_history_display.setFont(QFont("Monospace", 12))
        self.chat_history_display.setStyleSheet(
            "background-color: #2D2D2D;"
            "color: #E0E0E0;"
            "border-radius: 12px;"
            "padding: 15px;"
            "border: 1px solid #444;"
            "box-shadow: inset 0px 0px 8px rgba(0, 0, 0, 0.4);"
        )
        self.chat_history_display.setOpenExternalLinks(False)
        self.chat_history_display.setReadOnly(True)
        main_layout.addWidget(self.chat_history_display)

        self.add_message("Bot", "Hello! I'm your AI assistant. How can I help you today?")

        # Removed streaming_response_label and its associated styling as it's no longer used for LLM output.
        # It's only used for STT status now.
        self.stt_status_label = QLabel() # Renamed for clarity
        self.stt_status_label.setFont(QFont("Monospace", 12))
        self.stt_status_label.setStyleSheet(
            "color: #A5D6A7; font-style: italic; padding-left: 10px; margin-bottom: 8px;"
            "border-bottom: 1px solid #444;"
            "padding-bottom: 5px;"
        )
        self.stt_status_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.stt_status_label.hide() # Hidden initially
        main_layout.addWidget(self.stt_status_label)


        self.spinner_label = QLabel()
        self.spinner_movie = QMovie("spinn1.gif")
        if self.spinner_movie.isValid():
            self.spinner_label.setMovie(self.spinner_movie)
            self.spinner_label.setFixedSize(32, 32)
            self.spinner_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.spinner_label.setStyleSheet("padding-left: 10px; margin-bottom: 8px;")
            self.spinner_movie.start() # Start movie, but hide label
            self.spinner_label.hide()
        else:
            print("Error: Could not load spinn1.gif. Make sure it's in the correct path.")
            self.spinner_label.setText("Thinking...")
            self.spinner_label.setStyleSheet(
                "color: #FFA500; font-style: italic; padding-left: 10px; margin-bottom: 8px;")

        spinner_layout = QHBoxLayout()
        spinner_layout.addWidget(self.spinner_label)
        spinner_layout.addStretch()
        main_layout.addLayout(spinner_layout)

        input_control_layout = QHBoxLayout()
        input_control_layout.setSpacing(10)

        self.user_input_field = QLineEdit()
        self.user_input_field.setPlaceholderText("Type your message here or click mic to speak...")
        self.user_input_field.setFont(QFont("Arial", 12))
        self.user_input_field.setStyleSheet(
            "background-color: #383838;"
            "color: white;"
            "padding: 10px;"
            "border-radius: 8px;"
            "border: 1px solid #666;"
            "selection-background-color: #1E88E5;"
            "selection-color: white;"
        )
        self.user_input_field.returnPressed.connect(self._send_message)
        input_control_layout.addWidget(self.user_input_field)

        self.mic_button = QPushButton()
        self.mic_button.setIcon(QIcon("mic_icon.png"))  # Ensure mic_icon.png exists or replace with text
        self.mic_button.setIconSize(self.mic_button.sizeHint() * 0.7)
        self.mic_button.setFixedSize(40, 40)
        self.mic_button.setStyleSheet(
            "background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF5733, stop:1 #FF8D33);"
            "color: white;"
            "border-radius: 20px;"
            "border: none;"
            "QPushButton:hover { background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #E04E2D, stop:1 #E07A2D); }"
            "QPushButton:pressed { background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #C04526, stop:1 #C06A26); padding-top: 22px; padding-bottom: 18px; }"
        )
        self.mic_button.clicked.connect(self._start_voice_input)
        input_control_layout.addWidget(self.mic_button)

        self.send_button = QPushButton("Send")
        self.send_button.setFont(QFont("Arial", 12, QFont.Bold))
        self.send_button.setStyleSheet(
            "background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #007BFF, stop:1 #0056b3);"
            "color: white;"
            "border-radius: 8px;"
            "padding: 10px 20px;"
            "border: none;"
            "QPushButton:hover { background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0056b3, stop:1 #004085); }"
            "QPushButton:pressed { background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #004085, stop:1 #002752); padding-top: 12px; padding-bottom: 8px; }"
        )
        self.send_button.setFixedSize(100, 40)
        self.send_button.clicked.connect(self._send_message)
        input_control_layout.addWidget(self.send_button)

        main_layout.addLayout(input_control_layout)

    def _connect_threads(self):
        self.stt_thread.recognized_text.connect(self._handle_stt_result)
        self.stt_thread.error_occurred.connect(self._handle_stt_error)
        self.stt_thread.listening_status.connect(self._update_stt_status_label) # Connect to renamed label

    def _set_input_enabled(self, enabled):
        self.user_input_field.setEnabled(enabled)
        self.send_button.setEnabled(enabled)
        self.mic_button.setEnabled(enabled)

    def add_message(self, sender, message):
        if sender == "User":
            color = "#90CAF9"
            align = Qt.AlignRight
            background = "#4A4A4A"
            float_style = "right"
        else:  # Bot (for final display)
            color = "#A5D6A7"
            align = Qt.AlignLeft
            background = "#3A3A3A"
            float_style = "left"

        formatted_message = f'''
        <div style="background-color: {background}; border-radius: 10px; padding: 8px 12px; margin-bottom: 8px; max-width: 80%; float: {float_style}; clear: both;">
            <p style="color:{color}; font-size:11pt; margin: 0;"><b>{sender}:</b> {message}</p>
        </div>
        '''
        self.chat_history_display.append(formatted_message)
        self.chat_history_display.verticalScrollBar().setValue(self.chat_history_display.verticalScrollBar().maximum())

    def _send_message(self):
        user_message = self.user_input_field.text().strip()
        if user_message:
            self.add_message("User", user_message)
            self.user_input_field.clear()
            self._set_input_enabled(False)  # Disable input while bot is thinking
            self._toggle_spinner(True) # Show spinner

            # Hide STT status label and clear it, as we are now processing LLM response
            self.stt_status_label.hide()
            self.stt_status_label.setText("")

            self.chat_history_display.verticalScrollBar().setValue(
                self.chat_history_display.verticalScrollBar().maximum())

            # Start the non-streaming LLM + TTS process
            self.assistant_response_thread = AssistantResponseThread(
                self.assistant,
                user_message,
                elevenlabs_client,
                DEFAULT_ELEVENLABS_VOICE_ID
            )
            self.assistant_response_thread.response_complete.connect(self._handle_bot_response_complete)
            self.assistant_response_thread.error_occurred.connect(self._handle_assistant_thread_error)
            self.assistant_response_thread.thinking_status.connect(self._toggle_spinner)
            self.assistant_response_thread.start()
        else:
            QMessageBox.warning(self, "Empty Message", "Please type a message before sending.")

    def _start_voice_input(self):
        # Ensure previous STT thread is stopped if running (though listen() blocks)
        if self.stt_thread.isRunning():
            self.stt_thread.stop() # This signals to stop, but blocking listen() will still finish
            self.stt_thread.wait(500) # Wait a bit for it to clean up if possible

        self._set_input_enabled(False)
        self.user_input_field.setPlaceholderText("Listening for your voice...")
        self._toggle_spinner(True) # Show spinner for listening
        self.stt_status_label.show() # Show STT status label
        self.stt_status_label.setText("Preparing microphone...")
        self.chat_history_display.verticalScrollBar().setValue(self.chat_history_display.verticalScrollBar().maximum())
        self.stt_thread.start()

    def _handle_stt_result(self, text):
        self.user_input_field.setText(text)
        self.user_input_field.setPlaceholderText("Type your message here or click mic to speak...")
        self._toggle_spinner(False) # Hide spinner after STT
        self.stt_status_label.hide() # Hide STT status label
        self._set_input_enabled(True)
        self._send_message()  # Automatically send recognized text

    def _handle_stt_error(self, error_message):
        self.user_input_field.setPlaceholderText("Type your message here or click mic to speak...")
        self._toggle_spinner(False) # Hide spinner
        self.stt_status_label.hide() # Hide STT status label
        self._set_input_enabled(True)
        QMessageBox.warning(self, "Voice Input Error", f"Error: {error_message}")
        self.add_message("Bot", f"I had trouble understanding your voice: {error_message}")

    def _update_stt_status_label(self, status_text):
        """Updates the label with STT status (e.g., "Listening...", "Processing...")."""
        self.stt_status_label.setText(status_text)
        self.stt_status_label.show()


    def _handle_bot_response_complete(self, full_response_text):
        """Receives the complete bot response and updates the UI."""
        self._toggle_spinner(False) # Hide spinner
        self._set_input_enabled(True) # Re-enable input
        self.add_message("Bot", full_response_text) # Add the full message to history
        self.chat_history_display.verticalScrollBar().setValue(self.chat_history_display.verticalScrollBar().maximum())
        self.assistant_response_thread = None # Clear thread reference

    def _handle_assistant_thread_error(self, error_message):
        """Handles errors from the AssistantResponseThread."""
        self._toggle_spinner(False) # Hide spinner
        self._set_input_enabled(True) # Re-enable input
        QMessageBox.critical(self, "Assistant Error", f"An error occurred: {error_message}")
        self.add_message("Bot", f"An internal error occurred: {error_message}")
        self.assistant_response_thread = None # Clear thread reference

    def _toggle_spinner(self, show):
        """Controls visibility and animation of the spinner."""
        if show:
            self.spinner_label.show()
            if self.spinner_movie.isValid():
                self.spinner_movie.start()
        else:
            self.spinner_label.hide()
            if self.spinner_movie.isValid():
                self.spinner_movie.stop()


# --- Main Application Window ---
class MyPyQt5App(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AI Assistant Application")
        self.setGeometry(100, 100, 800, 600)

        screen_geometry = QApplication.desktop().screenGeometry()
        x = (screen_geometry.width() - self.width()) / 2
        y = (screen_geometry.height() - self.height()) / 2
        self.move(int(x), int(y))

        self.setContentsMargins(0, 0, 0, 0)
        self.setAutoFillBackground(True)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        self.welcome_screen = WelcomeScreen()
        self.chatbot_screen = ChatbotScreen()

        self.stacked_widget.addWidget(self.welcome_screen)
        self.stacked_widget.addWidget(self.chatbot_screen)

        self.welcome_screen.enter_clicked.connect(self._show_chatbot_screen)

        self.stacked_widget.setCurrentWidget(self.welcome_screen)

    def _show_chatbot_screen(self):
        self.stacked_widget.setCurrentWidget(self.chatbot_screen)

    def closeEvent(self, event):
        # Ensure STT thread is properly stopped when closing
        if self.chatbot_screen.stt_thread and self.chatbot_screen.stt_thread.isRunning():
            self.chatbot_screen.stt_thread.stop()
            self.chatbot_screen.stt_thread.quit()
            self.chatbot_screen.stt_thread.wait(2000)

        # Ensure assistant response thread is stopped
        if self.chatbot_screen.assistant_response_thread and self.chatbot_screen.assistant_response_thread.isRunning():
            # Since play() is blocking, we mainly ensure the thread is cleaned up.
            # No explicit 'stop' for this thread, it should finish its task quickly.
            self.chatbot_screen.assistant_response_thread.quit()
            self.chatbot_screen.assistant_response_thread.wait(2000)

        # Stop pyttsx3 engine
        if self.chatbot_screen.tts_engine_local:
            self.chatbot_screen.tts_engine_local.stop()

        event.accept()


# --- Main application entry point ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyPyQt5App()
    window.show()
    sys.exit(app.exec_())