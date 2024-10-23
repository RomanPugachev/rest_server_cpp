import json
from datetime import datetime, timezone
import requests
import time



class ServiceAction:
    def __init__(self):
        self.actor_id = "default_actor_id"
        self.service_name = "default_service_name"
        self.action = "default_action_name"
        self.timestamp_nano = int(datetime.now().replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc).timestamp() * 1e9)

    def __init__(self, actor_id : str, service_name : str, action : str, timestamp_nano : int):
        self.actor_id = actor_id
        self.service_name = service_name
        self.action = action
        self.timestamp_nano = timestamp_nano

    def to_dict(self):
        return {
            "service_name": self.service_name,
            "action": self.action,
            "timestamp_nano": self.timestamp_nano
        }

    def __str__(self):
        return self.to_dict().__str__()

    @staticmethod
    def getServicesActionsDataByLokiResponse(raw_response) -> list['ServiceAction']:
        json_response = raw_response.json()
        results = list(json_response["data"]["result"])
        service_actions_list = list()
        for current_result_dict in results:  # Every result is a dict which corresponds to one ServiceAction
            current_action_dict_from_json = json.loads(current_result_dict['values'][0][1])
            current_service_id = current_action_dict_from_json['Actor']['ID']
            current_service_name = current_result_dict["stream"]["Actor_Attributes_name"]
            current_action_name = current_action_dict_from_json['Action']
            current_timestamp_nano = int(current_action_dict_from_json['timeNano'])
            service_actions_list.append(ServiceAction(current_service_id, current_service_name, current_action_name, current_timestamp_nano))
        return service_actions_list