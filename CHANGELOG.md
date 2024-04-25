## 0.6.1 (2024-04-25)

### Fix

- **BaseBrowser**: remove self.browser.close() that case error in Macos


## 0.6.0 (2024-04-24)
### Feat

- **ChatGPTClient**: Now can use ChatGPT 3.5 without login or credential provided.
- **ChatGPTClient**: Now ChatGPT 4.0 model works well.
  
### Fix

- **ChatGPTClient**: adapt to the new ChatGPT website UI
- **ChatGPTClient**: Deprecated login method, added manual pass verification page and login to get profile like gemini
- **ChatGPTClient**: Fix switch_model xpath bugs
- **GeminiClient**: Fix xpath bugs now can get respond correctly


## 0.5.0 (2024-03-18)

### Feat

- **is_url_check_filetype**: new functions to check filetype and if the string is url
- **lechat**: Mistral Le Chat is automated
- **gemini_multimodal**: It is possible to upload image to Gemini
- **image**: Implementation of image upload feature
- **multiagent**: First commit of Multiagent subpackage including Conversation
- **reset_thread**: now it is possible to reset chat, disabled model switch

### Fix

- **import**: Changed init file
- **logging**: import logging removed
- **object_markers**: Fixed old markers and new file format
- **init**: Initialization fixes
- **logging_and_driver_arguments**: It is now possible to pass driver arguments as dictionary
- **logging_interacting**: Logging changed to instance based logger and fixed a bug in interaction
- **claude**: Fixed a response error
- **logging**: uses it's own logging
