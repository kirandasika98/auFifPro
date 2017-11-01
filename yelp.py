"""
This file handles everything needed to communicate with the Yelp API (v3).

Yelp credentials should be saved in a .json file for local development.
Ask me for further instructions
Format for JSON
{
    "yelp": {
        "client_id": "CLIENT_ID",
        "client_secret": "CLIENT_SECRET"
    }
}
"""
import requests
import os
import json

API_AUTH_ENDPOINT = "https://api.yelp.com/oauth2/token"
API_ENDPOINT_V3 = "https://api.yelp.com/v3/"
LOCATION = 36832
DEFAULT_LAT = 32.609857032
DEFAULT_LONG = -85.4807820

if "HEROKU" in os.environ:
    # Grab client_id, client_secret and access_token from HEROKU
    ACCESS_TOKEN = os.environ["YELP_ACCESS_TOKEN"]
    CLIENT_ID = os.environ["YELP_CLIENT_ID"]
    CLIENT_SECRET = os.environ["YELP_CLIENT_SECRET"]
else:
    # Grab yelp credentials from json file
    credentials = json.loads(file("credentials.json").read())
    ACCESS_TOKEN = credentials["yelp"]["access_token"]
    CLIENT_ID = credentials["yelp"]["client_id"]
    CLIENT_SECRET = credentials["yelp"]["client_secret"]


class YelpFusionHandler():
    def __init__(self, user=None):
        self.user = user
        self.headers = dict(Authorization="Bearer {}".format(ACCESS_TOKEN))

    def get_businesses(self, search_query=None):
        if search_query is None:
            # creating a new params dict if one if not provided
            search_query = dict(location=LOCATION)

        search_query["location"] = LOCATION
        url = API_ENDPOINT_V3 + "businesses/search"
        business_data_request = requests.get(url, params=search_query,
                                             headers=self.headers)

        return json.dumps(business_data_request.json(), indent=4)

    def get_business_data_by_id(self, yelp_id=None):
        """
        Gets the data of a yelp business by id
        """
        if yelp_id is None:
            return None

        url = API_ENDPOINT_V3 + "businesses/" + yelp_id
        business_data_request = requests.get(url, headers=self.headers)
        return business_data_request.json()

    def get_auto_complete_businesses(self, search_query=None):
        """
        args:
            search_query must contain term, latitude and longitude
        return:
            json dict of suggestions
        """
        if search_query is None:
            search_query = dict(term="Coffee", latitude=DEFAULT_LAT,
                                longitude=DEFAULT_LONG)

        search_query["latitude"] = DEFAULT_LAT
        search_query["longitude"] = DEFAULT_LONG
        url = API_ENDPOINT_V3 + "autocomplete"
        autocomplete_data_request = requests.get(url, params=search_query,
                                                 headers=self.headers)

        return autocomplete_data_request.json()["businesses"]


if __name__ == "__main__":
    yfh = YelpFusionHandler()
    query = str(raw_input("search term: "))
    print yfh.get_auto_complete_businesses({"text": query})
