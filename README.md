# Shortcut Ticket Github Action
This custom github action is used to create shortcut tickets for the specified alert type after a pull request is opened

## Required Environment Variables

## `$SHORTCUT_TOKEN`

**Required** Github default token for Github API authentication.

## `$CLUBHOUSE_TOKEN`

**Required** Token used for Clubhouse API Authentication.

## `$ALERT_TYPE`

**Required** The alert type the tickets should be created for. Default is `dependabot`.


## `$PROJECT_ID`

**Required** ID of Shortcut project that the tickets will be created under. Default is `5255` for Security Ops project.

## `$PULL_REQUEST`

**Required** Pull request number parsed from Github context. Job will fail if pull request number is missing!


## Outputs

## `tickets`

The total number of Shortcut ticket that were created

## Example usage

```yaml
    steps:
      - name: Create Shortcut Tickets for Snyk Alerts
        id: snyk
        uses: radarlabs/shortcut-ticket-gh-action@v1.0
        env:
          SHORTCUT_TOKEN: ${{ secrets.CLUBHOUSE_TOKEN }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          PROJECT_ID: 5255
          ALERT_TYPE: Snyk
          PULL_REQUEST: ${{ github.event.pull_request.number }}
```
