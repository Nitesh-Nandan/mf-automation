from dotenv import load_dotenv
import upstox_client
from upstox_client.rest import ApiException
import os

load_dotenv()

token = os.getenv("UPSTOX_ACCESS_TOKEN")


configuration = upstox_client.Configuration()
configuration.access_token = 'eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiJIVzUyMTMiLCJqdGkiOiI2OTJiMTYxYmIzNGEzMTEzNGI4Njg4MjUiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6ZmFsc2UsImlhdCI6MTc2NDQzMTM4NywiaXNzIjoidWRhcGktZ2F0ZXdheS1zZXJ2aWNlIiwiZXhwIjoxNzY0NDUzNjAwfQ.vghdYoodvEACrrYa9EU6yF6A98EnNdJ1ovNjkPkOYok'

if __name__ == "__main__":
    api_instance = upstox_client.OrderApiV3(upstox_client.ApiClient(configuration))
    body = upstox_client.PlaceOrderV3Request(quantity=1, product="D",validity="DAY", price=9.12, tag="string", instrument_token="NSE_EQ|INE669E01016", order_type="LIMIT",
                                         transaction_type="BUY", disclosed_quantity=0, trigger_price=0.0, is_amo=True, slice=True)

    try:
        api_response = api_instance.place_order(body)
        print(api_response)
    except ApiException as e:
        print("Exception when calling OrderApi->place_order: %s\n" % e)

    print(token)
