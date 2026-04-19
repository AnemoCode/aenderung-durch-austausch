# Preview Deployment Workflow

Copy the YAML block below and save it as `.github/workflows/preview-deployment-description.yml`.

```yaml
name: Add Preview Deployment to PR Description

on:
  issue_comment:
    types: [created, edited]

jobs:
  append-preview-url:
    # Only run on PR comments from exploited-intern
    if: >
      github.event.issue.pull_request != null &&
      github.event.comment.user.login == 'exploited-intern'
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write

    steps:
      - name: Update PR description with preview deployment
        uses: actions/github-script@v7
        with:
          script: |
            const prNumber = context.issue.number;
            const commentBody = context.payload.comment.body;

            // Fetch the current PR description
            const { data: pr } = await github.rest.pulls.get({
              owner: context.repo.owner,
              repo: context.repo.repo,
              pull_number: prNumber,
            });

            const marker = '<!-- preview-deployment -->';
            const section = `${marker}\n\n---\n\n${commentBody}`;

            let body = pr.body || '';

            if (body.includes(marker)) {
              // Replace existing preview deployment section
              body = body.replace(
                new RegExp(`${marker}[\\s\\S]*$`),
                section
              );
            } else {
              // Append section at the very bottom
              body = body.trimEnd() + '\n\n' + section;
            }

            await github.rest.pulls.update({
              owner: context.repo.owner,
              repo: context.repo.repo,
              pull_number: prNumber,
              body,
            });
```
