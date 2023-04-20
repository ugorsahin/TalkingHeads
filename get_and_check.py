from handler import Handler
from constants import *
from ai_detector import AIDetector
import threading

prompt = f"""
I'm applying for this program
{PROGRAM_DESCRIPTION}
and they're asking me 
{QUESTION}
Answer this question considering the following points:
{STYLE}
And here's my resume so that you can know more about me
{RESUME}
"""

ai_detector = None
chatgpt = None
answer = None

def get_answer():
    global chatgpt
    chatgpt = Handler(USERNAME, PASSWORD, headless=False,)
    global answer
    chatgpt.interact(WRITING_FACTORS_TO_CONSIDER)
    answer = chatgpt.interact(prompt)

def detect_AI():
    global ai_detector
    ai_detector = AIDetector()

# Create two threads, one for each action
answer_thread = threading.Thread(target=get_answer)
detection_thread = threading.Thread(target=detect_AI)

# Start the threads
answer_thread.start()
detection_thread.start()

# Wait for the threads to finish
answer_thread.join()
detection_thread.join()

percentage = ai_detector.get_AI_percentage(answer)
chatgpt.delete_current_conversation()
print(answer)
print(percentage)