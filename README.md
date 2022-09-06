# [Nym (French)](https://t.me/nymfrench) community Bot

## Ajouter un mixnode

1. Fork du repo
2. Modifier le fichier [nodes.json](data/nodes.json) et rajouter les informations sous `mixnodes` ou `gateways`:

  * `idkey`: identity key du mixnode
  * `user`: pseudo Telegram (sans le `@`) 
  * `name`: site Web (optionnel) - [Emoji du pays](https://emojipedia.org/flags/) région

Par exemple:
```json
{
    "idkey": "APxUbCmGp4K9qDzvwVADJFNu8S3JV1AJBw7q6bS5KN9E",
    "user": ["Oheka","cgi_bin"],
    "name": "nym.notrustverify.ch - 🇨🇭Zurich"
  },
```

## To launch your own bot

### Pre-requisites

- docker
- docker-compose
- Telegram bot

Follow this [doc](https://core.telegram.org/bots#6-botfather) about how to create a bot

### Example

![](./resources/img/example.png)

### Getting started

```bash
git clone https://github.com/notrustverify/nymfrench-bot.git
cd ntv-bot
cp .env.example .env

```
In `.env` file, modify the value `TELEGRAM_TOKEN` by the token generated from [Botfather](https://t.me/botfather)

Start the bot `docker compose up -d --build`

