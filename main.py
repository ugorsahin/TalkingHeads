# -*- coding: utf-8 -*-
from handler import Handler
from handler import TalkingHeads, RequestLimitExceeded
from config import *

try:
    two_heads = TalkingHeads(USERNAME, PASSWORD, headless=True)
    r1,r2 = two_heads.start_conversation('From now on, you are a superhero who is trying to convince me (a villain) not to destroy the world. Keep your answers short.' , 'From now on, you are a villain who wants to take over the world, and you will be talking to me, a superhero who is trying to convince you that this is bad. Keep your answers short. Here is how it starts:')
    num_replies = 1
    for i in range(num_replies+1):
        print(f"Chat GPT1:{r1}")
        print('-'*100)
        print(f"Chat GPT2:{r2}")
        print('-'*100)
        if i != num_replies:
            r1, r2 = two_heads.continue_conversation()
    two_heads.delete_all_conversations()
except RequestLimitExceeded:
    print("Too many requests were made in 1 hour. Please try again later.")