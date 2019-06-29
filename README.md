[![MIT license](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/xdarkzlightz/duno/blob/master/LICENSE)
[![Discord](https://img.shields.io/discord/519056074255499264.svg?label=&logo=discord&logoColor=ffffff&color=7389D8&labelColor=6A7EC2)](https://discord.gg/JXW9RZk)
# Duno

Duno is a Discord bot implementation of the popular card game Uno, written in python using discord.py

Warning: I created this bot in 3 days, as a result the code is very messy and possibly buggy. I've had a couple playthroughs and everything functions normally from what I can tell. If you do run into a bug join the discord server or open a issue

## Gameplay and Images
Firstly in order to create a game you use the `;create` command, this creates a game unique to your channel. Players can then join with the `;join` command and leave with `;leave`, the game has an AFK timer of 5 minutes so if no commands get ran after 5 minutes the game will get deleted and removed from the channel

Now onto the gameplay, in order to start the game you use the `;start` command. Once started it will DM everyone their hand (You can also check it at any time with the `;hand` command). Players can play a card once it's their turn with the `;play colour value` command (Note for wilds that the cmd is `;play wild colour` or `;play wild+4 colour`. Players have a 60 second AFK timer, if the timer runs out it will give you a card and  **At the beginning of every turn the bot will check if you have any playable cards, if you don't then it will auto draw cards until you do have at least one playable card.** 

Now onto winning, once a player gets close to winning and have only one card left they can use the `;uno` command to either call uno or use it to call out the first person that didn't call out uno. Once a player plays all of their cards it will say the player has won and it will remove the game from the channel.

![Hand DM](https://i.ibb.co/wBr8dP0/Hand.png)

![Winning and gameplay](https://i.ibb.co/Rz99qMG/win.png)
(Thanks friend for letting me show this beautiful picture of me winning, this was a legit win btw)

## Setup
### Docker - Recommended
If you want to setup the bot for yourself without much installation trouble you should use the official docker image, copy the command below and replace the `YOUR BOT TOKEN` with your token into a terminal

`docker run -it -e TOKEN="TOKEN" xdarkzlightz/duno`

If you prefer docker-compose you can copy/paste the following yml, make sure to replace the TOKEN environment variable with your bot token

```
version: "3"

services:
	bot:
    	image: xdarkzlightz/duno
        environment:
        	- TOKEN=YOUR BOT TOKEN
        container_name: Duno
```

### Manual Installation
If you want to install the bot manually (Not recommended, there's a lot of room for error) just use the following instructions

prerequisites
 - python 3

#### Linux
Clone the repo `git clone https://github.com/xdarkzlightz/duno.git`

Change into the directory that was created `cd duno`

Rename the `example.env` file to `.env` and replace the information in there 

Create a virtual environment `python3 -m venv venv`, this is recommended so packages don't accidentally conflict with packages you installed outside of the bot however not necessary

Activate the virtual environment `source ./venv/bin/activate`

Start the bot `python3 ./src/bot.py`


#### Windows
Installation instructions not added yet

