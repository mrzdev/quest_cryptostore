# quest_cryptostore
A simple, dockerized [Cryptofeed](https://github.com/bmoscon/cryptofeed)
 callback that stores Binance Futures orderbook data in QuestDB.    
The native callback wouldn't want to work for me so I hacked this together.          
All you need to setup is clone this repo and run:
```bash
docker run -p 9000:9000 \
  -p 9009:9009 \
  -p 8812:8812 \
  -p 9003:9003 \
  -v "$(pwd):/var/lib/questdb" \
  questdb/questdb:latest

docker build . -t quest_cryptostore:latest

docker run --network="host" -d quest_cryptostore:latest
```
There's no need to add schema, because QuestDB client figures it out automatically:   

![stored_book](https://github.com/mrzdev/quest_cryptostore/assets/106373816/452779e6-469c-413c-91d8-6f896395ffac)
