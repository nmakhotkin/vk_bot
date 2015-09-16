# Vk Bot
Vk bot provides the ways to see any activity at vk.com, publish info to specific chats, receives some commands and generate the answers.

Installation
------------

Copy sample config `bot.conf.sample` to `bot.conf` and fill it with auth data.
Install the package:

    pip install -e .

Using
-----

Script 'vkontakte-bot' will be available after installation.
Simple run:

    vkontakte-bot

Test
----

For testing purpose, there is simple test script which sends
only test info to main chat (please configure properly *chat_id* field).

    python vk_bot/test.py
