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

![238929504-5963e2a1-af89-4fb7-925a-c8d00194af49](https://github.com/mrzdev/quest_cryptostore/assets/106373816/a2abbde9-c53e-4d3f-8c3f-c3a331b0c149)
