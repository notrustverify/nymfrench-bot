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
