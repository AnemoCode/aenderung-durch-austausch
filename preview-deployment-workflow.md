# Preview Deployment Workflow

Copy the YAML below and save it as `.github/workflows/preview-deployment-description.yml`.

```yaml
name: Append Preview Deployment to PR Description

on:
  issue_comment:
    types: [created, edited]

permissions:
  pull-requests: write

jobs:
  append-preview-url:
    if: |
      github.event.comment.user.login == 'exploited-intern' &&
      github.event.issue.pull_request != null
    runs-on: ubuntu-latest
    steps:
      - name: Append comment to PR description
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

            const marker = '<!-- preview-deployment-start -->';
            const endMarker = '<!-- preview-deployment-end -->';
            const currentBody = pr.body || '';

            const section = `${marker}\n\n---\n\n${commentBody}\n\n${endMarker}`;

            let newBody;
            if (currentBody.includes(marker)) {
              // Replace existing section
              newBody = currentBody.replace(
                new RegExp(`${marker}[\\s\\S]*?${endMarker}`),
                section
              );
            } else {
              // Append new section
              newBody = `${currentBody}\n\n${section}`;
            }

            await github.rest.pulls.update({
              owner: context.repo.owner,
              repo: context.repo.repo,
              pull_number: prNumber,
              body: newBody,
            });
```
