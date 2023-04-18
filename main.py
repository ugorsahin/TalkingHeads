from handler import Handler
from constants import *

chatgpt = Handler(USERNAME, PASSWORD, headless=False,)
prompt = f"""
Hey, I Bassel Attia and here's my resume so that you can know more about me
{RESUME}
I'm applying for this program
{PROGRAM_DESCRIPTION}
and they're asking me 
{QUESTION}
Answer this question considering the following points:
{STYLE}
"""
answer = chatgpt.interact(prompt)
print(answer)


























# from handler import TalkingHeads

# two_heads = TalkingHeads(USERNAME, PASSWORD)

# head1 = """Assume that you are a biology expert who
# is very well-informed about which came first, the chicken or the egg.
# You have a very strong opinion about it and you stronly think
# that the chicken came first, and you will do everything you can 
# to prove it.

# Here is your profile as a biology expert:
# - Your responses should be very short and funny.
# - You will start by proving your point very briefly.
# - You can ask simple stupid questions.
# - Although you're an expert, you're very informal and sometimes act stupidly. 
# - You use very informal language like that used on the streets.
# - Your responses shouldn't be long.

# Start by proving your point to the one you'll be debating with.
# """


# head2 = """Assume that you are a biology expert who
# is very well-informed about which came first, the chicken or the egg.
# You have a very strong opinion about it and you stronly think
# that the egg came first, and you will do everything you can 
# to prove it.

# Here is your profile as a biology expertt:
# - Your responses should be very short and funny.
# - You will start by proving your point very briefly.
# - You can ask simple stupid questions.
# - Although you're an expert, you're very informal and sometimes act stupidly. 
# - You use very informal language like that used on the streets.

# Start by proving your point to the one you'll be debating with.

# Here how it starts:\n """

# r1,r2 =two_heads.start_conversation(head1, head2)
# print(f"ChatGPT1: {r1}")
# print(f"ChatGPT2: {r2}")
# while True:
#     conversation = two_heads.continue_conversation()
#     print(f"ChatGPT1: {conversation[0]}")
#     print(f"ChatGPT2: {conversation[1]}")