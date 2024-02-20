## Why should we login manually to use Gemini, Claude or Copilot?
Much like Sisyphos' endless task of rolling a boulder up a hill only to see it to roll back down, it is a similar challenge automating a login page of a service used by millions. These services are constantly updating their login procedures for security, usability and all other reasons, causing automation code to become obsolete faster than ever. Also, the addition of security measures like 2FA is on place, further complicating the automation efforts. It is a never-ending challenge.

\* To login Claude, one needs to enter the verification code (OTP) sent to their email address, makes it impossible to automate.

## How to set up for Gemini, Claude or Copilot?
To access abovementioned services, you need to create a user profile and log in to your account manually. Once you have done this, the login will persist on following usages, much like your own browser! To do this, start the client with following parameters:

```python
chathead = GeminiClient(
    cold_start=True,
    incognito=False,
    headless=False,
    user_data_dir='<path/to/user/profile>'
)
```

It is headless because you need to login your account in order to use the system. It is incognito to utilize this manual login for the next times. Remember to replace <path/to/user/profile> with the path to your user profile directory.

- Now, you should have a normal functioning Chrome session.
- Click Sign In
- Enter your credentials and log in.
- If this is your first time using these services, agree on the terms and finish the tutorial.

After this, your setup is complete. You can call your constructor as follows:

```python
chathead = GeminiClient(
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

