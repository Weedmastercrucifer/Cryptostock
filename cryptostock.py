import requests      #for making HTTP requests
import json          #for handling json data
import time          #for sleep operation
from boltiot import Bolt
import conf,math,statistics          #configuration file



def get_bitcoin_price():
    URL="https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=USD"
    response = requests.request("GET",URL,verify=False)
    response = json.loads(response.text)
    print("response is",response)
    current_price = response["USD"]
    return current_price
print(get_bitcoin_price())
trade_price=35000
mybolt=Bolt(conf.bolt_api_key,conf.device_id)
history_data=[]




def send_telegram_message(message):
    """Sends message via Telegram"""
    url="https://api.telegram.org/" + conf.telegram_bot_id + "/sendMessage"
    data={
          "chat_id":conf.telegram_chat_id,
          "text":message
         }
    try:
       response= requests.request("POST",url,params=data)
       print("This is the Telegram url")
       print(url)
       print("This is the telegram response")
       print(response.text)
       telegram_data=json.loads(response.text)
       return telegram_data["ok"]
    except Exception as e:
           print("An error occurred while sending message")
           print(e)
           return False



def compute_bounds(history_data,frame_size,factor):
    if len(history_data)<frame_size:
       return None
    if len(history_data)>frame_size:
       del history_data[0:len(history_data)-frame_size]

    Mn=statistics.mean(history_data)
    Variance=0
    for data in history_data :
        Variance +=math.pow((data-Mn),2)
    Zn=factor*math.sqrt(Variance/frame_size)
    High_bound=history_data[frame_size-1]+Zn
    Low_bound=history_data[frame_size-1]-Zn
    return [High_bound,Low_bound]








while True:
      sale_price=get_bitcoin_price()
      try:
         print("Current sale price is", sale_price)
         print("Your selling price is", trade_price)
         if sale_price>trade_price:
            print("Turning on LED for 5 seconds")
            response_1=mybolt.digitalWrite('0','HIGH')
            print(response_1)
            print("Sending message via telegram")
            message="SALE PRICE IS HIGHER. TIME TO BUY SOME STOCKS"
            telegram_status=send_telegram_message(message)
            print("The telegram status is: ", telegram_status)
            time.sleep(5)
            response_1=mybolt.digitalWrite('0','LOW')
            print(response_1)
            time.sleep(5)


      except Exception as e:
             print("ERROR OCCURRED")
             print(e)

      bound=compute_bounds(history_data,conf.FRAME_SIZE,conf.MUL_FACTOR)
      if not bound:
         required_data_count=conf.FRAME_SIZE-len(history_data)
         print("Not enough data for Z-score. Need ", required_data_count, "more data points")
         history_data.append(sale_price)
         print(history_data)
         time.sleep(10)
         continue


      try:
         if sale_price >bound[0]:
            print("Stock is performing higher than expected. Sending message via telegram")
            message="STOCK IS PERFORMING HIGHER THAN EXPECTED"
            telegram_status=send_telegram_message(message)
            print("The telegram status is: ", telegram_status)
         elif sale_price<bound[1]:
              print("Stock is performing lower than expected. Sending message via telegram")
              message="STOCK IS PERFORMING LOWER THAN EXPECTED"
              telegram_status=send_telegram_message(message)
              print("The telegram status is: ", telegram_status)
         history_data.append(sale_price);
      except Exception as e:
             print("ERROR: " ,e)





      time.sleep(60)

