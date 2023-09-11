import requests
import json
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
error1 = 0
error2 = 0
error3 = 0
error4 = 0
error5 = 0
error6 = 0
error7 = 0

listLength = len(itemsId)
ordersAvgPlat = []
ordersLastSold = []
ordersItemType = []
ordersMaxMod = []
ordersUnrankedMod = []

print('itemIdLength: ', len(itemsId), 'itemNameLength: ', len(itemsName), 'urlNameLength: ', len(itemsUrlName))


def fetchAvgPlat(data, ordersLength, error):
    try:    
        avgPlat = data['payload']['statistics_closed']['90days'][ordersLength]['moving_avg']
    except KeyError as key:
        # Handle key error when the expected JSON structure is not found
        avgPlat = None
        error += 1
        print(f"    JSON structure error: {key} (Item {index})")
    return avgPlat, error

def fetchLastSold(data, ordersLength, error):
    try:
        lastSold = data['payload']['statistics_closed']['90days'][ordersLength]['wa_price']
    except KeyError as key:
        lastSold = None
        error += 1
        print(f"    JSON structure error: {key} (Item {index})")
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
                
                avgPlat, error1 = fetchAvgPlat(data, ordersLength, error1)
                ordersAvgPlat.append(avgPlat)
                
                lastSold, error2 = fetchLastSold(data, ordersLength, error2)
                ordersLastSold.append(lastSold)
                
                if 'mod_rank' in (data['payload']['statistics_closed']['90days'][ordersLength] or data['payload']['statistics_closed']['90days'][int((ordersLength)/2)]):
                    # Checks if the mod_rank object is in the indexed item data for both the unranked, [ordersLength], or "maxed", int((ordersLength)/2)],  mod
                    ordersItemType.append('Mod')
                    if(data['payload']['statistics_closed']['90days'][ordersLength]['mod_rank'] > 0):
                        # Checks if the indexed mod is actually maxed
                        avgMaxedPlat, error6 = fetchAvgPlat(data, ordersLength, error1)
                        ordersMaxMod.append(avgPlat)
                
                        lastSoldMaxed, error7 = fetchLastSold(data, ordersLength, error2)
                        ordersMaxMod.append(lastSoldMaxed)
                    else:
                        ordersMaxMod.append(None)
                    if(data['payload']['statistics_closed']['90days'][ordersLength]['mod_rank'] == 0):
                        # Checks if the indexed mod is actually unranked
                        unrankedModPlat = data['payload']['statistics_closed']['90days'][int((ordersLength)/2)]
                        ordersUnrankedMod.append(unrankedModPlat)
                    else:
                        ordersUnrankedMod.append(None)
                else:
                    #Handle the case when the item type isn't a mod
                    ordersItemType.append('Item')
                    ordersMaxMod.append('N.A.')
                    ordersUnrankedMod.append('N.A.')
                    
                    
                print(f"Item {index}: {ordersUrl} - avgPlat: {avgPlat} | lastSold: {lastSold}")
            else:
                # Handle the case when there is no data for the item
                lastSold = None
                ordersLastSold.append(lastSold)
                avgPlat = None
                ordersAvgPlat.append(avgPlat)
                error3 += 1
                print(f"Item {index}: {ordersUrl} - No data available")
        else:
            # Handle the case when data is not in the expected format
            lastSold = None
            ordersLastSold.append(lastSold)
            avgPlat = None
            ordersAvgPlat.append(avgPlat)
            error4 += 1
            print(f"Item {index}: {ordersUrl} - Data format error")
        
    except requests.exceptions.RequestException as e:
        # Handle network-related errors
        lastSold = None
        ordersLastSold.append(lastSold)
        avgPlat = None
        ordersAvgPlat.append(avgPlat)
        error5 += 1
        print(f"Item {index}: {ordersUrl} - Error fetching data: {e}")
    
    index += 1
    
print('itemIdLength: ', len(itemsId), 'itemNameLength: ', len(itemsName), 'avgPlatLength: ', len(ordersAvgPlat), 'lastSoldLength: ', len(ordersLastSold))
data = { "itemId": itemsId, "itemName": itemsName, "avgPlat": ordersAvgPlat, "lastSold": ordersLastSold}
df = pd.DataFrame(data)
print(df)

df.to_csv('items.csv')

print('avgPlat fetch errors: ', error1)
print('lastSold fetch errors: ', error2)
print('No data errors: ', error3)
print('Data format errors: ', error4)
print('Network errors: ', error5)

end_time = time.time()
execution_time = end_time - start_time
print('\nProgram execution time:', execution_time ,"seconds", execution_time/60 ,"minutes", (execution_time/60)/60 ,"hours")