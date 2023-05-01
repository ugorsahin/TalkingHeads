# ChatGPT_Automation
An undetected-chrome interface to communicate with ChatGPT

You need to have Chrome installed.
To pass Cloudflare robot test, undetected-chrome is a must.

Here is how to start quickly.

## Installation

```
git clone https://github.com/ugorsahin/ChatGPT_Automation
cd ChatGPT_Automation
pip setup .
```

## Usage

```
from chatgpt_automation import ChatGPT_Client

chatgpt = Handler(YOUR_USERNAME, YOUR_PASSWORD)

answer = chatgpt.interact("Hello, how are you today")

print(answer)
```

## TalkingHeads

This is a wrapper module to use more than one ChatGPT instance, it helps to create simulation for conversations.

Here is how to start quickly.

```
from chatgpt_automation import TalkingHeads

heads = TalkingHeads(YOUR_USERNAME, YOUR_PASSWORD, 2)

interviewer = """Assume that you are an interviewer at Google.\
 You are interviewing a candidate for the following job:
Minimum qualifications:
- Bachelor's degree in Computer Science, a related degree, or equivalent practical experience.
- Experience in software engineering, with C++ programming language.

Preferred qualifications:
- Experience with on-device automotive SDKs and development tools.
- Experience working with Linux.

Responsibilities
- Manage the automotive industry uses mapping data  to power autonomous and assisted driving.
- Gain an understanding of how our partners evaluate Geo services quality.

Here is your profile as an interviewer:
- You will start by asking questions to the candidate.
- You can ask complex questions.
- At the end, decide whether the candidate is a fit for the job.
- Explain you decision at the end.
- Be picky

Start by welcoming the interviewer.
"""


candidate = """Assume that you are a candidate for a position at Google.

You will answer the questions of the interviewer. 

Below is your CV:\n
Programming Languages
Python - C - C++ - JavaScript - SQL - LaTeX – Dart - Kotlin - Haskell

Frameworks, Tools and Related Tech Stack
PyTorch - Tensorflow - Numpy - Flask - Flutter - Docker - Git - Elasticsearch - GDB

Here how it starts:\n """

two_heads.start_conversation(interviewer, candidate)
```
Then you can continue to the conversation, call below function.
If you would like to alter responses, use the positional arguments

```
two_heads.continue_conversation(text_1: str= None, text_2: str= None)
```

## Issues & Contribution

I would be happy to answer any questions or accept your contributions. Let me know in issues if you need anything..
