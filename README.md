# shortcut-ticket-gh-action
custom github action to create shortcut tickets after a pull request is opened

## Inputs

## `repo-name`

**Required** The name of the repo whose PRs will be checked for the specified alert type. Default `"radarlabs/server"`.

## `alert-type`

**Required** The type of alert that shortcut tickets will be created for. Default `"dependabot"`.


## Outputs

## `tickets`

The total number of Shortcut ticket that were created

## Example usage

uses: radarlabs/shortcut-ticket-gh-action@v1
with:
    repo-name:  # id of input
        required: true
        default: 'radarlabs/server'
    alert-type:
        required: true
        default: 'dependabot'
