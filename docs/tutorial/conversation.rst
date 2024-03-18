How to use Conversation
=======================

Conversation is a special case of multiagent interactions, where only two agents are involved. The configuration file for conversation is similar to the multiagent configuration, but a conversation only has two agents. The following example demonstrates an example:

.. code-block:: python

    conversation_head = Conversation('path/to/config.yaml')
    interviewer = """Assume you are a researcher and will conduct a human cognition test.
    Instruct the subject with the following instructions, one by one. Only ask for one instruction at a time.
    Here are the instructions
    1) Without further ado, just write the following: "Book."
    2) Calculate 4x10.
    3) Name three countries with the largest total area in North America.

    Start by greeting the subject."""

    candidate = (
        "You accepted participating in a research study "
        "and you will follow the instructions of the researchers."
        "Answer with proper sentences."
    )

    responses = conversation_head.start_conversation(
        intro_prompt_1=interviewer, intro_prompt_2=candidate
    )
    print(response[0]) # interviewer
    print(response[1]) # candidate

Output:

.. code-block::

    Greetings! Thank you for participating in our human cognition test. Let's begin with the first instruction:
    Please write the word "Book."

    Book

.. code-block:: python

    responses = conversation_head.continue_conversation()
    print(response[0]) # interviewer
    print(response[1]) # candidate

Output:
.. code-block::

    Great job! Now, onto the second instruction:
    Please calculate 4 multiplied by 10.

    4 multiplied by 10 equals 40.

