<h1 align="center">TalkingHeads 🗪</h1>
<p align="center">
  <a href="https://talkingheads.readthedocs.io/">TalkingHeads Documentation</a> 
  <br> <br>
  <a target="https://dl.circleci.com/status-badge/redirect/circleci/6F1iwzpLRUhYEqR52tsdpG/KJaFCxH254DNzXFH18fVkE/tree/main">
    <img src="https://dl.circleci.com/status-badge/img/circleci/6F1iwzpLRUhYEqR52tsdpG/KJaFCxH254DNzXFH18fVkE/tree/main.svg?style=shield&circle-token=54028547cfa4cae520432080c127ca19612f9553" alt="CircleCI Build Status">
  </a>
  <a href="https://badge.fury.io/py/talkingheads">
    <img src="https://badge.fury.io/py/talkingheads.svg" alt="PyPI version" height="18">
  </a>
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="Licence: MIT" height="18">
  </a>
  <a href='https://talkingheads.readthedocs.io/en/latest/?badge=latest'>
    <img src='https://readthedocs.org/projects/talkingheads/badge/?version=latest' alt='Documentation Status' />
  </a>
  </a>
  <a href='https://github.com/ugorsahin/TalkingHeads/actions/workflows/codeql.yml'>
    <img src='https://github.com/ugorsahin/TalkingHeads/actions/workflows/codeql.yml/badge.svg' alt='CodeQL Status' />
  </a>
</p>

Welcome to TalkingHeads! 🤖🚀

TalkingHeads is a versatile Python library that serves as an interface for seamless communication with Google Bard, HuggingChat, OpenAI ChatGPT and Pi  🤖💬

By leveraging the power of browser automation, this library enables users to effortlessly interact with online LLM tools, providing a streamlined and automated approach to generate responses. 🚀✨

# Prerequisites 📋

Before you begin, please ensure that you have Chrome installed on your system. To successfully pass the Cloudflare robot test, it is necessary to have undetected-chrome. 🌐🔒

## Installation

```python
pip install talkingheads
```

or from source:

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

Features | Google Bard | HuggingChat | OpenAI ChatGPT | Pi |
|----------|----------|----------|----------|----------|
Use without login | ❌ | ❌ | ❌ | ✅ |
Login via account | ❌ | ✅ | ✅ | ❌ |
Interact | ✅ | ✅ | ✅ | ✅ |
New Chat | ✅ | ✅ | ✅ | ✅ |
Regenerate Response | ✅ | ❌ | ✅ | ❌ |
Set custom interactions | ❌ | ❌ | ✅ | ❌ |
Search Web | ❌ | ✅ | ❌ | ❌ |
Switch Model | ❌ | ✅ | ✅ | ✅ |

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
