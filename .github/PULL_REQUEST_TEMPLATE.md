# Contribution Guide

We welcome your contributions to this repository. To ensure elegant code style and better code quality, we have prepared
the following contribution guidelines.

## What We Accept

+ This PR fixes a typo or improves the documentation (if this is the case, you may skip the other checks).
+ This PR fixes a specific issue — please reference the issue number in the PR description. Make sure your code strictly
  follows the coding standards below.
+ This PR introduces a new feature — please clearly explain the necessity and implementation of the feature. Make sure
  your code strictly follows the coding standards below.

## Code Style Guide

Good code style is an art. We have prepared a `pre-commit` hook to enforce consistent code
formatting across the project. You can clean up your code following the steps below:

```shell
pre-commit run --all-files
```

If your code complies with the standards, you should not see any errors.

## Naming Conventions

+ Please use **English** for naming; do not use Pinyin or other languages. All comments should also be in English.
+ Follow **PEP8** naming conventions strictly, and use underscores to separate words. Avoid meaningless names such as
  `a`, `b`, `c`.

## For glmv-reward Contributors

Before PR, Please run:

```bash
cd glmv-reward/
uv sync
uv run poe lint
uv run poe typecheck
```
