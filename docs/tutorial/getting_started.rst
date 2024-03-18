Getting Started 📋
==================

Before you begin, please ensure that Chrome is installed on your system. 

Here is a script to install Chrome

.. code-block:: bash

    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    sudo dpkg -i google-chrome-stable_current_amd64.deb

Installation
************

.. code-block:: bash

    pip install talkingheads


or from source:

.. code-block:: bash

    pip install git+https://github.com/ugorsahin/TalkingHeads

Usage
*****
.. code-block:: python

    from talkingheads import HuggingChatClient

    chathead = HuggingChatClient(YOUR_USERNAME, YOUR_PASSWORD)

    response = chathead.interact("Hello, how are you today")

    print(response)

.. toctree::
   :maxdepth: 2

Setup User Data Directory
*************************

Setting up a user profile is required to use Claude, Copilot, or Gemini. The login pages of these chatbots are not automated because:

* Claude sends you a verification code to log into your account
* Copilot (Microsoft) and Gemini (Google) log you in through their SSO. Automating the login pages of two of the biggest customer and business service providers opens a window for malicious use, and their login pages change every now and then, which will be a never-ending effort.

However, it is possible to set up a user profile and log in to the account in this profile, just like your regular browser, and then using this browser to connect chatbots is much more convenient. Since your login will last a while, you will not be forced to log in every time.

Setting up a user profile can be done with or without using talkingheads. Here, you will find both approaches.

Using CLI

Open a terminal and type the following command:

.. code-block:: bash

google-chrome --user-data-dir=path/to/user/profile

Chrome will welcome you. From here, navigate to the Claude, Copilot, or Gemini webpage and log in. After that, you are ready to use your user profile with talkingheads. Take a look at the below example:

.. code-block:: python

    chathead = GeminiClient(
        incognito=False,
        user_data_dir="path/to/user/profile"
    )

The important thing here is that you set the `incognito=False`. As you may already noticed, you can't use your regular login in incognito mode. Replace `<path/to/user/profile>` with the path to your user profile directory.

If you want to log in without using the CLI, create an instance as provided below.

.. code-block:: python

    chathead = GeminiClient(
        cold_start=True,
        incognito=False,
        headless=False,
        user_data_dir="path/to/user/profile"
    )

#. Now, you should have a normal functioning Chrome session.
#. If you are not at the webpage, type the webpage address (e.g. `https://gemini.google.com/chat/`)
#. Enter your credentials and log in.
#. If this is your first time using the account, agree to the terms and finish the tutorial.

After this, your setup is complete. You can call your constructor as follows:

.. code-block:: python

    chathead = GeminiClient(
        incognito=False,
        user_data_dir='<path/to/user/profile>'
    )

Login without using environment variables
*****************************************

If you don't want to keep your username-password as an environment variable or put them in the code, you can manually create a user profile as described above and log in. This will create a permanent profile, which you can use afterward. Keep it in mind to check the `Remember me` button! Please consider that the login caches may expire, so you may need to log in occasionally. 

To use a profile with a manual login, please

#. set `credential_check=False` to turn off controlling the existence of variables
#. set `skip_login=True` to turn off the login procedure.

.. code-block:: python

    chathead = ChatGPTClient(
        incognito=False,
        user_data_dir='<path/to/user/profile>',
        credential_check=False,
        skip_login=True
    )

Replace `<path/to/user/profile>` with the path to user profile.
