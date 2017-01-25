#!/usr/bin/env python
"""
Alice API library using requests
~~~~~~~~~~~~~~~~~~~~~
Alice API Python Wrapper using Requests (https://github.com/kennethreitz/requests)
Full documentation
is at <http://python-requests.org>.
2016 by <ion@key.co>

"""
import sys
import requests
from ConfigParser import SafeConfigParser


class Alice:
    def __init__(self, api_key=None):
        config = SafeConfigParser()
        config.read('config.ini')
        default_uri_root = config.get("alice-api", "uri_root")
        default_api_key = config.get("alice-api", "api_key")
        default_auth = config.get("alice-api", "basic_auth")

        self.uri_root = default_uri_root
        self.api_key = api_key if api_key is not None else default_api_key
        self.auth = default_auth
        self.querystring = {"apikey": self.api_key}
        self.headers = {
            'authorization': default_auth,
            'content-type': "application/json",
            'cache-control': "no-cache"
        }

    def request(self, url, method, json=None):
        try:
            if method == 'GET':
                return requests.get(url, headers=self.headers, params=self.querystring).json()

            elif method == 'POST':
                if json is None:
                    print 'Empty JSON form. Nothing to create.'
                return requests.post(url, headers=self.headers, params=self.querystring, json=json)
        except requests.exceptions.Timeout:
            # Retry or retry loop
            pass
        except requests.exceptions.TooManyRedirects:
            # bad url
            pass
        except requests.exceptions.RequestException as e:
            # catastrophic error. bail.
            print e
            sys.exit(1)

    # =============================================================== #
    # From [ staff-hotel-group-api ]
    def get_all_hotels(self):
        """
        GET : (Alice note) Load all hotels with which current user can interact
        """
        url = self.uri_root + "staff/v1/hotels"
        return self.request(url, "GET")

    def get_all_hotel_ids(self):
        hotels = self.get_all_hotels()
        ids = [h['id'] for h in hotels]
        return ids

    # =============================================================== #
    # From [ staff-facilites-api ]
    def get_hotel_facilities(self, hotel_id):
        """
        GET : (Alice note) Load facilities for the given hotel.
        """
        url = self.uri_root + "staff/v1/hotels/" + str(hotel_id) + "/facilites"
        return self.request(url, "GET")

    def get_hotel_facility_id(self, hotel_id):
        url = self.uri_root + "staff/v1/hotels/" + str(hotel_id) + "/facilites"
        facilities = self.request(url)
        ids = [f['id'] for f in facilities if f['name'] == 'Concierge']
        return ids[0]

    def get_hotel_services(self, hotel_id, facilities_id):
        """
         GET : (Alice note) Load services for facility.
        """
        url = self.uri_root + "staff/v1/hotels/" + str(hotel_id) + "/facilities/" + str(facilities_id) + "/services"
        return self.request(url, "GET")

    def get_hotel_menus(self, hotel_id, facilities_id):
        """
         GET : (Alice note) Load menus for facility.
        """
        url = self.uri_root + "staff/v1/hotels/" + str(hotel_id) + "/facilities/" + str(facilities_id) + "/menus"
        return self.request(url, "GET")

    # =============================================================== #
    # From [ staff-hotel-arrival-api ]
    def create_hotel_arrival(self, hotel_id, json_form):
        """
        POST : (Alice note) Create hotel arrival.
        """
        if len(json_form) == 0:
            print 'Error: empty JSON form. Nothing to create.'
        else:
            url = self.uri_root + "staff/v1/hotels/" + str(hotel_id) + "/arrivals"
            return self.request(url, "POST", json_form)

    def create_bulk_hotel_arrivals(self, hotel_id, json_form):
        """
        POST : (Alice note) Create bulk hotel arrivals.
        """
        if len(json_form) == 0:
            print 'Error: empty JSON form. Nothing to create.'
        else:
            url = self.uri_root + "staff/v1/hotels/" + str(hotel_id) + "/arrivals/bulk"
            return self.request(url, "POST", json_form)
