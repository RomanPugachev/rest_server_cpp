from . import ServiceContainerActions
from . import ServiceActions
from . import ConvertionForJS
import os
import requests

RESULT_LIST_FOR_CONTAINER_EVENTS = list()
QUERY_FOR_CONTAINER_EVENTS = '{job="docker_events"} | json | Type = "container" and Action =~ "start|stop|update|kill"'

RESULT_LIST_FOR_SERVICE_EVENTS = list()
QUERY_FOR_SERVICE_EVENTS = '{job="docker_events"} | json | Type = "service" and Action =~ "create|remove|update"'


BASE_LOKI_URL = os.getenv("BASE_LOKI_URL", 'http://loki:3100/loki/api/v1')

limit = int(os.environ.get('LIMIT', 0))

def update_logs_info():
    update_logs_info_for_container_events()
    update_logs_info_for_service_events()


def update_logs_info_for_container_events():
    global RESULT_LIST_FOR_CONTAINER_EVENTS, BASE_LOKI_URL, limit, QUERY_FOR_CONTAINER_EVENTS
    try:
        if limit > 0:
            raw_response = requests.get(f"{BASE_LOKI_URL}/query_range",params={"query" : QUERY_FOR_CONTAINER_EVENTS, "limit": limit})
        else:
            raw_response = requests.get(f"{BASE_LOKI_URL}/query_range", params={"query": QUERY_FOR_CONTAINER_EVENTS})
        if raw_response.status_code != 200:
            print("Failed to get response from Loki")
            raise Exception(raw_response.content)
        RESULT_LIST_FOR_CONTAINER_EVENTS = ServiceContainerActions.ServiceContainerActionEntry.getServicesContainersDataByLokiResponse(raw_response)
    except Exception as e:
        print(f"Error sending request: {e}")

def update_logs_info_for_service_events():
    global RESULT_LIST_FOR_SERVICE_EVENTS, BASE_LOKI_URL, limit, QUERY_FOR_SERVICE_EVENTS
    try:
        if limit > 0:
            raw_response = requests.get(f"{BASE_LOKI_URL}/query_range",
                                        params={"query": QUERY_FOR_SERVICE_EVENTS, "limit": limit})
        else:
            raw_response = requests.get(f"{BASE_LOKI_URL}/query_range", params={"query": QUERY_FOR_SERVICE_EVENTS})
        if raw_response.status_code != 200:
            print("Failed to get response from Loki")
            raise Exception(raw_response.content)
        RESULT_LIST_FOR_SERVICE_EVENTS = ServiceActions.ServiceAction.getServicesActionsDataByLokiResponse(raw_response)
    except Exception as e:
        print(f"Error sending request: {e}")


def get_service_info(service_name):
    global RESULT_LIST_FOR_CONTAINER_EVENTS, RESULT_LIST_FOR_SERVICE_EVENTS
    update_logs_info()
    if service_name is None:
        return RESULT_LIST_FOR_CONTAINER_EVENTS
    for service in RESULT_LIST_FOR_CONTAINER_EVENTS:
        if service.service_name == service_name:
            return service
    return "Your service is not in found"



def getBackendTimeLinesGlobalInfo():
    global RESULT_LIST_FOR_CONTAINER_EVENTS
    update_logs_info()
    groups_container, items_container = ConvertionForJS.get_groups_and_items_from_service_container_actions_entries(RESULT_LIST_FOR_CONTAINER_EVENTS)
    groups_service, items_service = ConvertionForJS.get_groups_and_items_from_service_actions_entries(RESULT_LIST_FOR_SERVICE_EVENTS)
    merged_groups, merged_items = ConvertionForJS.merge_groups_and_items_from_services_and_containers_actions(groups_container, items_container, groups_service, items_service)
    result_dict = {"groups" : [{"id" : service_name, "content" : service_name} for service_name in merged_groups], "items" : [item.to_dict() for item in merged_items]}
    return result_dict