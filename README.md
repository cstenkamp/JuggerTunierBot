# Turnierchecker

Bot der auf [turniere.jugger.org](turniere.jugger.org) geht und in unsere Telegram-Gruppe eine Umfrage schickt sobald ein neues Turnier verfügbar ist.

## Install

First you need to create a `.env` file with the following contents:
```
GROUP_ID=YOUR_GROUP_ID
TGRAM_TOKEN=YOUR_BOT_TOKEN
```
You can create a new bot and get its token in under a minute using Telegram's @Botfather, and you can figure out the Group ID of your group by adding Telegram's @RawDataBot to it.

### Linux + Docker
Install Docker and Docker-Compose, clone this repository, and then add to your crontab: `*/15 * * * * /usr/local/bin/docker-compose -f /path/to/JuggerTunierBot/docker-compose.yml up &>> /var/log/juggerturnierbot.log` As per the compose-file, the `.env` file resides in `path/to/data`, but you can mount volumes from other places at will.

### Everything else

Requires Python >= 3.8ish. Clone this repo, add a new directory `data` in root, and inside it add the env-file under the name `.env`. Create a new conda-environment, activate it, run `pip install -r requirements.txt` and then run `python turnierchecker.py`.