import json
import os
import uuid
import datetime
from collector.jira import Jira
from collector.nullify import Nullify
from collector.snyk import Snyk
import boto3
import botocore

def variables(X):
    data = {}
    for x in X:
        if X[x] is not None:
            data[x] = X[x]
        if x not in os.environ:
            if data.get(x) is None:
                print(f"Variable {x} is not set")
                return False
        else:
            data[x] = os.environ[x]
    return data

def upload(data,tag):
    print(f"Uploading {len(data)} records for {tag}...")
    if data == []:
        print(f"No data found for {tag}.")
    else:
        # -- define the list of variables that will be used in the substition function
        VARS = {
            'YYYY'      : datetime.datetime.now(datetime.UTC).strftime('%Y'),
            'MM'        : datetime.datetime.now(datetime.UTC).strftime('%m'),
            'DD'        : datetime.datetime.now(datetime.UTC).strftime('%d'),
            'UUID'      : str(uuid.uuid4()),
            'TAG'       : tag,
        }

        # -- upload local file
        v = variables({
            'UPLOAD_TARGET' : 'data/$TAG/$YYYY/$MM/$DD/$UUID.json'
        })
        if v:
            path = v['UPLOAD_TARGET']
            for x in VARS:
                path = path.replace(f"${x}",VARS[x])
            print(f"Uploading {len(data)} records for {tag} --> {path}")
            try:
                os.makedirs(os.path.dirname(path),exist_ok = True)        
                with open(path,"wt",encoding='UTF-8') as q:
                    q.write(json.dumps(data,default=str))
            except:
                print("ERROR - cannot write the file")

        # -- upload a file to AWS S3
        v = variables({
            'UPLOAD_TARGET' : 'data/$TAG/$YYYY/$MM/$DD/$UUID.json',
            'UPLOAD_S3_BUCKET' : None
        })
        if v:
            path = v['UPLOAD_TARGET']
            for x in VARS:
                path = path.replace(f"${x}",VARS[x])
            print(f"Uploading {len(data)} records for {tag} --> s3://{v['UPLOAD_S3_BUCKET']}/{path}")
            try:
                boto3.client('s3').put_object(
                    Body = json.dumps(data,default=str),
                    Bucket = v['UPLOAD_S3_BUCKET'],
                    Key = path,
                    ACL='bucket-owner-full-control'
                )
            except botocore.exceptions.ClientError as error:
                print(f"ERROR - s3.put_object - {error.response['Error']['Code']}")

def main():
    # -- snyk
    x = variables({
        'SNYK_TOKEN' : None
    })
    if x:
        print(f"==> snyk_orgs - Extracting....")
        org = Snyk(**x).snyk_call('/rest/orgs')
        upload(org,'snyk_ogs')

        data = []
        for o in org:
            print(f"==> snyc_issues - Extracting for org {o['id']}...")
            data += Snyk(**x).snyk_call(f"/rest/orgs/{o['id']}/issues")
        upload(data,'snyk_issues')

    # -- jira
    x = variables({
        'JIRA_ENDPOINT' : None,
        'JIRA_USERNAME' : None,
        'JIRA_PASSWORD' : None,
        'JIRA_JQL'      : 'project="ABC"',
        'JIRA_TAG'      : 'jira_search'
    })
    if x:
        print(f"==> {x['JIRA_TAG']} - Extracting....")
        data = Jira(**x).search(x['JIRA_JQL'])
        upload(data,x['JIRA_TAG'])
    
    # -- nullify
    x = variables({
        'NULLIFY_TOKEN'             : None,
        'NULLIFY_ENDPOINT'          : None,
        'NULLIFY_GITHUB_OWNER_ID'   : None,
        'NULLIFY_FROM_TIME'         : (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%SZ')
    })
    if x:
        print(f"==> nullify_sca_events - Extracting....")
        data = Nullify(**x).sca_events(x['NULLIFY_FROM_TIME'])
        upload(data,'nullify_sca_events')

        print(f"==> nullify_sast_events - Extracting....")
        data = Nullify(**x).sast_events(x['NULLIFY_FROM_TIME'])
        upload(data,'nullify_sast_events')

        print(f"==> nullify_sca_counts - Extracting....")
        data = Nullify(**x).sca_counts()
        upload(data,'nullify_sca_counts')

        # Error 500 from Nullify
        # print(f"==> nullify_admin_repositories - Extracting....")
        # data = Nullify(**x).admin_repositories()
        # upload(data,'nullify_admin_repositories')

        
    
if __name__=='__main__':
    main()
