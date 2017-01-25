import requests
import alice_api
from parse_rest.query import QueryResourceDoesNotExist, QueryResourceMultipleResultsReturned


def register_parse():
    from parse_rest.connection import register
    from ConfigParser import SafeConfigParser
    # key analytics credentials
    config = SafeConfigParser()
    config.read('config.ini')
    app_id = config.get('parse-db-prod', 'app_id')
    rest = config.get('parse-db-prod', 'rest_api_key')
    master = config.get('parse-db-prod', 'master_key')
    register(app_id, rest, master_key=master)


if __name__ == "__main__":
    from parse_rest.datatypes import Object
    from ConfigParser import SafeConfigParser

    class Market(Object):
        pass

    class ServiceMap(Object):
        pass

    class FieldMap(Object):
        pass

    register_parse()

    # call Alice
    a = alice_api.Alice()
    hotel_ids = a.get_all_hotel_ids()

    for hid in hotel_ids:
        fid = a.get_hotel_facility_id(hid)
        response = a.get_hotel_services(hid, fid)

        for sm in response:
            aliceSMId = str(sm['id'])
            try:
                market = Market.Query.get(aliceHotelNumber=str(hid))
                serviceMap = ServiceMap.Query.get(aliceServiceId=aliceSMId, market=market)
                print serviceMap
                options = sm['options']

                for o in options:
                    fieldId = str(o['id'])
                    fieldName = o['name']
                    try:
                        fm = FieldMap.Query.get(aliceFieldId=fieldId, serviceMap=serviceMap,
                                                aliceFieldName=fieldName, aliceServiceId=aliceSMId)
                    except QueryResourceDoesNotExist:
                        field = FieldMap(aliceFieldId=fieldId, serviceMap=serviceMap,
                                         aliceFieldName=fieldName, aliceServiceId=aliceSMId)
                        field.save()

            except (QueryResourceDoesNotExist, QueryResourceMultipleResultsReturned) as e:
                print e
                print str(hid) + " - " + aliceSMId
                pass

