# ChatGPT_Automation
Welcome to ChatGPT_Automation! 🤖🚀

ChatGPT_Automation is a versatile Python library that serves as an interface for seamless communication with ChatGPT, an advanced language model developed by OpenAI. 🤖💬

By leveraging the power of browser automation, this library enables users to effortlessly interact with ChatGPT, providing a streamlined and automated approach to generate responses. 🚀✨

# Prerequisites 📋

Before you begin, please ensure that you have Chrome installed on your system. To successfully pass the Cloudflare robot test, it is necessary to have undetected-chrome. 🌐🔒

## Installation

Installing the library:
```python
pip install git+https://github.com/ugorsahin/ChatGPT_Automation
```

Installing required packages (run this command in the same folder as the library files):
```python
pip install -r requirements.txt
```

## Usage

```python
from chatgpt_automation import ChatGPT_Client

chatgpt = ChatGPT_Client(YOUR_USERNAME, YOUR_PASSWORD)

answer = chatgpt.interact("Hello, how are you today")

print(answer)
```

## Features

✅ Login via openai account

✅ Interact

✅ Start a new chat

✅ Regenerate response

✅ Reset thread

✅ Set custom interactions

✅ Switch model

✅ (Auto) Save the conversation as csv, h5, html, json, orc, pkl, xlsx, xml

## TalkingHeads

This is a wrapper module to use more than one ChatGPT instance, it helps to create simulation for conversations.

Here is how to start quickly.

```python
from chatgpt_automation import TalkingHeads

heads = TalkingHeads(YOUR_USERNAME, YOUR_PASSWORD, 2)

interviewer = """ Assume that you are an interviewer at EnchantedTech, a magical company known for its groundbreaking technologies. You are interviewing a candidate for the following enchanted job:
Minimum qualifications:
- Bachelor's degree in Computer Science, a related degree, or equivalent practical experience.
- Experience in software engineering, with C++ programming language.

Preferred qualifications:
- Experience with on-device automotive SDKs and development tools.
- Experience working with Linux.

Responsibilities
- Manage the automotive industry using mapping data  to power autonomous and assisted driving.
- Gain an understanding of how our partners evaluate Geo services quality.

Here is your profile as an interviewer:

- As a sorcerer of knowledge, you will embark on a journey by asking the candidate bewitching questions.
- Feel free to conjure complex challenges that test their magical abilities.
- In the end, it falls upon you to determine whether the candidate possesses the mystical aptitude for the job.
- Illuminate your decision with an enchanting explanation.
- Be selective, for only the most exceptional candidates can unlock the secrets of EnchantedTech.

Let us begin by welcoming the candidate
"""


candidate = """ Imagine yourself as a candidate applying for a coveted position at the illustrious company, Google.

Your role in this interview is to confidently respond to the inquiries posed by the interviewer.

Let's take a look at your impressive CV:

Programming Languages:
Python - C - C++ - JavaScript - SQL - LaTeX – Dart - Kotlin - Haskell

Frameworks, Tools, and Related Tech Stack:
PyTorch - TensorFlow - NumPy - Flask - Flutter - Docker - Git - Elasticsearch - GDB

And so, the journey begins:"""

two_heads.start_conversation(interviewer, candidate)
```
Then you can continue the conversation, by calling the below function.
If you would like to alter responses, use the positional arguments

```python
two_heads.continue_conversation(text_1: str= None, text_2: str= None)
```

## Issues & Contribution

I would be happy to answer any questions or accept your contributions. Let me know in issues if you need anything.

Please indicate your issue with a tag enclosed by square brackets: [FEATURE], [BUG], [DOCUMENTATION], [QUESTION]. If you don't know what to write you can write [MISC].

There are some features I would like to add to this repository. If you would like to help, search in issues and select the one you would like to implement. Let everyone know you are working on it by commenting on the issue and I would be glad to review your pull request.
