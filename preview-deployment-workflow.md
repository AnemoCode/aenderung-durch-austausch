# Preview Deployment Workflow

Paste the content below into `.github/workflows/preview-deployment-description.yml`.

```yaml
name: Add Preview Deployment to PR Description

on:
  issue_comment:
    types: [created, edited]

jobs:
  add-preview-to-pr:
    runs-on: ubuntu-latest
    if: |
      github.event.comment.user.login == 'exploited-intern' &&
      github.event.issue.pull_request != null
    permissions:
      pull-requests: write
    steps:
      - name: Append preview URL to PR description
        uses: actions/github-script@v7
        with:
          script: |
            const prNumber = context.issue.number;
            const commentBody = context.payload.comment.body;

            const { data: pr } = await github.rest.pulls.get({
              owner: context.repo.owner,
              repo: context.repo.repo,
              pull_number: prNumber,
            });

            const currentBody = pr.body || '';

            // Marker used to find and replace the preview section on updates
            const MARKER = '<!-- exploited-intern-preview -->';

            let newBody;
            if (currentBody.includes(MARKER)) {
              newBody = currentBody.replace(
                new RegExp(`${MARKER}[\\s\\S]*$`),
                `${MARKER}\n${commentBody}`
              );
            } else {
              newBody = currentBody
                ? `${currentBody}\n\n${MARKER}\n${commentBody}`
                : `${MARKER}\n${commentBody}`;
            }

            await github.rest.pulls.update({
              owner: context.repo.owner,
              repo: context.repo.repo,
              pull_number: prNumber,
              body: newBody,
            });
```

## How it works

- **Trigger:** fires on every `issue_comment` that is created or edited.
- **Guard conditions:** only runs when both conditions are true:
  - the comment author is `exploited-intern`
  - the comment belongs to a pull request (not a plain issue)
- **Idempotency:** an HTML comment marker (`<!-- exploited-intern-preview -->`) is inserted once. On subsequent edits by the bot the section is replaced in-place rather than appended again, so the description never accumulates duplicates.
- **Permissions:** only `pull-requests: write` is required; no repository-level token changes are needed.
