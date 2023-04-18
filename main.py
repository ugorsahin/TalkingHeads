from handler import Handler
from constants import *
from ai_detector import AIDetector

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
# chatgpt = Handler(USERNAME, PASSWORD, headless=False,)
# answer = chatgpt.interact(prompt)
# chatgpt.delete_current_conversation()
# print(answer)
answer = """Hey there!
I am really excited about the opportunity to participate in the Youth Summer Fest in Timisoara, Romania as a volunteer in the Media and Promotion team. The idea of being part of such a vibrant and culturally rich festival in the European Capital of Culture for 2023 is truly thrilling!
As someone with a background in computer engineering and mobile app development, I believe that my technical skills, particularly in media and content creation, would be valuable in contributing to the festival's promotional activities. I am confident in my ability to take photos and videos, write articles, and create engaging content for online promotion. Moreover, I am fluent in Arabic, English, and German, which could be an asset in communicating with a diverse team of international volunteers and promoting the festival to a wider audience.
Aside from my technical skills, I am also passionate about youth empowerment and community engagement. I have previous experience in volunteering and organizing events for children and young people, which has honed my leadership and communication skills. I am eager to learn more about how festivals are organized and gain hands-on experience in facilitating activities during the festival.
Furthermore, I am excited about the opportunity to share my own culture and learn about other cultures through the intercultural evenings that are part of the volunteering project. I believe that cultural exchange is a powerful way to foster understanding and create meaningful connections among people from different backgrounds.
Overall, I am looking forward to being part of a dynamic and enthusiastic team of international volunteers, and I am confident that this experience will not only allow me to contribute to the success of the Youth Summer Fest, but also provide me with valuable skills, knowledge, and unforgettable memories. Can't wait to be a part of this amazing project!
Cheers,
Bassel"""
ai_detector = AIDetector()
print(ai_detector.get_AI_percentage(answer))


























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