from __future__ import print_function
# import requests
import asyncio
import aiohttp
import pandas as pd
import time
import numpy as np

from itemsInfo import itemsName, itemsId, itemsUrlName


start_time = time.time()

ordersAvgPlat = []
ordersLastSold = []
ordersItemType = []
ordersAvgPlatMaxMod = []
ordersLastSoldMaxMod = []
ordersAvgPlatDiff = []
ordersLastSoldPlatDiff = []

print('itemIdLength: ', len(itemsId), 'itemNameLength: ', len(itemsName), 'urlNameLength: ', len(itemsUrlName))


def fetchAvgPlat(data, ordersLength, error, index):
    try:    
        avgPlat = data['payload']['statistics_closed']['90days'][ordersLength]['moving_avg']
    except KeyError as key:
        # Handle key error when the expected JSON structure is not found
        avgPlat = 0
        error += 1
        print(f"        JSON structure error: {key} (Item {index})")
    return avgPlat, error

def fetchLastSold(data, ordersLength, error, index):
    try:
        lastSold = data['payload']['statistics_closed']['90days'][ordersLength]['wa_price']
    except KeyError as key:
        lastSold = 0
        error += 1
        print(f"        JSON structure error: {key} (Item {index})")
    return lastSold, error


async def fetchStats():
    async with aiohttp.ClientSession() as session:
        index = 0
        aPError = 0
        lSError = 0
        nDError = 0
        dFError = 0
        NError = 0
        aPError2 = 0
        lSError2 = 0
        mRError = 0
        nMDError = 0
        avgMaxedPlat = 0
        lastSoldMaxed = 0
        avgPlatDiff = 0
        lastSoldPlatDiff = 0
        requests = 10
        
        for item in itemsUrlName:
            rate = 1/requests # sets rate limit of 10 requests/second
            try:
                ordersUrl = 'https://api.warframe.market/v1/items/{}/statistics'
                response = await session.get(ordersUrl.format(item), ssl = False)
                # session.raise_for_status()  # Raise an exception for HTTP errors
                
                data = await response.json()
                
                if 'payload' in data and 'statistics_closed' in data['payload'] and '90days' in data['payload']['statistics_closed']:
                    ordersLength = len(data['payload']['statistics_closed']['90days']) - 1
                    if ordersLength > 0:
                        
                        avgPlat, aPError = fetchAvgPlat(data, ordersLength, aPError, index)
                        lastSold, lSError = fetchLastSold(data, ordersLength, lSError, index)
                        
                        # Allows for values to be able to still be used in math by keeping them 'float' values only, not 'NoneType' and 'float'
                        if avgPlat != 0:
                            ordersAvgPlat.append(avgPlat)
                        else:
                            ordersAvgPlat.append(None)
                        if lastSold != 0:
                            ordersLastSold.append(lastSold)
                        else:
                            ordersLastSold.append(None)

                        if 'mod_rank' in (data['payload']['statistics_closed']['90days'][ordersLength] or data['payload']['statistics_closed']['90days'][ordersLength - 1]):
                            # Checks if the mod_rank object is in the indexed item data for both the unranked, ordersLength, or "maxed", ordersLength - 1,  mod
                            ordersItemType.append('Mod')
                            if ordersLength > 1:
                                
                                if(data['payload']['statistics_closed']['90days'][ordersLength - 1]['mod_rank'] > 0):
                                    # Checks if the indexed mod is actually maxed 
                                    avgMaxedPlat, aPError2 = fetchAvgPlat(data, ordersLength - 1, aPError2, index)
                                    lastSoldMaxed, lSError2 = fetchLastSold(data, ordersLength - 1, lSError2, index)
                                    
                                    # Allows for values to be able to still be used in math by keeping them 'float' values only, not 'NoneType' and 'float'
                                    if avgMaxedPlat!= 0:
                                        ordersAvgPlatMaxMod.append(avgMaxedPlat)
                                    else:
                                        ordersAvgPlatMaxMod.append(None)
                                    if lastSoldMaxed != 0:
                                        ordersLastSoldMaxMod.append(lastSoldMaxed)
                                    else:
                                        ordersLastSoldMaxMod.append(None)
                                    
                                    avgPlatDiff = avgMaxedPlat - avgPlat
                                    ordersAvgPlatDiff.append(round(avgPlatDiff, 2))
                                    lastSoldPlatDiff = lastSoldMaxed - lastSold
                                    ordersLastSoldPlatDiff.append(round(lastSoldPlatDiff, 2))
                                else:
                                    ordersAvgPlatDiff.append(None)
                                    ordersLastSoldPlatDiff.append(None)
                                    ordersAvgPlatMaxMod.append(None)
                                    ordersLastSoldMaxMod.append(None)
                                    mRError += 1
                                    print(f"                Mod rank mismatch: (Item {index})")
                                    
                            else:
                                ordersAvgPlatDiff.append(None)
                                ordersLastSoldPlatDiff.append(None)
                                ordersAvgPlatMaxMod.append(None)
                                ordersLastSoldMaxMod.append(None)
                                nMDError += 1
                                print(f"            No maxed mod data available: (Item {index})")
                        else:
                            # Handle the case when the item type isn't a mod
                            ordersAvgPlatDiff.append(np.nan)
                            ordersLastSoldPlatDiff.append(np.nan)
                            ordersItemType.append('Item')
                            ordersAvgPlatMaxMod.append(np.nan)
                            ordersLastSoldMaxMod.append(np.nan)
                            
                        print(f"Item {index}: {ordersUrl.format(item)} - avgPlat: {ordersAvgPlat[index]} | lastSold: {ordersLastSold[index]} | avgPlatMaxed: {ordersAvgPlatMaxMod[index]}", 
                            f" | lastSoldMaxed: {ordersLastSoldMaxMod[index]} | avgPlatDiff: {ordersAvgPlatDiff[index]} | lastSoldPlatDiff {ordersLastSoldPlatDiff[index]}")
                    else:
                        # Handle the case when there is no data for the item
                        ordersLastSold.append(None)
                        ordersAvgPlat.append(None)
                        ordersItemType.append(None)
                        ordersAvgPlatMaxMod.append(None)
                        ordersLastSoldMaxMod.append(None)
                        ordersAvgPlatDiff.append(None)
                        ordersLastSoldPlatDiff.append(None)
                        nDError += 1
                        print(f"    No data available: (Item {index})")
                else:
                    # Handle the case when data is not in the expected format
                    ordersLastSold.append(None)
                    ordersAvgPlat.append(None)
                    ordersItemType.append(None)
                    ordersAvgPlatMaxMod.append(None)
                    ordersLastSoldMaxMod.append(None)
                    ordersAvgPlatDiff.append(None)
                    ordersLastSoldPlatDiff.append(None)
                    dFError += 1
                    print(f"    Data format error: (Item {index})")
                    
                # Adds rate limit
                await asyncio.sleep(rate)
                
            except aiohttp.ClientError as e:
                # Handle network-related errors
                ordersLastSold.append(None)
                ordersAvgPlat.append(None)
                ordersItemType.append(None)
                ordersAvgPlatMaxMod.append(None)
                ordersLastSoldMaxMod.append(None)
                ordersAvgPlatDiff.append(None)
                ordersLastSoldPlatDiff.append(None)
                NError += 1
                requests = requests - 1 # lowers amount of requests per second by 1
                print(f"Aiohttp client error: {e} (Item {index})")
            
            index += 1
    
        print('itemIdLength: ', len(itemsId), 'itemNameLength: ', len(itemsName), 'itemType: ', len(ordersItemType),
            'avgPlatLength: ', len(ordersAvgPlat), 'lastSoldLength: ', len(ordersLastSold),
            'avgPlatMaxedLength: ', len(ordersAvgPlatMaxMod),'lastSoldMaxedLength: ', len(ordersLastSoldMaxMod),
            'avgPlatDiffLength', len(ordersAvgPlatDiff), 'lastSoldPlatDiffLength', len(ordersLastSoldPlatDiff))

        data = { "itemId": itemsId, "itemName": itemsName, "itemType": ordersItemType, "avgPlat": ordersAvgPlat, 
                "lastSold": ordersLastSold, "avgPlatMaxed": ordersAvgPlatMaxMod, "lastSoldMaxed": ordersLastSoldMaxMod,
                "avgPlatDiff": ordersAvgPlatDiff, "lastSoldPlatDiff": ordersLastSoldPlatDiff}
        df = pd.DataFrame(data)
        print(df)

        df.to_csv('items.csv')

        print('avgPlat fetch errors: ', aPError)
        print('lastSold fetch errors: ', lSError)
        print('avgPlat fetch errors (Mod): ', aPError)
        print('lastSold fetch errors (Mod): ', lSError)
        print('Mod rank mismatch errors: ', mRError)
        print('No maxed mod data errors:', nMDError)
        print('No data errors: ', nDError)
        print('Data format errors: ', dFError)
        print('Network errors: ', NError)

        end_time = time.time()
        execution_time = end_time - start_time
        print('\nProgram execution time:', round(execution_time, 2) ,"seconds or", round((execution_time/60), 3) ,"minutes or", round(((execution_time/60)/60), 4) ,"hours\n")
        
asyncio.run(fetchStats())