#!/usr/bin/env bash
CONTAINER_ID=$1

if [ -z "$CONTAINER_ID" ]; then
  echo "Error: Container ID is required"
  exit 1
fi

# Run multiple commands inside the container
docker exec $CONTAINER_ID /bin/bash -c "
  flask --app sip_pdb db init
  flask --app sip_pdb db migrate
  flask --app sip_pdb db upgrade
  flask --app sip_pdb add-admin-user --username superadmin --password defaultpassword --role superadmin
  flask --app sip_pdb add-admin-user --username ppdb-admin --password defaultpassword --role admin
"