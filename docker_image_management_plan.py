#!/usr/bin/env python

from ansible.module_utils.basic import AnsibleModule
import docker
import traceback

def get_docker_image_tags(image_name, client):
    image_tags = []
    # List all images
    for image in client.images.list():
        for tag in image.tags:
            # Filter tags that start with the image name
            if tag.startswith(image_name):
                image_tags.append(tag)
    return image_tags

def get_image_management_plan(images, client):
    plan = {}
    for identifier, image_info in images.items():
        image_name = image_info['name']
        provided_tag = image_info.get('tag', 'latest')  # Default to 'latest' if not specified
        full_image_name = f"{image_name}:{provided_tag}"

        existing_tags = get_docker_image_tags(image_name, client)
        provided_tag_present = any(tag for tag in existing_tags if tag == full_image_name)

        # Initialize the plan for this identifier
        plan[identifier] = {'to_pull': [], 'to_remove': []}

        # Add to pull list if not present
        if not provided_tag_present:
            plan[identifier]['to_pull'].append(full_image_name)

        # Prepare tags for deletion (excluding the provided tag)
        for tag in existing_tags:
            if tag != full_image_name:
                plan[identifier]['to_remove'].append(tag)

    return plan

def main():
    module = AnsibleModule(
        argument_spec=dict(
            images=dict(type='dict', required=True),
        ),
        supports_check_mode=True
    )

    images = module.params['images']
    client = docker.from_env()

    try:
        plan = get_image_management_plan(images, client)
        module.exit_json(changed=False, plans=plan)
    except Exception as e:
        module.fail_json(msg="Failed to retrieve Docker image tags.", exception=traceback.format_exc())

if __name__ == '__main__':
    main()
