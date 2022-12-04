# ChatGPT_Selenium
A Headless Chrome interface to communicate with ChatGPT

A short class definition to deal with ChatGPT via your code.

You need to have Chrome installed in your Linux.

Here is how to quick start

```
from handler import Handler

chatgpt = Handler(YOUR_USERNAME, YOUR_PASSWORD)

answer = chatgpt.interact("Hello, how are you today")

print(answer)
```