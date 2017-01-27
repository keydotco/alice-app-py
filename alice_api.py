#!/usr/bin/env python
"""
Alice API library using requests
~~~~~~~~~~~~~~~~~~~~~
Alice API Python Wrapper using Requests (https://github.com/kennethreitz/requests)
Full documentation
is at <http://python-requests.org>.
Alice API at <http://developer.aliceapp.com/staff.html>
2016 by <ion@key.co>

"""
import sys
import requests
from ConfigParser import SafeConfigParser


class RequestError(Exception):
    pass


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

    def _try_request(self, url, method, json=None, attempt_number=1):
        # NOTE: Add response status check.
        max_attempts = 3
        try:
            if method == 'GET':
                response = requests.get(url, headers=self.headers, params=self.querystring)

            elif method == 'POST':
                response = requests.post(url, headers=self.headers, params=self.querystring, json=json)

            elif method == 'PUT':
                response = requests.put(url, headers=self.headers, params=self.querystring, json=json)

            response.raise_for_status()

        except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
            # Retry or retry loop
            if attempt_number < max_attempts:
                attempt = attempt_number + 1
                return self._try_request(url, method, json=json, attempt_number=attempt)
            else:
                print e
                raise RequestError('max retries exceed when trying to get the page at %s' % url)
        except requests.exceptions.TooManyRedirects:
            # bad url
            pass
        except requests.exceptions.RequestException as e:
            # catastrophic error. bail.
            print e
            sys.exit(1)

        if method == 'GET':
            return response.json()

        return response

    # =============================================================== #
    # From [ staff-hotel-group-api ]
    def get_all_hotels(self):
        """
        GET : (Alice note) Load all hotels with which current user can interact
        """
        url = self.uri_root + "staff/v1/hotels"
        return self._try_request(url, "GET")

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
        return self._try_request(url, "GET")

    def get_hotel_facility_id(self, hotel_id):
        url = self.uri_root + "staff/v1/hotels/" + str(hotel_id) + "/facilites"
        facilities = self._try_request(url, "GET")
        ids = [f['id'] for f in facilities if f['name'] == 'Concierge']
        return ids[0]

    def get_hotel_services(self, hotel_id, facilities_id):
        """
         GET : (Alice note) Load services for facility.
        """
        url = self.uri_root + "staff/v1/hotels/" + str(hotel_id) + "/facilities/" + str(facilities_id) + "/services"
        return self._try_request(url, "GET")

    def get_hotel_menus(self, hotel_id, facilities_id):
        """
         GET : (Alice note) Load menus for facility.
        """
        url = self.uri_root + "staff/v1/hotels/" + str(hotel_id) + "/facilities/" + str(facilities_id) + "/menus"
        return self._try_request(url, "GET")

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
            return self._try_request(url, "POST", json_form)

    def create_bulk_hotel_arrivals(self, hotel_id, json_form):
        """
        POST : (Alice note) Create bulk hotel arrivals.
        """
        if len(json_form) == 0:
            print 'Error: empty JSON form. Nothing to create.'
        else:
            url = self.uri_root + "staff/v1/hotels/" + str(hotel_id) + "/arrivals/bulk"
            return self._try_request(url, "POST", json_form)

    # =============================================================== #
    # From [ staff-workflow-status-api ]
    def get_workflow_statuses(self, hotel_id):
        """
         GET : (Alice note) Search for workflow statuses.
        """
        url = self.uri_root + "staff/v1/hotels/" + str(hotel_id) + "/workflowStatuses"
        return self._try_request(url, "GET")

    # =============================================================== #
    # From [ staff-reservation-api ]
    def get_hotel_reservations(self, hotel_id):
        """
         GET : (Alice note) Search for reservations. Total number of found reservations is returned in X-Total-Count header
        """
        url = self.uri_root + "staff/v1/hotels/" + str(hotel_id) + "/reservations"
        return self._try_request(url, "GET")

    def create_hotel_reservation(self, hotel_id, json_form):
        """
        POST : (Alice note) Create reservation.
        """
        if len(json_form) == 0:
            print 'Error: empty JSON form. Nothing to create.'
        else:
            url = self.uri_root + "staff/v1/hotels/" + str(hotel_id) + "/reservations"
            return self._try_request(url, "POST", json_form)

    def update_hotel_reservation(self, hotel_id, reservation_id, json_form):
        """
        PUT : (Alice note) Update reservation.
        sample json form:
        {'reservationNumber': 'zErk1oRzfl',
         'status': 'Approved',
         'end': '2017-01-21T05:00:00Z',
         'uuid': '3a600abc-d611-4008-97a2-a69e4bfa769e',
         'firstname': 'Aladdin',
         'lastname': 'Grant',
         'id': 212136,
         'start': '2017-01-19T05:00:00Z',
         'email': 'david+alangrant@key.co'}
        """
        url = self.uri_root + "staff/v1/hotels/" + str(hotel_id) + "/reservations/" + str(reservation_id)
        if len(json_form) == 0:
            print 'Error: empty JSON form. Nothing to update.'
        else:
            url = self.uri_root + "staff/v1/hotels/" + str(hotel_id) + "/reservations/" + str(reservation_id)
            return self._try_request(url, "PUT", json_form)


    # =============================================================== #
    # From [ staff-data-sets-api ]
    def get_dashboard_data(self, hotel_id, dashboard_id):
        """
         GET : (Alice note) Load data sets for the given dashboard.
        """
        url = self.uri_root + "staff/v1/hotels/" + str(hotel_id) + "/dashboards/" + str(dashboard_id) + "/dataSets"
        return self._try_request(url, "GET")

    def get_all_dashboards(self, hotel_id):
        """
        GET : (Alice note) Load dashboards for the given hotel.
       """
        url = self.uri_root + "staff/v1/hotels/" + str(hotel_id) + "/dashboards"
        return self._try_request(url, "GET")

    # =============================================================== #
    # From [ staff-hotel-user-api ]
    def get_all_services(self, hotel_id):
        """
         GET : (Alice note) Load data sets for the given dashboard.
        """
        url = self.uri_root + "staff/v1/hotels/" + str(hotel_id) + "/users"
        return self._try_request(url, "GET")

    # =============================================================== #
    # From [ staff-tickets-api ]
    def get_all_tickets(self, hotel_id):
        """
         GET : (Alice note) Search for tickets. Total number of found tickets is returned in X-Total-Count header.
        """
        url = self.uri_root + "staff/v1/hotels/" + str(hotel_id) + "/tickets"
        return self._try_request(url, "GET")

    def get_ticket(self, hotel_id, ticket_id):
        """
         GET : (Alice note) Load ticket.
        """
        url = self.uri_root + "staff/v1/hotels/" + str(hotel_id) + "/tickets/" + str(ticket_id)
        return self._try_request(url, "GET")

    def get_ticket_messages(self, hotel_id, ticket_id):
        """
         GET : (Alice note) Load all messages for ticket.
        """
        url = self.uri_root + "staff/v1/hotels/" + str(hotel_id) + "/tickets/" + str(ticket_id) + "/messages"
        return self._try_request(url, "GET")

    def get_ticket_transitions(self, hotel_id, ticket_id):
        """
         GET : (Alice note) Workflow statuses allowed for transition for the ticket.

        """
        url = self.uri_root + "staff/v1/hotels/" + str(hotel_id) + "/tickets/" + str(ticket_id) + "/transitions"
        return self._try_request(url, "GET")

    def update_ticket_messages(self, hotel_id, ticket_id, json_form):
        """
        PUT : (Alice note) Add message to ticket.

        """
        if len(json_form) == 0:
            print 'Error: empty JSON form. Nothing to update.'
        else:
            url = self.uri_root + "staff/v1/hotels/" + str(hotel_id) + "/tickets/" + str(ticket_id) + "/messages"
            return self._try_request(url, "PUT", json_form)

    def update_menu_order(self, hotel_id, ticket_id, json_form):
        """
        PUT : (Alice note) All parameters are optional. Only specified parameters will be updated.

        """
        if len(json_form) == 0:
            print 'Error: empty JSON form. Nothing to update.'
        else:
            url = self.uri_root + "staff/v1/hotels/" + str(hotel_id) + "/tickets/" + str(ticket_id) + "/menuOrder"
            return self._try_request(url, "PUT", json_form)

    def update_service_request(self, hotel_id, ticket_id, json_form):
        """
        PUT : (Alice note) All parameters are optional. Only specified parameters will be updated.

        """
        if len(json_form) == 0:
            print 'Error: empty JSON form. Nothing to update.'
        else:
            url = self.uri_root + "staff/v1/hotels/" + str(hotel_id) + "/tickets/" + str(ticket_id) + "/serviceRequest"
            return self._try_request(url, "PUT", json_form)

    def update_workflow_status(self, hotel_id, ticket_id, json_form):
        """
        PUT : (Alice note) Update ticket workflow status.

        """
        if len(json_form) == 0:
            print 'Error: empty JSON form. Nothing to update.'
        else:
            url = self.uri_root + "staff/v1/hotels/" + str(hotel_id) + "/tickets/" + str(ticket_id) + "/workflowStatus"
            return self._try_request(url, "PUT", json_form)

    def create_offline_request(self, hotel_id, json_form):
        """
        POST : (Alice note) Create offline request.

        """
        if len(json_form) == 0:
            print 'Error: empty JSON form. Nothing to update.'
        else:
            url = self.uri_root + "staff/v1/hotels/" + str(hotel_id) + "/tickets/offlineRequest"
            return self._try_request(url, "POST", json_form)

    def create_service_request(self, hotel_id, json_form):
        """
        POST : (Alice note) Create service request.

        """
        if len(json_form) == 0:
            print 'Error: empty JSON form. Nothing to update.'
        else:
            url = self.uri_root + "staff/v1/hotels/" + str(hotel_id) + "/tickets/serviceRequest"
            return self._try_request(url, "POST", json_form)
