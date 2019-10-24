# Twitch-Chat-Bot

This repository contains a bot module that connects to a Twitch Chat irc channel to read or store messages.
By reading and storing messages the bot can search for a specified phrase within messages or tally votes
from a specified library.  

runBot.py starts the bot with command line interaction allowing for connection and disconnection to different
channels and running methods.

In order to run the bot successfully you will need to get a oauth Token from Twitch.  This can be easily found
in user settings on Twitch.tv.  I reccommend that you write the token into the code to simplify things.
