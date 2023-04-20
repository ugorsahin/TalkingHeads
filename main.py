# -*- coding: utf-8 -*-
from handler import Handler
from constants import *
from ai_detector import AIDetector
import threading
from handler import TalkingHeads, RequestLimitExceeded
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from handler import Handler
from config import *
app = FastAPI()
templates = Jinja2Templates(directory="templates/")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.post("/chat", response_class=HTMLResponse)
async def chat(request: Request):
    try:
        two_heads = TalkingHeads(USERNAME, PASSWORD)
        form_data = await request.form()
        answer1, answer2 = two_heads.start_conversation(form_data['gpt1'], form_data['gpt2'])
        chat = [f"GPT1: {answer1}\n"]
        chat.append( f"GPT2: {answer2}\n")
        for i in range(3):
            answer1, answer2 = two_heads.continue_conversation()
            chat.append(f"GPT1: {answer1}\n")
            chat.append(f"GPT2: {answer2}\n")
        two_heads.delete_all_conversations()
        two_heads.driver.close_webdriver()
        return templates.TemplateResponse("chat.html", {"request": request, "chat": chat})    
    except RequestLimitExceeded:
        print("Too many requests were made in 1 hour. Please try again later.")

# try:
#     two_heads = TalkingHeads(USERNAME, PASSWORD)
#     r1,r2 = two_heads.start_conversation('hi' , 'act very rude to anything you get')
#     print(r1)
#     print(r2)
#     for i in range(2):
#         print(i)
#         r1, r2 = two_heads.continue_conversation()
#         print(r1)
#         print(r2)
#     two_heads.delete_all_conversations()
# except RequestLimitExceeded:
#     print("Too many requests were made in 1 hour. Please try again later.")