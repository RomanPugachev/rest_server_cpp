from collections import defaultdict

import requests
import json
from opentelemetry.sdk.resources import CONTAINER_NAME

class Action:
    def __init__(self, container_id, action_name, timestamp_nano):
        self.container_id = container_id
        self.action_name = action_name
        self.timestamp_nano = timestamp_nano

    def __str__(self):
        return (self.to_dict()).__str__()

    def to_dict(self):
        return {"container_id" : self.container_id,
                "action_name" : self.action_name,
                "timestamp_nano" : self.timestamp_nano}


class Container:
    def __init__(self, service_name, image, container_id, actions : list[Action]):
        self.service_name = service_name
        self.image = image
        self.container_id = container_id
        self.actions = actions

    def __str__(self):
        return (self.to_dict()).__str__()

    def to_dict(self):
        return {
            "service_name" : self.service_name,
            "image": self.image,
            "container_id" : self.container_id,
            "actions" : [action.to_dict() for action in self.actions]
        }


class Service:
    def __init__(self, service_name, containers : list[Container]):
        self.service_name = service_name
        self.containers = containers

    def __str__(self):
        return (self.to_dict()).__str__()

    def to_dict(self):
        return {
            "service_name" : self.service_name,
            "containers" : [container.to_dict() for container in self.containers]
        }

    def __iter__(self):
        return iter(self.containers)

class ServiceContainerActionEntry:
    def __init__(self,  service_name, image, container_id,  action, timestamp_nano):
        self.service_name = service_name
        self.image = image
        self.container_id = container_id
        self.action = action
        self.timestamp_nano = timestamp_nano

    def __str__(self):
        return (self.to_dict()).__str__()

    def to_dict(self):
        return {
            'service_name' : self.service_name,
            "image" : self.image,
            "container_id" : self.container_id,
            "action" : self.action,
            "timestamp_nano": self.timestamp_nano
        }

    @staticmethod
    def getServicesContainersDataByLokiResponse(raw_response) -> list['Service']:
        entries = ServiceContainerActionEntry.getParsedEntries(raw_response)
        return ServiceContainerActionEntry.createListOfServices(entries)

    @staticmethod
    def getParsedEntries(raw_response) -> list['ServiceContainerActionEntry']:
        json_response = raw_response.json()
        results = list(json_response["data"]["result"])
        entries =list()
        for entry in results:
            entries.append(ServiceContainerActionEntry.parse_entry(entry))
        return entries


    @staticmethod
    def parse_entry(entry : dict) -> 'ServiceContainerActionEntry':
        try:
            entry_dict = json.loads(entry["values"][0][1])

            SERVICE_NAME = entry["stream"]["Actor_Attributes_com_docker_swarm_service_name"]
            IMAGE = entry_dict["Actor"]["Attributes"]["image"]
            SERVICE_CONTAINER_ID = entry_dict["id"]
            action_value = entry["stream"]["Action"]
            ACTION = action_value[:action_value.find(":")] if action_value.find(":") != -1 else action_value
            TIMESTAMP = entry_dict["timeNano"]
        except Exception as e:
            print(f"Error parsing entry: {e}")
            raise RuntimeWarning(f"Couldn't parse entry: {entry}")
        return ServiceContainerActionEntry(SERVICE_NAME, IMAGE, SERVICE_CONTAINER_ID, ACTION, TIMESTAMP)


    @staticmethod
    def createListOfServices(entries : list['ServiceContainerActionEntry']) -> list['Service']:
        services_dict = defaultdict(lambda: defaultdict(list))

        # Step 1: Group entries by service name and container id
        for entry in entries:
            services_dict[entry.service_name][entry.container_id].append(entry)

        # Step 2: Create Service objects
        extracted_services = []
        for service_name, containers_dict in services_dict.items():
            containers = []

            # Step 3: Create Container objects
            for container_id, entries in containers_dict.items():
                actions = []

                # Step 4: Create Action objects for each container
                for entry in entries:
                    action = Action(entry.container_id, entry.action, entry.timestamp_nano)
                    actions.append(action)

                # Create the Container object
                container = Container(service_name, entries[0].image, container_id, actions)
                containers.append(container)

            # Create the Service object
            service = Service(service_name, containers)
            extracted_services.append(service)
        return extracted_services








# EXAMPLE OF entry_dict:
# {
#     "status" : "exec_start: /bin/sh -c wget --quiet --tries=1 --spider $CADVISOR_HEALTHCHECK_URL || exit 1",
#     "id" : "e950fad5f8d391a9568c48e6e58452e17f2399fab540a6d39923b9ca7ac4e61a",
#     "from" : "fefx/gcr.io.cadvisor.cadvisor:v0.49.1@sha256:00ff3424f13db8d6d62778253e26241c45a8d53343ee09944a474bf88d3511ac",
#     "Type" : "container",
#     "Action" : "exec_start: /bin/sh -c wget --quiet --tries=1 --spider $CADVISOR_HEALTHCHECK_URL || exit 1",
#     "Actor" : {
#         "ID" : "e950fad5f8d391a9568c48e6e58452e17f2399fab540a6d39923b9ca7ac4e61a",
#         "Attributes" : {
#             "com.docker.stack.namespace" : "grafana",
#             "com.docker.swarm.node.id" : "4jvm3w7jlynhv9x5zgsgqhtb3",
#             "com.docker.swarm.service.id" : "ckxcz6zikt4jrvfrmdfdeyjze",
#             "com.docker.swarm.service.name" : "grafana_cadvisor",
#             "com.docker.swarm.task" : "",
#             "com.docker.swarm.task.id" : "nfg4jb9wgcwzwoga5thi0k8s3",
#             "com.docker.swarm.task.name" : "grafana_cadvisor.1.nfg4jb9wgcwzwoga5thi0k8s3",
#             "execID" : "edbf7063b03c1028a09f0fe287f6738ee21d9d213f8decc27c6651955efb5f21",
#             "image" : "fefx/gcr.io.cadvisor.cadvisor:v0.49.1@sha256:00ff3424f13db8d6d62778253e26241c45a8d53343ee09944a474bf88d3511ac",
#             "name" : "grafana_cadvisor.1.nfg4jb9wgcwzwoga5thi0k8s3"
#         }
#     },
#     "scope" : "local",
#     "time" : 1729184717,
#     "timeNano" : 1729184717752726354
# }



