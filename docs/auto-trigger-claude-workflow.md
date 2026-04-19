# Auto-trigger Claude when Issue moves to "In Progress"

This workflow automatically posts `@claude implement` as a comment on an issue whenever its GitHub Project status is changed to **"In Progress"**. That comment then triggers the existing `claude.yml` workflow to start implementation.

## How it works

1. GitHub fires a `projects_v2_item` event whenever a project item's field is edited.
2. This workflow queries the GraphQL API to read the item's current **Status** and resolve the linked issue number.
3. If the status is exactly `"In Progress"`, it posts `@claude implement` as a comment on that issue.
4. The existing Claude workflow picks up the comment and starts the implementation.

## Prerequisites

- Your repository must already have the [claude-code-action](https://github.com/anthropics/claude-code-action) workflow set up (the `claude.yml` file in `.github/workflows/`).
- The project must be a **GitHub Projects v2** project.
- For **organization-level projects**, the `GITHUB_TOKEN` may lack project read access. In that case, create a Personal Access Token (PAT) with the `project` scope and store it as a repository secret (e.g., `PROJECT_READ_TOKEN`), then replace `${{ secrets.GITHUB_TOKEN }}` in the `Check status and get issue number` step with `${{ secrets.PROJECT_READ_TOKEN }}`.

## Workflow file

Save this as `.github/workflows/auto-trigger-claude.yml` in your repository:

```yaml
name: Auto-trigger Claude on Issue In Progress

on:
  projects_v2_item:
    types: [edited]

jobs:
  trigger-claude:
    # Only process items that are linked to an Issue (not PRs or draft issues)
    if: github.event.projects_v2_item.content_type == 'Issue'
    runs-on: ubuntu-latest
    permissions:
      issues: write

    steps:
      - name: Check status and get issue number
        id: check
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          ITEM_NODE_ID: ${{ github.event.projects_v2_item.node_id }}
          CONTENT_NODE_ID: ${{ github.event.projects_v2_item.content_node_id }}
        run: |
          RESULT=$(gh api graphql \
            -f query='
              query($itemId: ID!, $contentId: ID!) {
                item: node(id: $itemId) {
                  ... on ProjectV2Item {
                    fieldValues(first: 20) {
                      nodes {
                        ... on ProjectV2ItemFieldSingleSelectValue {
                          name
                          field {
                            ... on ProjectV2SingleSelectField {
                              name
                            }
                          }
                        }
                      }
                    }
                  }
                }
                content: node(id: $contentId) {
                  ... on Issue {
                    number
                  }
                }
              }
            ' \
            -f itemId="$ITEM_NODE_ID" \
            -f contentId="$CONTENT_NODE_ID")

          STATUS=$(echo "$RESULT" | jq -r '
            .data.item.fieldValues.nodes[]
            | select(.field.name == "Status")
            | .name
            // empty
          ')
          ISSUE_NUMBER=$(echo "$RESULT" | jq -r '.data.content.number // empty')

          echo "status=$STATUS" >> "$GITHUB_OUTPUT"
          echo "issue_number=$ISSUE_NUMBER" >> "$GITHUB_OUTPUT"

      - name: Post @claude implement comment
        if: steps.check.outputs.status == 'In Progress' && steps.check.outputs.issue_number != ''
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          ISSUE_NUMBER: ${{ steps.check.outputs.issue_number }}
          REPO: ${{ github.repository }}
        run: |
          gh issue comment "$ISSUE_NUMBER" \
            --repo "$REPO" \
            --body "@claude implement"
```

## Customisation

| What to change | Where |
|---|---|
| Status field name is not `"Status"` | Update `select(.field.name == "Status")` in the GraphQL filter |
| Status option is not `"In Progress"` | Update `steps.check.outputs.status == 'In Progress'` in the `if` condition |
| Custom Claude prompt | Change the `--body "@claude implement"` to any prompt you like |
| Org-level project needs elevated token | Replace `secrets.GITHUB_TOKEN` in the `check` step with a PAT secret that has `project` scope |
