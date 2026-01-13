# drone-plugin-awx

triggers awx jobs from drone

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
- `ORGANIZATION` - (optional) awx organization for dynamic inventory (int)
- `JOB_TEMPLATE_ID` - (optional) job template id (int)
- `EXTRA_VARS` - (optional) extra vars for job (json string)
