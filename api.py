import requests
import pandas as pd
import time

start_time = time.time()

infoUrl = 'https://api.warframe.market/v1/items'
r = requests.get(infoUrl)
print(r.status_code)

itemsLength = len(r.json()['payload']['items'])
index = 1
itemsName = []
itemsId = []
itemsUrlName = []

# Gathers id, url_name, and url_name for all items
while(index != itemsLength):
    urlName = r.json()['payload']['items'][index]['url_name']
    id = r.json()['payload']['items'][index]['id']
    name = r.json()['payload']['items'][index]['item_name']
    
    itemsId.append(id)
    itemsName.append(name)
    itemsUrlName.append(urlName)
    index += 1
    
index = 0
aPError = 0
lSError = 0
nDError = 0
dFError = 0
NError = 0
apError2 = 0
lSError2 = 0
mRError = 0
nMDError = 0
avgMaxedPlat = None
lastSoldMaxed = None
listLength = len(itemsId)

ordersAvgPlat = []
ordersLastSold = []
ordersItemType = []
ordersAvgPlatMaxMod = []
ordersLastSoldMaxMod = []

print('itemIdLength: ', len(itemsId), 'itemNameLength: ', len(itemsName), 'urlNameLength: ', len(itemsUrlName))


def fetchAvgPlat(data, ordersLength, error):
    try:    
        avgPlat = data['payload']['statistics_closed']['90days'][ordersLength]['moving_avg']
    except KeyError as key:
        # Handle key error when the expected JSON structure is not found
        avgPlat = None
        error += 1
        print(f"        JSON structure error: {key} (Item {index})")
    return avgPlat, error

def fetchLastSold(data, ordersLength, error):
    try:
        lastSold = data['payload']['statistics_closed']['90days'][ordersLength]['wa_price']
    except KeyError as key:
        lastSold = None
        error += 1
        print(f"        JSON structure error: {key} (Item {index})")
    return lastSold, error
    

while index != listLength:
    try:
        ordersUrl = 'https://api.warframe.market/v1/items/' + itemsUrlName[index] + '/statistics'
        r = requests.get(ordersUrl)
        r.raise_for_status()  # Raise an exception for HTTP errors
        
        data = r.json()
        
        if 'payload' in data and 'statistics_closed' in data['payload'] and '90days' in data['payload']['statistics_closed']:
            ordersLength = len(r.json()['payload']['statistics_closed']['90days']) - 1
            if ordersLength > 0:
                
                avgPlat, aPError = fetchAvgPlat(data, ordersLength, aPError)
                ordersAvgPlat.append(avgPlat)
                
                lastSold, lSError = fetchLastSold(data, ordersLength, lSError)
                ordersLastSold.append(lastSold)

                if 'mod_rank' in (data['payload']['statistics_closed']['90days'][ordersLength] or data['payload']['statistics_closed']['90days'][ordersLength - 1]):
                    # Checks if the mod_rank object is in the indexed item data for both the unranked, ordersLength, or "maxed", ordersLength - 1,  mod
                    ordersItemType.append('Mod')
                    if ordersLength > 1:
                        
                        if(data['payload']['statistics_closed']['90days'][ordersLength - 1]['mod_rank'] > 0):
                            # Checks if the indexed mod is actually maxed
                            avgMaxedPlat, aPError2 = fetchAvgPlat(data, ordersLength - 1, aPError2)
                            ordersAvgPlatMaxMod.append(avgMaxedPlat)
                    
                            lastSoldMaxed, lSError2 = fetchLastSold(data, ordersLength - 1, lSError2)
                            ordersLastSoldMaxMod.append(lastSoldMaxed)
                        else:
                            ordersAvgPlatMaxMod.append(None)
                            ordersLastSoldMaxMod.append(None)
                            mRError += 1
                            print(f"                Mod rank mismatch: (Item {index})")
                            
                    else:
                            ordersAvgPlatMaxMod.append(None)
                            ordersLastSoldMaxMod.append(None)
                            nMDError += 1
                            print(f"            No maxed mod data available: (Item {index})")
                else:
                    # Handle the case when the item type isn't a mod
                    ordersItemType.append('Item')
                    ordersAvgPlatMaxMod.append('N.A.')
                    ordersLastSoldMaxMod.append('N.A.')
                    
                print(f"Item {index}: {ordersUrl} - avgPlat: {avgPlat} | lastSold: {lastSold} | avgPlatMaxed: {avgMaxedPlat} | lastSoldMaxed: {lastSoldMaxed}")
            else:
                # Handle the case when there is no data for the item
                ordersLastSold.append(None)
                ordersAvgPlat.append(None)
                ordersItemType.append(None)
                ordersAvgPlatMaxMod.append(None)
                ordersLastSoldMaxMod.append(None)
                nDError += 1
                print(f"    No data available: (Item {index})")
        else:
            # Handle the case when data is not in the expected format
            ordersLastSold.append(None)
            ordersAvgPlat.append(None)
            ordersItemType.append(None)
            ordersAvgPlatMaxMod.append(None)
            ordersLastSoldMaxMod.append(None)
            dFError += 1
            print(f"    Data format error: (Item {index})")
        
    except requests.exceptions.RequestException as e:
        # Handle network-related errors
        ordersLastSold.append(None)
        ordersAvgPlat.append(None)
        ordersItemType.append(None)
        ordersAvgPlatMaxMod.append(None)
        ordersLastSoldMaxMod.append(None)
        NError += 1
        print(f"Error fetching data: {e} (Item {index})")
    
    index += 1
    
print('itemIdLength: ', len(itemsId), 'itemNameLength: ', len(itemsName), 'itemType: ', len(ordersItemType), 'avgPlatLength: ', len(ordersAvgPlat), 'lastSoldLength: ', len(ordersLastSold), 'avgPlatMaxed: ', len(ordersAvgPlatMaxMod), 'lastSoldMaxed: ', len(ordersLastSoldMaxMod))
data = { "itemId": itemsId, "itemName": itemsName, "itemType": ordersItemType, "avgPlat": ordersAvgPlat, "lastSold": ordersLastSold, "avgPlatMaxed": ordersAvgPlatMaxMod, "lastSoldMaxed": ordersLastSoldMaxMod}
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