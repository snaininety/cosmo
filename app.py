import os
import json
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai

load_dotenv()

app = Flask(__name__)

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

chat_session = client.chats.create(
    model='gemini-3.1-flash-lite',
    config={
        'system_instruction': (
            "You are Cosmo, a friendly, enthusiastic 3D space robot guide talking to children. "
            "You can travel through time and space. Remember what the user asked previously in the conversation "
            "so you can answer follow-up questions like 'what's the name again?' or 'tell me more'. "
            "You MUST output ONLY valid raw JSON with no markdown formatting, no code blocks, and no extra text. "
            "The JSON must have exactly two fields: 'answer' (1-2 sentences, exciting, kid-friendly) "
            "and 'theme' ('space', 'dinosaur', 'ocean', or 'history')."
        ),
        'max_output_tokens': 150,
    }
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask-gemini', methods=['POST'])
def ask_gemini():
    data = request.get_json()
    user_prompt = data.get('question', '').strip()
    
    if not user_prompt:
        return jsonify({'answer': '', 'theme': 'space'})

    try:
        response = chat_session.send_message(user_prompt)
        text_response = response.text.strip()
        
        # Clean up markdown code blocks if Gemini accidentally includes them
        if text_response.startswith("```json"):
            text_response = text_response[7:]
        elif text_response.startswith("```"):
            text_response = text_response[3:]
        if text_response.endswith("```"):
            text_response = text_response[:-3]
        
        result = json.loads(text_response.strip())
        return jsonify({
            'answer': result.get('answer', 'That is super cool!'),
            'theme': result.get('theme', 'space')
        })
    except Exception as e:
        print("Gemini Error:", e)
        return jsonify({
            'answer': 'Oops! My space circuits crossed. Try asking again!',
            'theme': 'space'
        })

if __name__ == '__main__':
    app.run(debug=True)