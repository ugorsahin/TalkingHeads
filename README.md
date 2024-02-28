<h1 align="center">TalkingHeads 💬</h1>
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
  <a href="https://pepy.tech/project/talkingheads"><img src="https://static.pepy.tech/badge/talkingheads"></a>
  </a>
  <a href='https://github.com/ugorsahin/TalkingHeads/actions/workflows/codeql.yml'>
    <img src='https://github.com/ugorsahin/TalkingHeads/actions/workflows/codeql.yml/badge.svg' alt='CodeQL Status' />
  </a>
  <a href="https://codecov.io/gh/ugorsahin/TalkingHeads" > 
    <img src="https://codecov.io/gh/ugorsahin/TalkingHeads/graph/badge.svg?token=YPXKNXSZAD"/> 
  </a>
  <a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
</p>

Welcome to TalkingHeads! 💬

TalkingHeads is a versatile Python library that serves as an interface for seamless communication with ChatGPT, Claude, Copilot, Gemini, HuggingChat, and Pi  🤖

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
from talkingheads import PiClient

chathead = PiClient()

answer = chathead.interact("Hello, how are you today")

print(answer)
```

## Features

Features | Gemini | Claude | Copilot | HuggingChat | ChatGPT | Pi |
|--------|------|--------|---------|-------------|---------|----|
Use without login | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ |
Login* | ➖ | ➖ | ➖ | ✅ | ✅ | ➖ |
Interact | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
New Chat | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
Regenerate Response | ✅ | ✅ | ❌  | ❌ | ✅ | ❌ |
Set custom interactions | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
Search Web | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ |
Plugins | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
Switch Model | ❌ | ❌ | ✅** | ✅ | ✅ | ✅ |

✅ (Auto) Save the conversation as csv, h5, html, json, orc, pkl, xlsx, xml

- ✅ : Functionality exists and implemented
- ❌ : Functionality does not exist
- ➖ : Fuctionality exists but not implemented

\* The first time login is manually done for Gemini, Claude and Copilot. Check documentation for first time setup. Please take a look at [FAQ](FAQ.md) to set up.
\*\* The modes of Copilot (Creative, Balanced and Precise) are accessible with model switch. However, it is unclear if they are different models.

## Issues & Contribution

Feel free to dive in, share your knowledge, and collaborate. I would be happy to answer any questions or accept your contributions. Let me know in issues if you need anything.

Enhancing our documentation would be fantastic and appreciated. Help me improve documentation with your valuable contributions.
Please indicate your issue with a tag enclosed by square brackets: [FEATURE], [BUG], [DOCUMENTATION], [QUESTION]. If you don't know what to write you can write [MISC]. I will prioritize issues with tags.

## Where is old ChatGPT_Automation library?

You can still run your code to connect ChatGPT, follow the below tutorial

```bash
export OPENAI_UNAME=<your@email>
export OPENAI_PWD=><password>
```
```python
from talkingheads import ChatGPTClient

chathead = ChatGPTClient()

answer = chathead.interact("Hello, how are you today")

print(answer)
```
