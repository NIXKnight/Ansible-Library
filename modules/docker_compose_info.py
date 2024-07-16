#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import docker
import os
import yaml

# Function to check the status of containers defined in a docker-compose file.
def check_containers_status(compose_file, project_name):
    client = docker.from_env()
    is_any_container_running = False  # Initially assume no container is running.

    # Ensure the compose_file path ends with .yaml or .yml. If not, append 'docker-compose.yaml' to the path.
    if not compose_file.endswith(('.yaml', '.yml')):
        compose_file = os.path.join(compose_file, 'docker-compose.yaml')

    # Check if the compose file exists; if not, return an error message.
    if not os.path.exists(compose_file):
        return None, "The specified docker-compose file does not exist."

    try:
        with open(compose_file, 'r') as file:
            compose_data = yaml.safe_load(file)
            services = compose_data.get('services', {}).keys()
            for service in services:
                service_name_filter = f"{project_name}_{service}"
                containers = client.containers.list(filters={"name": service_name_filter})  # List containers matching the service name.
                # Check if any container for the service is running.
                if any(container.status == 'running' for container in containers):
                    is_any_container_running = True
                    break
    except Exception as e:
        return None, str(e)

    return is_any_container_running, None

def main():
    module = AnsibleModule(
        argument_spec=dict(
            path=dict(type='str', required=True),
            project_name=dict(type='str', required=True),
        ),
        supports_check_mode=True
    )

    compose_path = module.params['path']
    project_name = module.params['project_name']
    is_any_container_running, error = check_containers_status(compose_path, project_name)  # Check the container status.

    # Handle potential errors.
    if error is not None:
        module.fail_json(msg=error)
    else:
        module.exit_json(changed=False, any_container_running=is_any_container_running)

if __name__ == '__main__':
    main()
