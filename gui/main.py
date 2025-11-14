import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QMessageBox, QLineEdit,
    QTextBrowser, QStackedWidget
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread # QTimer is not strictly needed for non-streaming, but kept for general utility
from PyQt5.QtGui import QFont, QColor, QPalette, QMovie
from backend.assistant_core import GeminiAssistant

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
            "QPushButton:hover { background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #218838, stop:1 #388E3C); border: 2px solid #0D47A1; }"
            "QPushButton:pressed { background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1E7E34, stop:1 #2E7D32); padding-top: 22px; padding-bottom: 18px; }"
        )
        enter_button.setFixedSize(300, 80)
        enter_button.clicked.connect(self.enter_clicked.emit)
        layout.addWidget(enter_button, alignment=Qt.AlignCenter)

# --- QThread for API Calls (Non-Streaming) ---
class AssistantThread(QThread):
    response_complete = pyqtSignal(str) # Emits the final text response or error
    assistant_thinking = pyqtSignal(bool) # To show/hide spinner

    def __init__(self, assistant_instance, user_query):
        super().__init__()
        self.assistant = assistant_instance
        self.user_query = user_query

    def run(self):
        self.assistant_thinking.emit(True) # Show spinner
        try:
            # The send_prompt now yields a single (type, content) tuple
            for response_type, content in self.assistant.send_prompt(self.user_query):
                if response_type == "final_text":
                    self.response_complete.emit(content)
                elif response_type == "error":
                    self.response_complete.emit(f"Error: {content}") # Send error message through the same signal
        except Exception as e:
            self.response_complete.emit(f"An unexpected error occurred: {e}")
        finally:
            self.assistant_thinking.emit(False) # Hide spinner


class ChatbotScreen(QWidget):
    def __init__(self, parent=None):
        self.assistant = GeminiAssistant() # Initialize the assistant here
        super().__init__(parent)
        self.initUI()

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

        # Initial static bot message
        self.add_message("Bot", "Hello! I'm your AI assistant. How can I help you today?")

        self.spinner_label = QLabel()
        self.spinner_movie = QMovie("spinn1.gif")
        if self.spinner_movie.isValid():
            self.spinner_label.setMovie(self.spinner_movie)
            self.spinner_label.setFixedSize(32, 32)
            self.spinner_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.spinner_label.setStyleSheet("padding-left: 10px; margin-bottom: 8px;")
            self.spinner_label.hide() # Initially hidden
        else:
            print("Error: Could not load spinner.gif. Make sure it's in the correct path.")
            self.spinner_label.setText("Thinking...")
            self.spinner_label.setStyleSheet("color: #FFA500; font-style: italic; padding-left: 10px; margin-bottom: 8px;")

        spinner_layout = QHBoxLayout()
        spinner_layout.addWidget(self.spinner_label)
        spinner_layout.addStretch()
        main_layout.addLayout(spinner_layout)

        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)

        self.user_input_field = QLineEdit()
        self.user_input_field.setPlaceholderText("Type your message here...")
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
        input_layout.addWidget(self.user_input_field)

        self.send_button = QPushButton("Send") # Changed to self.send_button for consistency
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
        input_layout.addWidget(self.send_button)

        main_layout.addLayout(input_layout)

    def add_message(self, sender, message):
        if sender == "User":
            color = "#90CAF9"
            align = Qt.AlignRight
            background = "#4A4A4A"
        else: # Bot
            color = "#A5D6A7"
            align = Qt.AlignLeft
            background = "#3A3A3A"

        formatted_message = f'''
        <div class="chat-message" style="background-color: {background}; border-radius: 10px; padding: 8px 12px; margin-bottom: 8px; max-width: 80%; float: {["left", "right"][align == Qt.AlignRight]}; clear: both;">
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

            # Disable input and show spinner while waiting for response
            self.user_input_field.setEnabled(False)
            self.send_button.setEnabled(False)
            self._toggle_spinner(True)

            # Create and start the thread for API call
            self.assistant_thread = AssistantThread(self.assistant, user_message)
            self.assistant_thread.response_complete.connect(self._handle_bot_response)
            self.assistant_thread.assistant_thinking.connect(self._toggle_spinner) # Connect to toggle spinner
            self.assistant_thread.start()
        else:
            QMessageBox.warning(self, "Empty Message", "Please type a message before sending.")

    def _handle_bot_response(self, bot_reply):
        # Enable input and hide spinner
        self.user_input_field.setEnabled(True)
        self.send_button.setEnabled(True)
        self._toggle_spinner(False) # Ensure spinner is hidden

        self.add_message("Bot", bot_reply)
        self.chat_history_display.verticalScrollBar().setValue(self.chat_history_display.verticalScrollBar().maximum())

    def _toggle_spinner(self, show):
        if show:
            self.spinner_label.show()
            if self.spinner_movie.isValid():
                self.spinner_movie.start()
        else:
            self.spinner_label.hide()
            if self.spinner_movie.isValid():
                self.spinner_movie.stop()


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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyPyQt5App()
    window.show()
    sys.exit(app.exec_())