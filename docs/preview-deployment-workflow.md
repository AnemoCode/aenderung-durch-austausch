# Preview Deployment PR Description Workflow

This workflow automatically appends the Dokploy preview URL comment to the bottom of a PR description whenever the `exploited-intern[bot]` GitHub App posts a Dokploy preview comment on the PR.

> [!NOTE]
> To activate this, copy the YAML below into `.github/workflows/preview-deployment-pr-description.yml`.
> The token used to merge this PR must have the `workflows` scope (PAT) or the GitHub App must have `workflows: write` permission.

## How It Works

1. The workflow triggers when an `issue_comment` event is fired.
2. It checks that the comment is on a PR (not a plain issue), posted by the `exploited-intern[bot]` app, and contains the header `Dokploy Preview Deployment`.
3. The comment body is wrapped in HTML marker comments and either appended to or replaces a previous block at the bottom of the PR body. This ensures updates (e.g. a re-deploy) overwrite the old status instead of appending duplicates.

## Example Dokploy Comment

The bot comment always looks like this:

```markdown
### Dokploy Preview Deployment


| Name       | Status       | Preview                               | Updated (UTC)         |
|------------|--------------|---------------------------------------|-----------------------|
| ÄdA Web Staging  | ⚌ Failed | [Preview URL](https://preview-aeda-web-staging-iduicr-qmkibs.aenderung-durch-austausch.de) | 2026-04-19T10:20:21.271Z |
```

## Workflow YAML

Copy this into `.github/workflows/preview-deployment-pr-description.yml`:

```yaml
name: Update PR Description with Preview Deployment

on:
  issue_comment:
    types: [created]

jobs:
  update-pr-description:
    if: >-
      github.event.issue.pull_request != null &&
      github.event.comment.user.login == 'exploited-intern[bot]' &&
      contains(github.event.comment.body, 'Dokploy Preview Deployment')
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write

    steps:
      - name: Sync preview deployment block in PR description
        uses: actions/github-script@v7
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          script: |
            const startMarker = '<!-- preview-deployment:start -->';
            const endMarker = '<!-- preview-deployment:end -->';

            const commentBody = context.payload.comment.body;
            const prNumber = context.payload.issue.number;

            const { data: pr } = await github.rest.pulls.get({
              owner: context.repo.owner,
              repo: context.repo.repo,
              pull_number: prNumber,
            });

            const currentBody = pr.body || '';
            const block = `${startMarker}\n${commentBody}\n${endMarker}`;

            const startIndex = currentBody.indexOf(startMarker);
            const endIndex = currentBody.indexOf(endMarker);

            let newBody;
            if (startIndex !== -1 && endIndex !== -1 && endIndex > startIndex) {
              newBody =
                currentBody.substring(0, startIndex) +
                block +
                currentBody.substring(endIndex + endMarker.length);
            } else {
              const separator = currentBody.length > 0 ? '\n\n' : '';
              newBody = currentBody + separator + block;
            }

            if (newBody === currentBody) {
              core.info(`PR #${prNumber} description already up to date.`);
              return;
            }

            await github.rest.pulls.update({
              owner: context.repo.owner,
              repo: context.repo.repo,
              pull_number: prNumber,
              body: newBody,
            });

            core.info(`Updated PR #${prNumber} description with preview deployment info.`);
```
