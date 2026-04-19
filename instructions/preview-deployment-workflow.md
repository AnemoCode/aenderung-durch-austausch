# Preview Deployment PR Description Workflow

Paste the YAML below into `.github/workflows/preview-deployment-pr-description.yml`.

**What it does:**
- Triggers whenever `exploited-intern` creates or edits a comment on a pull request
- Appends (or replaces) the comment content at the very bottom of the PR description
- Uses an HTML comment marker (`<!-- preview-deployment -->`) so subsequent updates replace the section instead of duplicating it

```yaml
name: Update PR Description with Preview Deployment

on:
  issue_comment:
    types: [created, edited]

jobs:
  update-pr-description:
    if: github.event.issue.pull_request != null && github.event.comment.user.login == 'exploited-intern'
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write

    steps:
      - name: Append preview deployment info to PR description
        uses: actions/github-script@v7
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          script: |
            const commentBody = context.payload.comment.body;
            const prNumber = context.payload.issue.number;

            const { data: pr } = await github.rest.pulls.get({
              owner: context.repo.owner,
              repo: context.repo.repo,
              pull_number: prNumber,
            });

            const currentBody = pr.body || '';
            const marker = '<!-- preview-deployment -->';

            let newBody;
            const markerIndex = currentBody.indexOf(marker);
            if (markerIndex !== -1) {
              newBody = currentBody.substring(0, markerIndex) + marker + '\n\n' + commentBody;
            } else {
              newBody = currentBody + '\n\n' + marker + '\n\n' + commentBody;
            }

            await github.rest.pulls.update({
              owner: context.repo.owner,
              repo: context.repo.repo,
              pull_number: prNumber,
              body: newBody,
            });

            core.info(`Updated PR #${prNumber} description with preview deployment info.`);
```
