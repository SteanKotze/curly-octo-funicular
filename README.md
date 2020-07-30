# curly-octo-funicular
This repository adds scripts to Streamlabs Chatbot to allow users to use a more reliable heist. Additionally, the script also allows the viewers of the channel to gain points by typing messages in chat and through a fishing event.


# Requirements
This library is standalone and only requires python scripting to be enabled in your Steamlabs Chatbot.

# Installation
To install this library navigate to your streamlabs chatbot scripts folder. Once there clone the respository.

# Usage
This library can be used primarily through the twitch chat interface using the following commands.

## Heist
```
!heist <points>
```
If there is no heist that has been started, a mesage will be sent in twitch chat informing the viewers that a new heist is starting and that they can enter it.

If there is a heist that has been started but not executed the user will be informed that they have joined the heist.

If heist is on cooldown the user will be informed that heist is on cooldown and how long it will be until heist is active again.

## Fishing
```
!fish
```
To start the fishing event either @I_am_steak or @Tiltasaurus must type !fish in twitch chat. When this has been done chat will be informed that a school of fish is passing. In order to catch fish the viewers need to type any message containgin the word `fish`, when they have done this they stand a chance to catch a fish and earn points.

# Contributing
Checkout a new branch, push your changes, make a Pull Request to master. After doing this I'll review the work and request changes / approve the PR as I see fit.

# Requests
If there are any changes that you'd like me to make to the scripts you can request them by contacting me at steankotze@gmail.com

# License
None