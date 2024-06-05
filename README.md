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
    <img src="https://img.shields.io/codecov/c/github/ugorsahin/talkingheads"/> 
  </a>
  <a href="https://github.com/astral-sh/ruff"><img alt="Code style: black" src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json"></a>
</p>

Welcome to TalkingHeads! 💬

TalkingHeads is a Python library that serves as an interface for seamless communication with ChatGPT, Claude, Copilot, Gemini, LeChat, HuggingChat, and Pi  🤖

By leveraging the power of browser automation, this library enables users to effortlessly interact with online chat agents 🚀✨

You can utilize more than one agent by using multiagent module, and improve your workflow with an ensemble of models!

# Prerequisites 📋

- Install Chrome
- Register to the provider you would like to use (or not, and use Pi!)

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

response = chathead.interact("Hello, how are you today")

print(response)
```

## Features
Features            | Claude | ChatGPT | Copilot | Gemini | LeChat | HuggingChat | Pi |
|-------------------|--------|---------|---------|--------|--------|-------------|----|
Use without login   | ❌     | ❌      | ✅      | ❌     |  ❌    | ❌          | ✅ |
Login*              | ➖     | ✅      | ➖      | ➖     |  ✅    | ✅          | ➖ |
Interact            | ✅     | ✅      | ✅      | ✅     |  ✅    | ✅          | ✅ |
New Chat            | ✅     | ✅      | ✅      | ✅     |  ✅    | ✅          | ✅ |
Regenerate Response | ✅     | ✅      | ❌      | ✅     |  ❌    | ❌          | ❌ |
Custom Interactions | ❌     | ✅      | ❌      | ❌     |  ❌    | ❌          | ❌ |
Search Web          | ❌     | ❌      | ✅      | ❌     |  ❌    | ✅          | ❌ |
Plugins             | ❌     | ❌      | ✅      | ❌     |  ❌    | ❌          | ❌ |
Switch Model        | ❌     | ✅      | ✅**    | ❌     |  ✅    | ✅          | ✅ |
Multimodal (Visual) | ✅     | ➖***   | ✅      | ✅     |  ❌    | ❌          | ❌ |

✅ (Auto) Save the conversation as csv, h5, html, json, orc, pkl, xlsx, xml

- ✅ : Functionality exists and implemented
- ❌ : Functionality does not exist
- ➖ : Fuctionality exists but not implemented

\* You should use a user profile and login manually to use Gemini, Claude and Copilot.Please take a look at documentation and [FAQ](FAQ.md) to set up a user profile.

\*\* The modes of Copilot (Creative, Balanced and Precise) are accessible with model switch. However, it is unclear if they are different models.

\*\*\* ChatGPT has multimodality, but only for premium users, donate me a premium account if you need that to be implemented!

## Issues & Contribution

Feel free to dive in, share your knowledge, and collaborate. I would be happy to answer any questions or accept your contributions. Let me know in issues if you need anything.

Enhancing our documentation would be fantastic and appreciated. Help me improve documentation with your valuable contributions.
Please indicate your issue with a tag enclosed by square brackets: [FEATURE], [BUG], [DOCUMENTATION], [QUESTION]. If you don't know what to write you can write [MISC]. I will prioritize issues with tags.

## Where is old ChatGPT_Automation library?

You can still run your code to connect ChatGPT, follow the below tutorial

```bash
export ChatGPT_UNAME=<your@email>
export ChatGPT_PWD=><password>
```
```python
from talkingheads import ChatGPTClient

chathead = ChatGPTClient()

response = chathead.interact("Hello, how are you today")

print(response)
```
