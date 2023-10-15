# TalkingHeads
Welcome to TalkingHeads! 🤖🚀

TalkingHeads is a versatile Python library that serves as an interface for seamless communication with Google Bard, HuggingChat and OpenAI ChatGPT 🤖💬

By leveraging the power of browser automation, this library enables users to effortlessly interact with online LLM tools, providing a streamlined and automated approach to generate responses. 🚀✨

# Prerequisites 📋

Before you begin, please ensure that you have Chrome installed on your system. To successfully pass the Cloudflare robot test, it is necessary to have undetected-chrome. 🌐🔒

## Installation

```python
pip install git+https://github.com/ugorsahin/TalkingHeads
```

## Usage

```python
from talkingheads import HuggingChatClient

chathead = HuggingChatClient(YOUR_USERNAME, YOUR_PASSWORD)

answer = chathead.interact("Hello, how are you today")

print(answer)
```

## Features

Features | Google Bard | HuggingChat | OpenAI ChatGPT |
|----------|----------|----------|----------|
Login via account | ❌ | ✅ | ✅ |
Interact | ✅ | ✅ | ✅ |
New Chat | ✅ | ✅ | ✅ |
Regenerate Response | ✅ | ❌ | ✅ |
Set custom interactions | ❌ | ❌ | ✅ |
Search Web | ❌ | ✅ | ❌ |
Switch Model | ❌ | ✅ | ✅ |

✅ (Auto) Save the conversation as csv, h5, html, json, orc, pkl, xlsx, xml

Please take a look at [FAQ](FAQ.md) to set up Bard.

## Further Features to implement

- [ ] Bard modify response
- [ ] Bard double check

## Issues & Contribution

I would be happy to answer any questions or accept your contributions. Let me know in issues if you need anything.

Please indicate your issue with a tag enclosed by square brackets: [FEATURE], [BUG], [DOCUMENTATION], [QUESTION]. If you don't know what to write you can write [MISC].

There are some features I would like to add to this repository. If you would like to help, search in issues and select the one you would like to implement. Let everyone know you are working on it by commenting on the issue and I would be glad to review your pull request.

## Where is old ChatGPT_Automation library?

You can still run your code to connect ChatGPT, follow the below tutorial


```python
from talkingheads import ChatGPTClient

chathead = ChatGPTClient(YOUR_USERNAME, YOUR_PASSWORD)

answer = chathead.interact("Hello, how are you today")

print(answer)
```