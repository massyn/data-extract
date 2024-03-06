# Extractor

## Synopsis

Generic data extractor that uses environment variables to determine what needs to be extracted

## Getting started

### Environment variables

#### Source Systems

|**Source**|**Variable**|**Status**|
|--|--|--|
|**JIRA**|JIRA_ENDPOINT|Mandatory|
||JIRA_USERNAME|Mandatory|
||JIRA_PASSWORD|Mandatory|
||JIRA_JQL|Mandatory|
|**Nullify**|NULLIFY_TOKEN|Mandatory|
||NULLIFY_ENDPOINT|Mandatory|
||NULLIFY_GITHUB_OWNER_ID|Mandatory|
||NULLIFY_FROM_TIME|Defaults to the last 7 days|

#### Destinations

|**Target**|**Variable**|**Status**|
|--|--|--|
|**AWS S3**|UPLOAD_TARGET|Defaults to `data/$TAG/$YYYY/$MM/$DD/$UUID.json`|
||UPLOAD_S3_BUCKET|Optional|
|**Local Disk**|UPLOAD_TARGET|Defaults to `data/$TAG/$YYYY/$MM/$DD/$UUID.json`|

### Output variables

When specifying and output path, you can use any of the following variables when defining the output path.

|**Variable**|**Usage**|
|--|--|
|`$TAG`|The name of the tag specified in the config|
|`$YYYY`|Current year in UTC|
|`$MM`|Current month in UTC|
|`$DD`|Current day in UTC|
|`$UUID`|A randonmy generated UUID|
