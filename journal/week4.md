# Week 4 — Postgres and RDS

# Requirements

## Update `backend-flask/requirements.txt`

Add the following python dependencies to the requirements file
```
psycopg[binary]
psycopg[pool]
```

# Workspace

## Update `.gitpod.yml`
The Gitpod IP address changes everytime a new workspace is launched. For a connection to the RDS to be established we need to update the ip address in the security group of the RDS. This can be done by adding the following command to the postgres task in `.gitpod.yml`.

```yml
command: |
      export GITPOD_IP=$(curl ifconfig.me)
      source "$THEIA_WORKSPACE_ROOT/backend-flask/bin/rds-update-sg-rule"
```

This command exports the IP address into an environment variable and runs the rds-update-sg-rule script. We will define this script below.

# Docker

## Update `docker-compose.yml`:

Add the following environment variable to the backend in docker-compose file

```yml
CONNECTION_URL: "${PROD_CONNECTION_URL}"
```

# Database

## Create `backend-flask/lib/db.py`:

In this new file we will create the database class that will allow us to interact with our RDS instance.

```python
from psycopg_pool import ConnectionPool
import os, sys, re
from flask import current_app as app

class DB:
  def __init__(self):
    self.init_pool()

  def init_pool(self):
    connection_url = os.getenv("CONNECTION_URL")
    self.pool = ConnectionPool(connection_url)

  def query_commit(self, sql, params={}): #commits data (i.e. insert)
    ...
  def print_sql_err(self,err):
    ...
  def query_wrap_object(self, template):
    ...
  def query_wrap_array(self, template):
    ...
  def query_object_json(self, sql, params={}): #returns json object
    ...
  def query_array_json(self, sql, params={}): #returns array of json objects
    ...
  def template(self, *args):
    ...
  def print_sql(self, title, sql):
    ...

db = DB()
```

We can now call these methods to interact with the database.

# Post Confirmation Lambda

Create the following python lambda to insert user data into the database whenever a cognito user signs up. This will automtically be triggered by Cognito.

```python
import json
import psycopg2
import os

def lambda_handler(event, context):
    user = event['request']['userAttributes']
    try:
        user_display_name = user['name']
        user_email = user['email']
        user_handle = user['preferred_username']
        user_cognito_id = user['sub']

        sql = f"""
            INSERT INTO users (display_name, email, handle, cognito_user_id)
            VALUES(%s, %s, %s, %s)
            """

        conn = psycopg2.connect(
            os.getenv('CONNECTION_URL')
        )
        cur = conn.cursor()

        params = [
            user_display_name, 
            user_email, 
            user_handle, 
            user_cognito_id
            ]

        cur.execute(sql, *params)
        conn.commit() 

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    finally:
        if conn is not None:
            cur.close()
            conn.close()
            print('Database connection closed.')

    return event
```
# Scripts

We can create shell scripts to perform repetitive tasks, for example to setup and connect our databases or to interact with the aws-cli. Here is a list of scripts we've implemented:

- `backend-flask/bin/db-connect`
- `backend-flask/bin/db-create`
- `backend-flask/bin/db-drop`
- `backend-flask/bin/db-schema-load`
- `backend-flask/bin/db-seed`
- `backend-flask/bin/db-sessions`
- `backend-flask/bin/db-setup`
- `backend-flask/bin/rds-update-sg-rule`

For example, here is the script that updates the security group rules we mentioned earlier. We added some formatting to be able to better view it in the terminal.

```bash
#! /usr/bin/bash

CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL="rds-update-sg-rule"
printf "${CYAN}== ${LABEL}${NO_COLOR}\n"

aws ec2 modify-security-group-rules \
    --group-id $DB_SG_ID \
    --security-group-rules "SecurityGroupRuleId=$DB_SG_RULE_ID,SecurityGroupRule={Description=GITPOD,IpProtocol=tcp,FromPort=5432,ToPort=5432,CidrIpv4=$GITPOD_IP/32}"
```

# SQL

