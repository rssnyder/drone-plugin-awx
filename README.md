# drone-plugin-awx

triggers awx jobs from harness

## settings

- `ENDPOINT` - awx endpoint (str)
- `USERNAME` - awx username (str: required unless `TOKEN` is set)
- `PASSWORD` - awx password (str: required unless `TOKEN` is set)
- `TOKEN` - (optional) existing oauth/personal access token; if set, `USERNAME`/`PASSWORD` are not required and no token is requested
- `API_PATH` - (optional) api base path (str: default `api/v2`; use `api/controller/v2` for AAP Platform Gateway deployments)
- `SAVE_TOKEN` - (optional) set awx token as step output (only when authenticating with `USERNAME`/`PASSWORD`)
- `TARGET_HOSTNAME` - (optional) target hostname (str)
- `TARGET_DESC` - (optional) target description (str)
- `ADD_TO_INVENTORY` - (optional) add target to inventory (bool: default false)
- `IGNORE_EXISTING_HOST` - (optional) ignore if host already exists in inventory (bool: default false)
- `INVENTORY_ID` - (optional) inventory id, if not provided, will be created dynamically (int)
- `INVENTORY_NAME` - (optional) inventory name for dynamic inventory (str)
- `INVENTORY_DESC` - (optional) inventory description for dynamic inventory (str)
- `ORGANIZATION_ID` - (optional) awx organization for dynamic inventory (int: default 1)
- `JOB_TEMPLATE_ID` - (optional) job template id (int)
- `EXTRA_VARS` - (optional) extra vars for job (json string)
- `LIMIT` - (optional) limit pattern for job execution (str)

## outputs

- `AWX_TOKEN` - awx token (str: if `SAVE_TOKEN` is true)
- `INVENTORY_ID` - inventory id (int: if inventory is created)
- `JOB_ID` - job id (int: if job is triggered)
- `JOB_STATUS` - job status (str: if job is triggered)
- `JOB_URL` - job url (str: if job is triggered)

## usage

```yaml
- step:
    type: Plugin
    name: awx
    identifier: awx
    spec:
        connectorRef: account.buildfarm_container_registry_cloud
        image: harnesscommunity/drone-plugin-awx
        settings:
            endpoint: http://awx.r.ss
            username: admin
            password: <+secrets.getValue("lab")>
            save_token: "true"
            target_hostname: home.r.ss
            job_template_id: "7"
```

### Ansible Automation Platform (Platform Gateway)

Newer AAP deployments front the controller with a Platform Gateway, which exposes
controller endpoints under `/api/controller/v2/` instead of `/api/v2/`. Set `API_PATH`
accordingly, and optionally supply an existing token to skip the `/tokens/` endpoint:

```yaml
- step:
    type: Plugin
    name: awx
    identifier: awx
    spec:
        image: harnesscommunity/drone-plugin-awx
        settings:
            endpoint: https://aap.example.com
            api_path: api/controller/v2
            token: <+secrets.getValue("aap_token")>
            job_template_id: "12"
            inventory_id: "5"
            add_to_inventory: "true"
            ignore_existing_host: "true"
```
<img width="1090" height="326" alt="image" src="https://github.com/user-attachments/assets/4d33b0b9-7063-4525-83d7-8bcf4d381b13" />
<img width="878" height="370" alt="image" src="https://github.com/user-attachments/assets/d6b65658-3656-47d8-a4a9-b628f860d4f7" />
