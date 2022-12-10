# Developers

This document provides guidance for developers to use this repository to release USGS executables.

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [Overview](#overview)
- [Triggering a release](#triggering-a-release)
  - [GitHub UI](#github-ui)
  - [GitHub CLI](#github-cli)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Overview

This repository only builds USGS programs and contains none of their source code. Its contents are concerned only with the build and release process. Repository contents have no direct relationship to release cadence or version/tag numbers.

As such, this repo's CI is configured to allow manually triggering releases, independent of changes to version-controlled files.

The `.github/workflows/release.yml` CI workflow is triggered on the following events:

- `push` to `master`
- `pull_request` to any branch
- `workflow_dispatch`

If the triggering event is a `push` or `pull_request`, binaries are built and uploaded as artifacts, then the workflow ends. If the triggering event is a `workflow_dispatch`, binaries are built and uploaded as artifacts, then a release is created, incrementing the version number. The release is *not* a draft, and is published immediately. If changes are detected to any of the program versions or timestamps, a draft PR is opened against the `master` branch to update the table in `README.md`.

**Note:** version numbers do not currently follow semantic versioning conventions. We simply increment an integer version number by 1 for each release.

## Triggering a release

The `workflow_dispatch` event is GitHub's mechanism for manually triggering workflows. This can be accomplished from the Actions tab in the GitHub UI, or via the [GitHub CLI](https://cli.github.com/manual/gh_workflow_run).

### GitHub UI

Navigate to the Actions tab of this repository. Select the release workflow. A `Run workflow` button should be visible in an alert at the top of the list of workflow runs. Click the `Run workflow` button, selecting the `master` branch. 

### GitHub CLI

Install and configure the [GitHub CLI](https://cli.github.com/manual/) if needed. Then the following command can be run from the root of your local clone of the repository:

```shell
gh workflow run release.yml
```

On the first run, the CLI will prompt to choose whether the run should be triggered on your fork of the repository or on the upstream version. This decision is stored for subsequent runs &mdash; to override it later, use the `--repo` (short `-R`) option to specify the repository. For instance, if you initially selected your fork but would like to trigger a release on the main repository:

```shell
gh workflow run release.yml -R MODFLOW-USGS/executables
```

**Note:** by default, workflow runs are associated with the repository's default branch. If the repo's default branch is `develop` (as is currently the case for `MODFLOW-USGS/executables`, you will need to use the `--ref` (short `-r`) option to specify the `master` branch when triggering a release from the CLI. For instance:

```shell
gh workflow run release.yml -R MODFLOW-USGS/executables -r master
```