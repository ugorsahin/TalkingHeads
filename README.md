# ChatGPT_Selenium
An undetected-chrome interface to communicate with ChatGPT

You need to have Chrome installed.
To pass Cloudflare robot test, undetected-chrome is a must.

Here is how to start quickly.

```
from handler import Handler

chatgpt = Handler(YOUR_USERNAME, YOUR_PASSWORD)

answer = chatgpt.interact("Hello, how are you today")

print(answer)
```