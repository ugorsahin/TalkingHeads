Getting Started 📋
==================
Before you begin, please ensure that you have Chrome installed on your system. 
To successfully pass the Cloudflare robot test, it is necessary to have undetected-chrome. 🌐🔒
Here is a script to install chrome

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

    answer = chathead.interact("Hello, how are you today")

    print(answer)

.. toctree::
   :maxdepth: 2

Setup Bard
**********

In order to use Bard, you need to log in to your Google account first. The login process is not straightforward to implement and there may be obstacles to pass like 2FA. Therefore, you need to complete a manual login to use Bard.

To set up Bard, you will need to create a user profile on Chrome and then log in to your Google account. To do this, follow these steps:

.. code-block:: python

    chathead = BardClient(
        cold_start=True,
        incognito=False,
        headless=False,
        user_data_dir='<path/to/user/profile>'
    )

Replace `<path/to/user/profile>` with the path to your user profile directory.

#. Now, you should have a normal functioning Chrome session.
#. Type `https://bard.google.com/chat/` to your address bar and click Sign In
#. Enter your credentials and log in.
#. If this is your first time using Google Bard, agree on the terms and finish the tutorial.

After this, your setup is complete. You can call your constructor as follows:

.. code-block:: python

    chathead = BardClient(
        incognito=False,
        user_data_dir='<path/to/user/profile>'
    )

Login without using environment variables
*****************************************

If you don't want to keep your username-password as environment variable or put them in the code, you can create a user profile as described above and login manually. This will create a permanent profile and you can use that profile afterwards, keep in my mind to check `Remember me` button! Please take into account that the login caches may expire so you may need to login every once in a while. 

Too use a profile with manual login, please

#. disable `credential_check=False` to avoid controlling existence of variables
#. enable `skip_login=True` to avoid login procedure.

.. code-block:: python

    chathead = ChatGPTClient(
        incognito=False,
        user_data_dir='<path/to/user/profile>',
        credential_check=False,
        skip_login=True
    )

Replace <path/to/user/profile> with the path to user profile.
