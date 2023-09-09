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
print(r.status_code)

listLength = len(itemsId)
ordersAvgPlat = []

print('itemId: ', len(itemsId), 'itemName: ', len(itemsName), 'urlName: ', len(itemsUrlName))

while index != listLength:
    try:
        ordersUrl = 'https://api.warframe.market/v1/items/' + itemsUrlName[index] + '/statistics'
        r = requests.get(ordersUrl)
        r.raise_for_status()  # Raise an exception for HTTP errors
        
        data = r.json()
        
        if 'payload' in data and 'statistics_closed' in data['payload'] and '90days' in data['payload']['statistics_closed']:
            ordersLength = len(r.json()['payload']['statistics_closed']['90days'])
            if ordersLength > 0:
                avgPlat = data['payload']['statistics_closed']['90days'][ordersLength - 1]['moving_avg']
                ordersAvgPlat.append(avgPlat)
                print(f"Item {index}: {ordersUrl} - AvgPlat: {avgPlat}")
            else:
                # Handle the case when there is no data for the item
                avgPlat = None
                ordersAvgPlat.append(avgPlat)
                print(f"Item {index}: {ordersUrl} - No data available")
        else:
            # Handle the case when data is not in the expected format
            avgPlat = None
            ordersAvgPlat.append(avgPlat)
            print(f"Item {index}: {ordersUrl} - Data format error")
        
    except requests.exceptions.RequestException as e:
        # Handle network-related errors
        avgPlat = None
        ordersAvgPlat.append(avgPlat)
        print(f"Item {index}: {ordersUrl} - Error fetching data: {e}")
    except KeyError as ke:
        # Handle key error when the expected JSON structure is not found
        avgPlat = None
        ordersAvgPlat.append(avgPlat)
        print(f"Item {index}: {ordersUrl} - JSON structure error: {ke}")
    
    index += 1
    
print('itemId: ', len(itemsId), 'itemName: ', len(itemsName), 'avgPlat: ', len(ordersAvgPlat))
data = { "itemId": itemsId, "itemName": itemsName, "avgPlat": ordersAvgPlat}
df = pd.DataFrame(data)
print(df)

df.to_csv('items.csv')

end_time = time.time()
execution_time = end_time - start_time
print("\nProgram execution time: ", execution_time ,"seconds")