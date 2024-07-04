from flask import Flask, render_template, request, jsonify
import openai
import speech_recognition as sr
import pyttsx3
from deep_translator import GoogleTranslator
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain_openai import ChatOpenAI
import logging

# Initialize logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Replace 'your_openai_api_key' with your actual OpenAI API key
openai.api_key = ''

class ChatBot:
    def __init__(self):
        self.input_prompt = """
            Welcome to the Pet Care ChatBot. Ask any questions related to pet care and pets!
            """
        self.memory = ConversationBufferMemory()
        self.openai_llm = ChatOpenAI(api_key=openai.api_key)
        self.conversation_chain = ConversationChain(llm=self.openai_llm, memory=self.memory)

    def translate_text(self, text, target_language):
        translated_text = GoogleTranslator(source='auto', target=target_language).translate(text)
        return translated_text

    def chat(self, msg, target_lang='en'):
        logging.debug(f"Original message: {msg}")
        if target_lang != 'en':
            msg = self.translate_text(msg, 'en')  # Translate to English for processing
            logging.debug(f"Translated message to English: {msg}")

        response = self.invoke(input=self.input_prompt + "\n" + msg)
        logging.debug(f"Response from OpenAI: {response}")

        if target_lang != 'en':
            response['response'] = self.translate_text(response['response'], target_lang)  # Translate response back to target language
            logging.debug(f"Translated response to target language: {response['response']}")

        return jsonify(response)

    def invoke(self, input):
        response = self.conversation_chain.invoke(input=input)
        return response

    def voice_to_text(self):
        try:
            recognizer = sr.Recognizer()
            microphone = sr.Microphone()
        except AttributeError:
            logging.error("PyAudio not found.")
            return None

        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
            logging.debug("Say something!")
            audio = recognizer.listen(source)

        try:
            text = recognizer.recognize_google(audio)
            logging.debug(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            logging.error("Could not understand audio")
            return None
        except sr.RequestError as e:
            logging.error(f"Error fetching results from Google Speech Recognition service: {e}")
            return None

    def text_to_speech(self, text):
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

chatbot = ChatBot()

@app.route("/")
def index():
    return render_template('chat.html')

@app.route("/get", methods=["POST"])
def chat():
    msg = request.form["msg"]
    target_lang = request.form.get("lang", "en")  # Default to English if lang parameter is not provided
    response = chatbot.chat(msg, target_lang)
    return response

@app.route("/voice", methods=["POST"])
def voice():
    text = chatbot.voice_to_text()
    if text:
        target_lang = request.form.get("lang", "en")  # Default to English if lang parameter is not provided
        response = chatbot.chat(text, target_lang)
        return response
    else:
        return jsonify({"response": "Could not understand audio."})

if __name__ == '__main__':
    app.run(debug=True, port=8000)
