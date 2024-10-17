import requests

def get_docker_metadata():
    try: # Query Docker's API to get the container's information
        container_info = requests.get("http://localhost:2375/containers/self/json").json()
        container_id = container_info['Id']

        # Fetch task information related to the service (for replica ID)
        task_info = requests.get("http://localhost:2375/tasks?filters={\"desired-state\":{\"running\":true}}").json()

        # Find task corresponding to current container
        replica_id = None
        app_version = None
        for task in task_info:
            if task['Status']['ContainerStatus']['ContainerID'] == container_id:
                # Get replica ID from the task's slot number
                replica_id = task['Slot']
                # Get app version from service labels or task definition
                service_info = requests.get(f"http://localhost:2375/services/{task['ServiceID']}").json()
                app_version = service_info['Spec']['Labels'].get('app_version', 'Unknown')
                break

        # Return the extracted info
        return container_id, replica_id, app_version
    except Exception as e:
        print(f"Error fetching Docker metadata: {e}")
        return 'Unknown', 'Unknown', 'Unknown'