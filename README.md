# [Nym (French)](https://t.me/nymfrench) community Bot

## Ajouter un mixnode

1. Fork du repo
2. Modifier le fichier [nodes.json](data/nodes.json) et rajouter les informations sous `mixnodes` ou `gateways`:

  * `idkey`: identity key du mixnode
  * `user`: pseudo Telegram (sans le `@`) 
  * `name`: site Web (optionnel) - [Emoji du pays](https://emojipedia.org/flags/) région
3. Créer un Pull requests

Exemple d'entrée dans `nodes.json` (les mixnodes se trouvent au début):
```json
{
    "idkey": "APxUbCmGp4K9qDzvwVADJFNu8S3JV1AJBw7q6bS5KN9E",
    "user": ["Oheka","cgi_bin"],
    "name": "nym.notrustverify.ch - 🇨🇭Zurich"
  },
```
