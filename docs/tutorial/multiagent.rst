How to use Multiagent
=====================

The Multiagent subpackage facilitates the combined utilization of multiple agents. This package is built on top of two essential functions:

* Broadcasting: Distribute a prompt across multiple agents
* Aggregate: Amalgamate many responses by using a literal instruction

By using these two basic blocks, one can create various flows. Here are some samples to embody it.

* Ask models to pick a number between 1-1000 and select the highest number.
* Seek advice from models about tips for brewing coffee and combine the responses.
* Ask them to write an interesting short story and select the best one.
* Ask models to name the most popular food across Europe and refine the most occurring one

In mathematical terms, an aggregate function takes multiple numerical values and condenses them into one summarized value representing the set. An aggregate function carries out this process of combining the various numbers into a single representative figure. Analogous, we aim to aggregate verbal expressions with a literal instruction.

# Configuration

An example configuration file is in the following form:

.. code-block:: yaml

    multiagent_settings:
        auto_save: true
        save_path: 'path/to/save/dir.csv'
    driver_settings:
        shared:
            verbose: true
            headless : true
            incognito : false
        nodes:
            ChatGPT: {}
            Pi: {}
            LeChat: {}

The options under `multiagent_settings` can be explained as meta-configuration. Currently, the only options here are `auto_save` and `save_path` to save your answers into a file.

The options under `driver_settings` are used to construct each chathead. To keep it modular, we have a `shared` key, which distributes the settings to all given `nodes`. In `nodes`, you can have individual settings. For example, if you would like to use Gemini, you need the following setting

.. code-block:: yaml

    driver_settings:
        nodes:
            Gemini:
                user_data_dir : path/to/user/profile

If you would like to use a user profile for more than one chathead, you need to set the `remote-debugging-port`. When a Chrome instance spawns with a user profile, it locks it to avoid overwriting the profile and corrupting it.

.. code-block:: yaml

    driver_settings:
        shared:
            driver_arguments:
                remote-debugging-port: 20222
        nodes:
            Gemini:
                user_data_dir : path/to/user/profile

Please note that the driver arguments use a dash (-), while other keys use an underscore (_). This inconsistency can be confusing, as Python arguments are typically written with underscores, while Chrome arguments are written with dashes. In future iterations, we can consider switching to the dash form in the configuration for consistency.

If you need to use the same provider more than once, follow the example below:

.. code-block:: yaml

    driver_settings:
        shared:
            incognite: true
        nodes:
            ChatGPT:
                tag: ChatGPT1
                uname_var: CHATGPT_UNAME_1
                pwd_var: CHATGPT_PWD_1
            ChatGPT:
                tag: ChatGPT2
                uname_var: CHATGPT_UNAME_2
                pwd_var: CHATGPT_PWD_2

This will separate the environment variables (remember to set them!) and enable you to use two different instances of the same chatbot. 


#. Voting (beta)

Voting is a special case of aggregation. In a regular aggregation, the aggregating chathead(s) derive a response by combining all responses. In voting, however, the process is slightly different:

* First, all agents respond to the prompt.
* These responses are combined and sent back to each agent as a new prompt, asking them to vote on the best answer.
* Finally, the best answer is selected based on the votes from the agents.

Let's use the "interesting short story" example:

* First, ask the models to write an interesting short story.
* Combine their responses and ask each model to vote on which story is the best.
* Select the story that received the most votes as the best answer.

Currently, this voting functionality is in beta form and will return a list of votes. However, plans are in place to automate the voting results.
