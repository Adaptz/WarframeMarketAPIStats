from __future__ import print_function
# import requests
import asyncio
import aiohttp
import pandas as pd
import time
import numpy as np


start_time = time.time()


itemsUrl = 'https://api.warframe.market/v1/items'

itemsName = []
itemsId = []
itemsUrlName = []
items = []

# Gathers id, url_name, and url_name for all items using asyncio
async def fetchItems():
    async with aiohttp.ClientSession() as session:
        response = await session.get(itemsUrl, ssl = False)
        data = await response.json()
        itemsLength = len(data['payload']['items'])
        index = 0
        while(index != itemsLength):
            items.append(index)
            index += 1 
            
        for item in items:
            urlName = data['payload']['items'][item]['url_name']
            id = data['payload']['items'][item]['id']
            name = data['payload']['items'][item]['item_name']
            
            itemsId.append(id)
            itemsName.append(name)
            itemsUrlName.append(urlName)
            print(item + 1,' / ',itemsLength,' Items Stored', end='\r')

# loop = asyncio.get_event_loop()
# loop.run_until_complete(items)
# loop.close
asyncio.run(fetchItems())
    
end_time = time.time()
execution_time = end_time - start_time
print('\n\nItems fetch time:', round(execution_time, 2) ,"seconds\n")

infoType = []

async def fetchInfo():
    async with aiohttp.ClientSession() as session:
        index = 0
        requests = 7
        for item in itemsUrlName:
            rate = 1/requests # sets rate limit of 7 requests/second
            try:
                infoUrl = 'https://api.warframe.market/v1/items/{}'
                
                response = await session.get(infoUrl.format(item), ssl=False)
                data = await response.json()
                if 'payload' in data and 'item' in data['payload']:
                    tags = data['payload']['item']['items_in_set'][0]['tags']
                    if 'mod' in tags:
                        if 'riven_mod' in tags:
                            infoType.append('Riven')
                        else:
                            infoType.append('Mod')
                    elif 'arcane_enhancement' in tags:
                        infoType.append('Arcane')
                    elif 'weapon' in tags:
                        infoType.append('Weapon')
                    elif 'warframe' in tags:
                        infoType.append('Warframe')
                    elif 'blueprint' in  tags:
                        infoType.append('Blueprint')
                    elif 'misc' in tags:
                        infoType.append('Misc.')
                    elif 'relic' in tags:
                        infoType.append('Relic')
                    elif 'fish' in tags:
                        infoType.append('Fish')
                    elif 'scene' in tags:
                        infoType.append('Scene')
                    elif 'emote' in tags:
                        infoType.append('Emote')
                    elif 'gem' in tags:
                        infoType.append('Gem')
                    elif 'sentinel' in tags:
                        infoType.append('Sentinel')
                    elif 'component' in tags:
                        infoType.append('Component')
                    elif 'skin' in tags:
                        infoType.append('Skin')
                    elif 'lens' in tags:
                        infoType.append('Lens')
                    elif 'imprint' in tags:
                        infoType.append('Imprint')
                    elif 'ayatan_sculpture' in tags:
                        infoType.append('Ayatan Sculpture')
                    elif 'collectible' in tags:
                        infoType.append('Collectible')
                    elif 'ayatan_star' in tags:
                        infoType.append('Ayatan Star')
                    elif 'beacon' in tags:
                        infoType.append('Beacon')
                    elif 'fusion core' in tags:
                        infoType.append('Fusion Core')
                    elif 'key' in tags:
                        infoType.append('Key')
                    else:
                        infoType.append('Other')
                else:
                    print(f"    Data format error: (Item {index})")
                    infoType.append('Unknown')  # Handle cases with unexpected JSON structure
                
                # Adds rate limit
                await asyncio.sleep(rate)
                    
                    
            except aiohttp.ClientError as e:
                # Handle network-related errors
                infoType.append(None)
                requests = requests - 1 # lowers amount of requests per second by 1
                print(f"Aiohttp client error: {e} (Item {index})")
                
            print(f"Item {index}: {infoUrl.format(item)} - Type : {infoType[index]}")
            index += 1
            
        uniqueTypes = set(infoType)
        for type in uniqueTypes:
            count = infoType.count(type)
            print(f'{type}: {count}')

            
asyncio.run(fetchInfo())

data = { "Id": itemsId, "Name": itemsName, "Type": infoType, "UrlName": itemsUrlName, "Url": itemsUrl}
df = pd.DataFrame(data)
print(df)

df.to_csv('itemsInfo.csv')
    
end_time = time.time()
execution_time = end_time - start_time
print('\n\nItems info fetch time:', round(execution_time, 2) ,"seconds\n")