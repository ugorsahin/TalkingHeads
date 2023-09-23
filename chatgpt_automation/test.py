from chatgpt_client import ChatGPT_Client

client = ChatGPT_Client(username="", password="", verbose=True, headless=False)
res = client.interact("Hello!")
print(res)