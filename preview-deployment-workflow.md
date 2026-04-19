# Preview Deployment Workflow

Copy the YAML below and save it as `.github/workflows/preview-deployment-description.yml`.

**Note:** GitHub uses the `issue_comment` event for comments on both issues *and* pull requests. The `pull_request` guard in the job condition ensures this workflow only runs when `exploited-intern` comments on a PR, never on a plain issue.

```yaml
name: Add preview deployment URL to PR description

on:
  issue_comment:
    types: [created, edited]

jobs:
  update-pr-description:
    # Only run for PR comments from exploited-intern
    if: >
      github.event.issue.pull_request != null &&
      github.event.comment.user.login == 'exploited-intern'
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write

    steps:
      - name: Update PR description with preview URL
        uses: actions/github-script@v7
        with:
          script: |
            const prNumber = context.issue.number;
            const commentBody = context.payload.comment.body;

            // Fetch current PR description
            const { data: pr } = await github.rest.pulls.get({
              owner: context.repo.owner,
              repo: context.repo.repo,
              pull_number: prNumber,
            });

            const marker = '<!-- preview-deployment-url -->';
            const section = `${marker}\n---\n**Preview deployment:**\n\n${commentBody}`;

            let currentBody = pr.body || '';

            let updatedBody;
            if (currentBody.includes(marker)) {
              // Replace existing section
              updatedBody = currentBody.replace(
                new RegExp(`${marker}[\\s\\S]*$`),
                section
              );
            } else {
              // Append new section
              updatedBody = `${currentBody}\n\n${section}`;
            }

            await github.rest.pulls.update({
              owner: context.repo.owner,
              repo: context.repo.repo,
              pull_number: prNumber,
              body: updatedBody,
            });
```
