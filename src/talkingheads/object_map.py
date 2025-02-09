"""Storage of the xpath, class and id identifiers"""

from easydict import EasyDict

markers = EasyDict(
    {
        "ChatGPT": {
            "login"      : "//button[@data-testid='login-button']",
            "email"      : "//input[contains(@class, 'email-input') or @id='username']",
            "pwd"        : "//input[@id='password']",
            "continue_btn": "//button[text()='Continue']",
            "tutorial"   : "//div[contains(text(), 'Okay, let’s go')]",
            "button"     : "button",
            "done"       : "//button[//div[text()='Done']]",
            "menu"       : "//button[@data-testid='profile-button']",
            "send"       : "//button[@data-testid='send-button']",
            "stop"       : "//button[@data-testid='stop-button']",
            "search"     : "//button[@aria-label='Search']",
            "reason"     : "//button[@aria-label='Reason']",
            "custom"     : "//div[contains(text(), 'Custom')]",
            "cust_toggle": "//button[@role='switch']",
            "cust_txt"   : "//textarea[@type='button']",
            "cust_save"  : "//div[contains(text(), 'Save')]",
            "cust_cancel": "//div[contains(text(), 'Cancel')]",
            "cust_tut"   : "//div[text()='OK']",
            "chatbox"    : "//div[@data-message-author-role='assistant']",
            "wait"       : "//button[contains(@data-testid, 'stop-button')]",
            "reset"      : "//a[//span[text()='New chat']]",
            "reset_cq"   : "truncate",
            "regen_1"    : "//button[div/span[contains(text(), '4o')]]",
            "regen_2"    : "//div[contains(text(), 'Try again')]",
            "textarea"   : '//div[@id="prompt-textarea"]',
            "gpt"        : "//span[text()='{}']"
        },
        "Copilot": {
            "file_types"    : ["gif", "jpg", "jpeg", "png", "webp"],
            "textarea"      : "//textarea[@id='userInput']",
            "chatbox"       : "//div[@data-content='ai-message']/div",
            "send"          : "//button[@aria-label='Submit message']",
            "disabled_send" : "//button[@aria-label='Submit message' and @disabled]",
            "upload_img"    : "//input[@type='file']",
            "thumbnail"     : "//img[@aria-label='Uploaded image']",
            "dismiss"       : "//button[@aria-label='Remove image']",
            "home"          : "//button[@data-testid='home-button']",
            "history"       : "//button[@aria-label='View history']",
            "open"          : "//button[@title='Open']",
            "new_chat"      : "//button[@data-testid='new-chat-button']",
            "submit"        : "//button[contains(@class, 'rounded-submitButton')]",
            "location"      : "//button[@title='Maybe later']",
            "think"         : "//button[contains(@title, 'Think')]",
            "think_active"  : "//span[contains(text(), 'Think')]"
        },
        "Gemini": {
            "file_types" : ["jpg", "jpeg", "png", "webp"],
            # "textarea"   : '//div[@role="textbox"]',
            "textarea"   : '//div[@contenteditable="true"]',
            "wait"       : '//rect',
            "chatbox"    : "//message-content",
            "send"       : "//button[@aria-label='Send message']",
            "new_chat"   : "//mat-icon[@fonticon='add']",
            "chat_conf"  : '//button[@data-test-id="confirm-button"]',
            "hist_off"   : '//button[@data-test-id="bard-activity-disabled-button"]',
            "regen"      : "//button[@aria-label='Regenerate']",
            "mod_opt"    : "//button[@role='menuitem'][not(contains(@style, 'none'))]",
            "img_btn"    : "//mat-icon[@fonticon='add_photo_alternate']",
            "img_upload" : "//input[@name='Filedata']",
            "img_loaded" : "//img[@aria-label='Image preview']",
            "got_it"     : "//button[@data-test-id='got-it-button']"
        },
        "LeChat" : {
            "username"   : "//div[@data-testid='node/input/identifier']//input",
            "password"   : "//div[@data-testid='node/input/password']//input",
            "textarea"   : "//div/textarea",
            "stop_gen"   : "//button[@aria-label='Stop generation']",
            "chatbox"    : "//*[contains(@class,'prose')]",
            "regen"      : "//button[@aria-label='Rewrite']",
            "model"      : "//button/span[@class='truncate']",
            "model_op"   : "//div[contains(@class, 'w-full')]/div[contains(@class, 'text-sm')]",
            "send"       : "//button[@aria-label='Send question']"
        },
        "HuggingChat": {
            "login"      : "//form[@action='/chat/login']/button",
            "username"   : "//input[@name='username']",
            "password"   : "//input[@name='password']",
            "a_login"    : "//button[contains(text(), 'Login')]",
            "textarea"   : "//textarea",
            "send"       : "//button[@aria-label='Send message']",
            "stop_gen"   : "//button[contains(text(),'Stop generating')]",
            "chatbox"    : "//div[@role='presentation']",
            "search"     : '//div[div[text()="Search the web"]]/button',
            "models"     : "//a[@href='/chat/models']",
            "model_li"   : "//div[@aria-label='Model card']/a",
            "model_a"    : "//div[div[span[text()='Active']]]/a",
            "settings"   : "//h2[text()='Settings']",
            "model_act"  : "//button[@name='Activate model']"
        },
        "Pi": {
            "textarea"   : "//textarea[@role='textbox']",
            "send"       : "//button[@aria-label='Submit text']",
            "wait"       : "//button[@disabled]",
            "chatbox"    : "//div[@class='flex items-center']"
        },
        "DeepSeek" : {
            "username"      : "//input[@type='text']",
            "password"      : "//input[@type='password']",
            "checkbox"      : "//div[contains(@class, 'checkbox-label')]",
            "login"         : "//div[contains(@class, 'register-button')]",
            "textarea"      : "//textarea",
            "send"          : "//div[@role='button' and @aria-disabled]",
            "send_button"   : "//div[@role='button']//div[@class='ds-icon']",
            "chatbox"       : "//div[div[contains(@class, 'ds-markdown')]]",
            "new_chat"      : "//span[contains(text(), 'New chat')]",
            "deepthink"     : "//div[span[contains(text(), 'DeepThink')]]",
            "search"        : "//div[span[contains(text(), 'Search')]]",
            "input_file"    : "//input[@type='file']",
            "disabled_send" : "//div[@role='button' and @aria-disabled='true']"
        }
    }
)
