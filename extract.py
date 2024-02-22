import argparse
import json
import os
import uuid
import datetime
import yaml
from collector import Collector
from collector.jira import Jira
from collector.nullify import Nullify
import boto3
import botocore

def replace_env_variable(input_string):
    if input_string is None:
        return input_string

    # Find all occurrences of ${...} in the input string
    start_index = input_string.find('${')
    while start_index != -1:
        end_index = input_string.find('}', start_index + 2)
        
        if end_index == -1:
            break  # Exit if closing '}' not found

        # Extract the variable name between ${ and }
        variable_name = input_string[start_index + 2:end_index]

        # Get the environment variable value
        if not variable_name in os.environ:
            log('ERROR',f'Environment variable {variable_name} is not found')
            return None

        env_value = os.environ.get(variable_name, f'${{{variable_name}}}')

        # Replace the ${...} with the environment variable value
        input_string = input_string[:start_index] + env_value + input_string[end_index + 1:]

        # Find the next occurrence of ${...}
        start_index = input_string.find('${', end_index + 1)

    return input_string

def main():
    parser = argparse.ArgumentParser(description='Data Extractor')
    parser.add_argument('-config',help='Specify the yaml config file',default='config.yml')
    args = parser.parse_args()

    C = Collector()

    # here we define which variables we expect for every plugin.
    # - define a variable, and its default value.
    VARS = {
        "jira_search" : {
            "endpoint"  : None,
            "username"  : None,
            "password"  : None,
            "jql"       : None
        },
        "nullify_sca_events" : {
            "endpoint"      : None,
            "githubOwnerId" : None,
            "token"         : None,
            "fromTime"      : (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=31)).strftime('%Y-%m-%dT%H:%M:%SZ')
        },
        "write_json" : {
            "output" : "data/$TABLE/$YEAR/$MONTH/$DAY/$UUID.json"
        },
        "write_s3" : {
            "bucket" : None,
            "key" : "data/$TABLE/$YEAR/$MONTH/$DAY/$UUID.json"
        }
    }

    # == first we parse the config to find all the sources, and validate that we have all their required inputs
    source = []
    dest = []
    with open(args.config,'rt',encoding='UTF-8') as y:
        for cfg in yaml.safe_load_all(y):

            # every config must have "plugin"
            if not 'plugin' in cfg:
                C.log('ERROR','No "plugin" in config')
            else:
                if not cfg['plugin'] in VARS:
                    C.log('ERROR',f"Unknown plugin \"{cfg['plugin']}\" specified")
                else:
                    if not 'variables' in cfg:
                        C.log('ERROR','No "variables" in config')
                    else:
                        V = {}
                        for k in VARS[cfg['plugin']]:
                            d = VARS[cfg['plugin']][k]
                            v = cfg['variables'].get(k)

                            # == overwrite the value if its none, and we have a default
                            if v is None and d is not None:
                                v = d

                            v = replace_env_variable(v)
                            if v is None:
                                C.log('ERROR',f"Variable {cfg['plugin']} / {k} is not set")
                                break
                            else:
                                V[k] = v
                        if 'table' not in cfg:
                            cfg['table'] = cfg['plugin']
                            C.log('WARNING',f"Setting table to {cfg['plugin']}")
                        
                        # -- if we made it this far, we have everything we need to kick off the plugin
                        if cfg['plugin'].startswith('write_'):
                            dest.append({ 'plugin' : cfg['plugin'], 'table' : cfg['table'], 'variables' : V})
                        else:
                            source.append({ 'plugin' : cfg['plugin'], 'table' : cfg['table'], 'variables' : V})

    # now lets loop through it all
    V = {
        'YYYY'      : datetime.datetime.now(datetime.UTC).strftime('%Y'),
        'MM'        : datetime.datetime.now(datetime.UTC).strftime('%m'),
        'DD'        : datetime.datetime.now(datetime.UTC).strftime('%d')
    }
    for S in source:
        V['UUID'] = str(uuid.uuid4())
        V['TABLE'] = S['table']
        V['PLUGIN'] = S['plugin']

        C.log('INFO',f"Starting source {S['plugin']} - {S['table']}")
        data = []

        if S['plugin'] == 'jira_search':
            data = Jira(**S['variables']).search(S['variables']['jql'])

        if S['plugin'] == 'nullify_sca_events':
            data = Nullify(**S['variables']).sca_events(S['variables']['fromTime'])

        for D in dest:
            if len(data) != 0:
                C.log('INFO',f"Starting destination {D['plugin']}")

                if D['plugin'] == 'write_json':
                    path = D['variables']['output']
                    for x in V:
                        path = path.replace(f"${x}",V[x])
                    
                    C.log('INFO',f"Writing to local path = {path}")
                    os.makedirs(os.path.dirname(path),exist_ok = True)        
                    with open(path,"wt",encoding='UTF-8') as q:
                        q.write(json.dumps(data,default=str))
                    
                if D['plugin'] == 'write_s3':
                    key = D['variables']['key']
                    for x in V:
                        key = key.replace(f"${x}",V[x])
                        try:
                            boto3.client('s3').put_object(
                                Body = json.dumps(data,default=str),
                                Bucket = D['variables']['bucket'],
                                Key = key,
                                ACL='bucket-owner-full-control'
                            )
                        except botocore.exceptions.ClientError as error:
                            C.log("ERROR",f"s3.put_object - {error.response['Error']['Code']}")
            else:
                C.log('WARNING','No data to be written')

if __name__=='__main__':
    main()
