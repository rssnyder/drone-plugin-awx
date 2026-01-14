from os import getenv
import stat
from sys import exit
from json import loads
from venv import logger
import logging

from requests import get, post

logging.basicConfig(level=logging.INFO)


def write_outputs(outputs: dict[str, str]):
    """
    write key value outputs to a local file to be rendered in the plugin step

    args:
        outputs (dict[str, str]): string to string mappings
    """

    output_file = open(getenv("DRONE_OUTPUT"), "a")

    for k, v in outputs.items():
        output_file.write(f"{k}={v}\n")

    output_file.close()


def write_secret_outputs(outputs: dict[str, str]):
    """
    write key value outputs to a local file to be rendered in the plugin step as secret

    args:
        outputs (dict[str, str]): string to string mappings
    """

    output_file = open(getenv("HARNESS_OUTPUT_SECRET_FILE"), "a")

    for k, v in outputs.items():
        output_file.write(f"{k}={v}\n")

    output_file.close()


def check_env(variable: str, default: str = None):
    """
    resolves an environment variable, returning a default if not found
    if no default is given, variable is considered required and must be set
    if not, logging.info the required var and fail the program

    args:
        variable (str): environment variable to resolve
        default (str): default value for variable if not found

    returns:
        str: the value of the variable
    """

    value = getenv(variable, default)
    if value == None:
        # if we are missing a PLUGIN_ var, ask the user for the expected setting
        stripped_variable = variable if "PLUGIN_" not in variable else variable[7:]
        logging.info(f"{stripped_variable} required")
        exit(1)

    return value


def get_token(username: str, password: str, endpoint: str):
    """
    get a token from awx

    args:
        username (str): username to use for authentication
        password (str): password to use for authentication
        endpoint (str): endpoint to use for authentication

    returns:
        str: the token
    """
    resp = post(f"{endpoint}/api/v2/tokens/", auth=(username, password))

    try:
        resp.raise_for_status()
    except Exception as e:
        logging.error(resp.text)
        raise e
    return resp.json()["token"]


def create_inventory(
    token: str, endpoint: str, name: str, description: str, organization: int
):
    """
    create an inventory in awx

    args:
        token (str): token to use for authentication
        endpoint (str): endpoint to use for authentication
        name (str): name of the inventory
        description (str): description of the inventory
        organization (int): organization to use for the inventory

    returns:
        int: the id of the inventory
    """
    resp = post(
        f"{endpoint}/api/v2/inventories/",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": name, "description": description, "organization": organization},
    )

    try:
        resp.raise_for_status()
    except Exception as e:
        logging.error(resp.text)
        raise e
    return resp.json()["id"]


def add_host_to_inventory(
    token: str, endpoint: str, inventory_id: int, name: str, description: str
):
    """
    add a host to an inventory in awx

    args:
        token (str): token to use for authentication
        endpoint (str): endpoint to use for authentication
        inventory_id (int): id of the inventory to add the host to
        name (str): name of the host
        description (str): description of the host

    returns:
        None
    """
    resp = post(
        f"{endpoint}/api/v2/inventories/{inventory_id}/hosts/",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": name, "description": description},
    )

    try:
        resp.raise_for_status()
    except Exception as e:
        logging.error(resp.text)
        raise e


def trigger_job(
    token: str, endpoint: str, job_template_id: int, inventory_id: int, extra_vars: dict
):
    """
    trigger a job in awx

    args:
        token (str): token to use for authentication
        endpoint (str): endpoint to use for authentication
        job_template_id (int): id of the job template to use
        inventory_id (int): id of the inventory to use
        extra_vars (dict): extra variables to pass to the job

    returns:
        int: the id of the job
    """
    resp = post(
        f"{endpoint}/api/v2/job_templates/{job_template_id}/launch/",
        headers={"Authorization": f"Bearer {token}"},
        json={"inventory": inventory_id, "extra_vars": extra_vars},
    )

    try:
        resp.raise_for_status()
    except Exception as e:
        logging.error(resp.text)
        raise e
    return resp.json()["id"]


def wait_for_job_completion(token: str, endpoint: str, job_id: int):
    """
    wait for a job to complete in awx

    args:
        token (str): token to use for authentication
        endpoint (str): endpoint to use for authentication
        job_id (int): id of the job to wait for

    returns:
        None
    """

    status = None
    while status in [None, "pending", "waiting", "running"]:
        resp = get(
            f"{endpoint}/api/v2/jobs/{job_id}/",
            headers={"Authorization": f"Bearer {token}"},
        )

        try:
            resp.raise_for_status()
        except Exception as e:
            logging.error(resp.text)
            raise e

        status = resp.json()["status"]
        logging.debug(f"Job running with status: {status}")

    return status


def main():
    endpoint = check_env("PLUGIN_ENDPOINT")
    username = check_env("PLUGIN_USERNAME")
    password = check_env("PLUGIN_PASSWORD")
    save_token = check_env("PLUGIN_SAVE_TOKEN", "")

    # inventory settings
    inventory_id = check_env("PLUGIN_INVENTORY_ID", "")
    inventory_name = check_env("PLUGIN_INVENTORY_NAME", "")
    inventory_description = check_env("PLUGIN_INVENTORY_DESC", "created by harness")
    organization = int(check_env("PLUGIN_ORGANIZATION_ID", "1"))

    # target host settings
    target_hostname = check_env("PLUGIN_TARGET_HOSTNAME", "")
    target_hostnames = loads(check_env("PLUGIN_TARGET_HOSTNAMES", "[]"))
    target_description = check_env("PLUGIN_TARGET_DESC", "created by harness")
    add_to_inventory = check_env("PLUGIN_ADD_TO_INVENTORY", "")

    # job settings
    job_template_id = check_env("PLUGIN_JOB_TEMPLATE_ID", "")
    extra_vars = check_env("PLUGIN_EXTRA_VARS", "{}")

    outputs = {}

    token = get_token(username, password, endpoint)
    if save_token:
        write_secret_outputs({"AWX_TOKEN": token})

    # if job template is passed, trigger it
    if job_template_id:
        logging.info(f"Job requested: {job_template_id}")

        # hostname must be provided at minimum
        if not (target_hostname or target_hostnames):
            logging.error("No target hostnames provided")
            return

        if target_hostname:
            target_hostnames.append(target_hostname)

        # if no inventory ID is provided, create one
        if not inventory_id:
            logging.info("No inventory ID provided, one will be created")

            # organization must be provided at minimum
            if not organization:
                logging.error("No organization provided")
                return

            inventory_id = create_inventory(
                token,
                endpoint,
                inventory_name or target_hostname or target_hostnames[0],
                inventory_description,
                organization,
            )
            outputs["INVENTORY_ID"] = inventory_id
            logging.info(f"Created inventory with ID: {inventory_id}")

            # add target host to inventory
            for hostname in target_hostnames:
                add_host_to_inventory(
                    token,
                    endpoint,
                    inventory_id,
                    hostname,
                    target_description,
                )
                logging.info(f"Added host to inventory {inventory_id}: {target_hostname}")

        elif add_to_inventory:
            # add target host to existing inventory
            add_host_to_inventory(
                token,
                endpoint,
                inventory_id,
                target_hostname,
                target_description,
            )
            logging.info(
                f"Added host to existing inventory {inventory_id}: {target_hostname}"
            )

        # trigger job
        job_id = trigger_job(
            token,
            endpoint,
            job_template_id,
            inventory_id,
            loads(extra_vars),
        )
        outputs["JOB_ID"] = job_id

        # wait for job to complete
        status = wait_for_job_completion(
            token,
            endpoint,
            job_id,
        )
        outputs["JOB_STATUS"] = status
        outputs["JOB_URL"] = f"'{endpoint}/#/jobs/playbook/{job_id}/output'"

        logger.info(f"Job completed with status: {status}")

    write_outputs(outputs)


if __name__ == "__main__":
    main()
