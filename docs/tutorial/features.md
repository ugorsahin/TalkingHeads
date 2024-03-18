# Features

Features            | Claude | ChatGPT | Copilot | Gemini | LeChat | HuggingChat | Pi
--------------------|--------|---------|---------|--------|--------|-------------|----
Use without login   | ❌     | ❌      | ✅      | ❌     |  ❌    | ❌          | ✅ 
Login*              | ➖     | ✅      | ➖      | ➖     |  ✅    | ✅          | ➖ 
Interact            | ✅     | ✅      | ✅      | ✅     |  ✅    | ✅          | ✅ 
New Chat            | ✅     | ✅      | ✅      | ✅     |  ✅    | ✅          | ✅ 
Regenerate Response | ✅     | ✅      | ❌      | ✅     |  ❌    | ❌          | ❌ 
Custom Interactions | ❌     | ✅      | ❌      | ❌     |  ❌    | ❌          | ❌ 
Search Web          | ❌     | ❌      | ✅      | ❌     |  ❌    | ✅          | ❌ 
Plugins             | ❌     | ❌      | ✅      | ❌     |  ❌    | ❌          | ❌ 
Switch Model        | ❌     | ✅      | ✅**    | ❌     |  ✅    | ✅          | ✅ 
Multimodal (Visual)| ✅     | ➖***   | ✅      | ✅     |  ❌    | ❌          | ❌ 

✅ (Auto) Save the conversation as csv, h5, html, json, orc, pkl, xlsx, xml


* ✅ : Functionality exists and implemented
* ❌ : Functionality does not exist
* ➖ : Functionality exists but not implemented


\* You should use a user profile and login manually to use Gemini, Claude and Copilot.Please take a look at documentation and [Setup User Data Directory](getting_started.rst) to set up a user profile.

\*\* The modes of Copilot (Creative, Balanced and Precise) are accessible with model switch. However, it is unclear if they are different models.

\*\*\* ChatGPT has multimodality, but only for premium users, donate me a premium account if you need that to be implemented!
