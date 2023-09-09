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
print(r.status_code)

listLength = len(itemsId)
ordersAvgPlat = []
ordersLastSold = []

print('itemIdLength: ', len(itemsId), 'itemNameLength: ', len(itemsName), 'urlNameLength: ', len(itemsUrlName))

while index != listLength:
    try:
        ordersUrl = 'https://api.warframe.market/v1/items/' + itemsUrlName[index] + '/statistics'
        r = requests.get(ordersUrl)
        r.raise_for_status()  # Raise an exception for HTTP errors
        
        data = r.json()
        
        if 'payload' in data and 'statistics_closed' in data['payload'] and '90days' in data['payload']['statistics_closed']:
            ordersLength = len(r.json()['payload']['statistics_closed']['90days'])
            if ordersLength > 0:
                try:
                    lastSold = data['payload']['statistics_closed']['90days'][ordersLength - 1]['wa_price']
                    ordersLastSold.append(lastSold)
                except KeyError as key:
                    lastSold = None
                    ordersLastSold.append(lastSold)
                    error1 += 1
                    print(f"    JSON structure error: {key} (Item {index})")
                    
                try:    
                    avgPlat = data['payload']['statistics_closed']['90days'][ordersLength - 1]['moving_avg']
                    ordersAvgPlat.append(avgPlat)
                except KeyError as key:
                    # Handle key error when the expected JSON structure is not found
                    avgPlat = None
                    ordersAvgPlat.append(avgPlat)
                    error1 += 2
                    print(f"    JSON structure error: {key} (Item {index})")

                print(f"Item {index}: {ordersUrl} - avgPlat: {avgPlat}  lastSold: {lastSold}")
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

#avgPlatMissing = ordersAvgPlat.count(None)
print('avgPlat fetch errors: ', error1)
#lastSoldMissing = ordersLastSold.count(None)
print('lastSold fetch errors: ', error2)
print('No data errors: ', error3)
print('Data format errors: ', error4)
print('Network errors: ', error5)

end_time = time.time()
execution_time = end_time - start_time
print('\nProgram execution time: ', execution_time/60 ,"minutes")