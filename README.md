# shortcut-ticket-gh-action
This custom github action is used to create shortcut tickets for the specified alert type after a pull request is opened

## Inputs

## `repoName`

**Required** The name of the repo whose PRs will be checked for the specified alert type. Default `"radarlabs/server"`.

## `alertType`

**Required** The type of alert that shortcut tickets will be created for. Default `"dependabot"`.


## Outputs

## `tickets`

The total number of Shortcut ticket that were created

## Example usage

```yaml
uses: radarlabs/shortcut-ticket-gh-action@v1
with:
    repoName:  # id of input
        required: true
        default: 'radarlabs/server'
    alertType:
        required: true
        default: 'dependabot'
```
