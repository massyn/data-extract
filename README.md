# Extractor

## Synopsis

Generic data extractor

## Getting started

## Source plugins

### Jira (Search)

[API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/#api-rest-api-3-search-get)

```yaml
plugin: jira_search
table: ...
variables:
  username: ...
  password: ...
  endpoint: ...
  jql: ...
```

## Destination plugins

### write_json

Write data to the local disk as a `json` file.

```yaml
plugin: write_json
variables:
  output: data/$TABLE/$YYYY/$MM/$DD/$UUID.json
```

### write_s3

Write data to an AWS S3 bucket as a `json` file.

```yaml
plugin: write_s3
variables:
  bucket: my-fancy-bucket-name
  key: data/$TABLE/$YYYY/$MM/$DD/$UUID.json
```

### Output variables

When specifying and output path, you can use any of the following variables when defining the output path.

|**Variable**|**Usage**|
|--|--|
|`$TABLE`|The name of the table specified in the config|
|`$PLUGIN`|The name of the plugin specified in the config|
|`$YYYY`|Current year in UTC|
|`$MM`|Current month in UTC|
|`$DD`|Current day in UTC|
|`$UUID`|A randonmy generated UUID|
