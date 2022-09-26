import kopf
import logging
from amqpstorm import management
from kubernetes import client, config
import base64
import os

API = management.ManagementApi(os.environ.get("RABBITMQ_URL"),
                                os.environ.get("RABBITMQ_USER"),
                                os.environ.get("RABBITMQ_PASSWORD"),
                                verify=os.environ.get("RABBITMQ_VERIFY"))

config.load_incluster_config()

kubeapi = client.CoreV1Api()

@kopf.on.create('rabbitmqusers.kopf.dev')
def create_fn(body, spec, name, namespace, logger, **kwargs):
    logging.debug(f"A handler is called with body: {body}")

    username = spec.get('username')
    vhost = spec.get('vhost')

    # Get secret
    passwordobj = spec.get('password')

    secret = kubeapi.read_namespaced_secret(passwordobj['name'], namespace).data
    password = str(base64.b64decode(secret[passwordobj['key']]))

    # Create virtualhost.
    try:
        API.virtual_host.create(vhost)
        logging.info(f"Virtual Host '{vhost}' created")
    except management.ApiConnectionError as why:
        logging.error('Connection Error: %s' % why)
    except management.ApiError as why:
        logging.error('Failed to create virtual host: %s' % why)

    # Create user.
    try:
        API.user.create(username, password, tags=vhost)
        logging.info(f"User '{username}' created")
    except management.ApiConnectionError as why:
        logging.error('Connection Error: %s' % why)
    except management.ApiError as why:
        logging.error('Failed to create user: %s' % why)

    # Update the Virtual Host permissions for user.
    try:
        API.user.set_permission(username,
                                virtual_host=vhost,
                                configure_regex='.*',
                                write_regex='.*',
                                read_regex='.*')
        logging.info(f"Permission updated  on virtual Host called: {vhost} for {username}")
    except management.ApiConnectionError as why:
        logging.error('Connection Error: %s' % why)        
    except management.ApiError as why:
        logging.error('Failed to update permissions: %s' % why)

@kopf.on.delete('rabbitmqusers.kopf.dev')
def delete_fn(spec, name, namespace, logger, **kwargs):
    username = spec.get('username')
    vhost = spec.get('vhost')

    # Delete virtual_host
    try:
        API.virtual_host.delete(vhost)
        logging.info(f"Virtual Host called: {vhost} deleted")
    except management.ApiConnectionError as why:
        logging.error('Connection Error: %s' % why)
    except management.ApiError as why:
        logging.error('Failed to delete virtual host: %s' % why)

    # Delete user
    try:
        API.user.delete(username)
        logging.error(f'User deleted {username}')
    except management.ApiConnectionError as why:
        logging.error('Connection Error: %s' % why)
    except management.ApiError as why:
        logging.error('Failed to delete user: %s' % why)