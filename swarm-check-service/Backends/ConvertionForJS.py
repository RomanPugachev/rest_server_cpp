import time
from datetime import datetime, timezone
from . import ServiceActions
from . import ServiceContainerActions


class TimeRangeItemForVis:
    def __init__(self, container : ServiceContainerActions.Container):
        self.id = container.container_id
        self.group = container.service_name
        container_start_time_known = False
        try:
            self.start = min([action.timestamp_nano for action in container.actions if "start" in action.action_name])
            container_start_time_known = True
        except Exception:
            self.start = int(datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1e9)
        currently_running = False
        try:
            self.end = max([action.timestamp_nano for action in container.actions if ("stop" in action.action_name or "exit" in action.action_name or "kill" in action.action_name)])
        except Exception:
            currently_running = True
            self.end = -1
        if currently_running:
            self.content = "Currently running: starttime " + (str(nanoseconds_to_datetime(self.start)) if container_start_time_known else "unknown")
        else:
            time_range = nanoseconds_to_time(int(time.time_ns()) - self.start)
            self.content = f'Container worked for: {time_range}' + ('' if container_start_time_known else ' or more')
        self.title = f'Container {self.id}'
        self.backend_path = self.id

    def __str__(self):
        return (self.to_dict()).__str__()

    def to_dict(self):
        return {
            "id" : self.id,
            "group" : self.group,
            "start" : self.start,
            "end" : self.end,
            "content" : self.content,
            "continuous": self.end == -1,
            "title" : self.title,
            "backend_path" : self.backend_path
        }


class TimePointItemForVis:
    def __init__(self, service_action : ServiceActions.ServiceAction):
        self.id = (f'Service {service_action.service_name}(id={service_action.actor_id})'
                   f': {service_action.action} at {service_action.timestamp_nano}')
        self.group = service_action.service_name
        self.timestamp = service_action.timestamp_nano
        self.type = "point"
        self.content = service_action.action

    def __str__(self):
        return (self.to_dict()).__str__()

    def to_dict(self):
        return {
            "id": self.id,
            "group": self.group,
            "timestamp": self.timestamp,
            "type": self.type,
            "content": self.content
        }


def get_groups_and_items_from_service_container_actions_entries(RESULT_LIST_FOR_CONTAINER_EVENTS : list[
    ServiceContainerActions.Service]):
    groups = set()
    items = list()
    for service in RESULT_LIST_FOR_CONTAINER_EVENTS:
        for container in service.containers:
            items.append(TimeRangeItemForVis(container))
        groups.add(service.service_name)
    return groups, items

def get_groups_and_items_from_service_actions_entries(RESULT_LIST_FOR_SERVICE_EVENTS: list[
    ServiceActions.ServiceAction]) \
        -> tuple[set, list[TimePointItemForVis]]:
    groups = set()
    items = list()
    for service_action in RESULT_LIST_FOR_SERVICE_EVENTS:
        groups.add(service_action.service_name)
        items.append(TimePointItemForVis(service_action))
    return groups, items

def merge_groups_and_items_from_services_and_containers_actions(container_groups : set, container_items : list[TimePointItemForVis],
                                                                service_groups : set, service_items : list[TimeRangeItemForVis]) \
        -> tuple[set, list]:
    container_groups.update(service_groups)
    items = container_items + service_items
    return container_groups, items



def nanoseconds_to_time(nanoseconds: int) -> str:
    seconds = nanoseconds // 1_000_000_000
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return f"{days} d:{hours:02d} h:{minutes:02d} m:{seconds:02d} s"



def nanoseconds_to_datetime(timestamp_nano : int) -> str:
    timestamp_seconds = timestamp_nano / 1e9
    dt = datetime.fromtimestamp(timestamp_seconds, tz=timezone.utc)
    return dt.strftime("%Y.%m.%d %H:%M:%S%Z")


