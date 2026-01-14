# drone-plugin-awx

triggers awx jobs from harness

## settings

- `ENDPOINT` - awx endpoint (str)
- `USERNAME` - awx username (str)
- `PASSWORD` - awx password (str)
- `SAVE_TOKEN` - (optional) set awx token as step output
- `TARGET_HOSTNAME` - (optional) target hostname (str)
- `TARGET_DESC` - (optional) target description (str)
- `ADD_TO_INVENTORY` - (optional) add target to inventory (bool: default false)
- `INVENTORY_ID` - (optional) inventory id, if not provided, will be created dynamically (int)
- `INVENTORY_NAME` - (optional) inventory name for dynamic inventory (str)
- `INVENTORY_DESC` - (optional) inventory description for dynamic inventory (str)
- `ORGANIZATION_ID` - (optional) awx organization for dynamic inventory (int: default 1)
- `JOB_TEMPLATE_ID` - (optional) job template id (int)
- `EXTRA_VARS` - (optional) extra vars for job (json string)

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
<img width="1090" height="326" alt="image" src="https://github.com/user-attachments/assets/4d33b0b9-7063-4525-83d7-8bcf4d381b13" />
<img width="878" height="370" alt="image" src="https://github.com/user-attachments/assets/d6b65658-3656-47d8-a4a9-b628f860d4f7" />
