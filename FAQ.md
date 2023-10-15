## Why should we login manually to use Bard?
In order to use Bard, you need to log in to your Google account first. The login process is straightforward to implement and there may be manual obstacles to pass like 2FA. Therefore, you need to complete a manual login to use Bard.

## How to set up Bard?
To set up Bard, you will need to create a user profile on Chrome and then log in to your Google account. To do this, follow these steps:

```python
chathead = BardClient(
    cold_start=True,
    incognito=False,
    headless=False,
    user_data_dir='<path/to/user/profile>'
)
```
Replace <path/to/user/profile> with the path to your user profile directory.

- Now, you should have a normal functioning Chrome session.
- Type `https://bard.google.com/chat/` to your address bar and click Sign In
- Enter your credentials and log in.
- If this is your first time using Google Bard, agree on the terms and finish the tutorial.

After this, your setup is complete. You can call your constructor as follows:

```python
chathead = BardClient(
    incognito=False,
    user_data_dir='<path/to/user/profile>'
)
```

## I don't want to login each time, is it possible?

Yes, that is possible. As an example, create a user profile with this code

```python
chathead = ChatGPTClient(
    username=<username>
    password=<password>
    incognito=False,
    user_data_dir='<path/to/user/profile>'
)
```
Replace <username>, <password>, and <path/to/user/profile> with your own values.

This will create a permanent profile and you can use that profile afterwards. After your first run, pass `skip_login=True` and `incognito=False` to your constructor.

