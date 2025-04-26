# Smart Mirror

The **Smart Mirror** is a Python-based application designed to transform a standard mirror into an interactive and intelligent display. It is specifically designed for use with the **Hailo 8L AI Module** and **Raspberry Pi 5**, leveraging their powerful capabilities for efficient edge AI processing. The Smart Mirror also features **facial detection and recognition** to provide a personalized and interactive user experience.

## Features
- **Weather Updates**: Displays current weather conditions and forecasts.
- **Calendar Integration(Coming Soon)**: Syncs with your calendar to show upcoming events.
- **News Headlines (Coming Soon)**: Keeps you informed with the latest news updates.
- **Facial Detection and Recognition**: Identifies users and provides personalized information such as tailored greetings, reminders, and preferences.
- **Modular Design**: Easily add or customize modules for personalized functionality.
- **Voice Commands (Pending Whisper Hailo8l release)**: Interact with the mirror using voice recognition (if implemented).
- **Optimized for Hailo 8L**: Enhanced AI performance for real-time applications (Degirum API Key required).
- **Raspberry Pi 5 Support**: Lightweight and efficient, compatible with the latest Raspberry Pi hardware.
- 
## Demo of Real-Time Recognition (Covering and Un-Covering Face)
![Untitled video](https://github.com/user-attachments/assets/4e214729-3cf0-420c-9e10-e359da51cfa7)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/mattm0127/smart_mirror.git
   ```
2. Navigate to the project directory:
   ```bash
   cd smart_mirror
   ```
3. Install the required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python main.py
   ```

## Hardware Requirements
To use this application effectively, ensure you have the following:
- A **Hailo 8L AI Module** for AI processing.
- A **Raspberry Pi 5** as the main computing device.
- A compatible monitor or display, ideally integrated with a two-way mirror.
- A camera module for facial detection and recognition.

## Facial Detection and Recognition
This application includes facial detection and recognition features, which enable the Smart Mirror to:
- Detect users in front of the mirror using advanced AI models.
- Recognize individual users and adapt its functionality to their preferences.
- Display personalized information and greetings based on the recognized user.

The facial detection and recognition capabilities are powered by the integration of the Hailo 8L AI Module, providing high performance and accuracy for real-time processing.

## Usage
After starting the application, the Smart Mirror will display the modules you have configured. Facial recognition will automatically activate when a user is detected by the camera. You can customize the layout, add new features, or modify existing ones by editing the Python modules.

## Contributing
Contributions are welcome! Feel free to fork this repository, create a new branch, and submit a pull request with your improvements.

## License
This project is licensed under the [MIT License](LICENSE).

## Acknowledgments
- Inspired by other smart mirror projects and the open-source community.
- Special thanks to Hailo and Raspberry Pi for their excellent hardware solutions.
