🤖 SpaCy Telegram Chatbot
📌 Overview
This is a NLP-powered chatbot built using SpaCy and integrated with Telegram via the Telegram Bot API. It processes user messages, determines sentence types, and generates appropriate responses using natural language processing techniques.

✨ Features
🧠 Uses SpaCy for sentence parsing and processing
📢 Supports WH-questions, Yes/No questions, instructions, and wishes
🔀 Handles POV transformations to make responses more natural
🔧 Built with Python, Telegram Bot API, and regex-based matching
💬 Can recognize different sentence structures and respond accordingly
🛠️ Technologies Used
Python
SpaCy (for NLP)
Telegram Bot API
Regular Expressions (Regex)
Logging & Debugging Tools
📦 Installation
Prerequisites
Ensure you have Python 3.7+ installed.

Steps
Clone this repository:
sh
Copy
Edit
git clone https://github.com/ItsMakha/SpacyChatBot.git
cd SpacyChatBot
Install dependencies:
sh
Copy
Edit
pip install SpacyChatBo
python -m spacy download en_core_web_sm
Set up your Telegram bot by replacing token in the script with your actual bot token.
Run the bot:
sh
Copy
Edit
python chatbot.py  
Start chatting with your bot on Telegram! 🚀
🚀 How It Works
The bot listens for user messages via Telegram.
It uses SpaCy to analyze sentence structure.
Based on detected patterns, it classifies the sentence as:
WH-Question 🤔
Yes/No Question ✅❌
Instruction 📢
Wish ✨
Generic Statement 📝
It generates an appropriate response and sends it back via Telegram.

🔧 Future Enhancements
Add custom responses for more engaging conversations
Integrate with external APIs for dynamic information retrieval
Improve context awareness to hold longer conversations
Deploy the bot on a cloud server for 24/7 availability
🤝 Contribution
