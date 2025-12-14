# Release Process

This document describes the semantic versioning and release process for ngx-renamer.

## Semantic Versioning

This project follows [Semantic Versioning 2.0.0](https://semver.org/):

- **MAJOR** version (X.0.0): Incompatible API changes or breaking changes
- **MINOR** version (0.X.0): New functionality in a backward compatible manner
- **PATCH** version (0.0.X): Backward compatible bug fixes

## Version Management

We use [bump2version](https://github.com/c4urself/bump2version) to manage versions automatically.

### Prerequisites

Install bump2version in your development environment:

```bash
pip install bump2version
```

Or install all dev dependencies:

```bash
pip install -r requirements-dev.txt
```

## Release Workflow

### 1. Ensure Clean State

Make sure all changes are committed and pushed to the `dev` branch:

```bash
git status
git checkout dev
git pull origin dev
```

### 2. Update CHANGELOG

Edit [CHANGELOG.md](CHANGELOG.md) to move items from `[Unreleased]` to a new version section:

```markdown
## [Unreleased]

## [X.Y.Z] - YYYY-MM-DD

### Added
- New feature descriptions

### Changed
- Changes to existing functionality

### Fixed
- Bug fixes

### Removed
- Removed features
```

### 3. Bump Version

Choose the appropriate bump command based on your changes:

#### Patch Release (bug fixes only)
```bash
bump2version patch
```

#### Minor Release (new features, backward compatible)
```bash
bump2version minor
```

#### Major Release (breaking changes)
```bash
bump2version major
```

This will automatically:
- Update the `VERSION` file
- Update `CHANGELOG.md` with the new version header
- Create a git commit with message "Bump version: X.Y.Z → X.Y.Z+1"
- Create a git tag `vX.Y.Z+1`

### 4. Push Changes

Push both the commit and the tag:

```bash
git push origin dev
git push origin --tags
```

### 5. Merge to Main

Create a pull request from `dev` to `main`:

```bash
gh pr create --base main --head dev \
  --title "Release vX.Y.Z" \
  --body "Release version X.Y.Z

See CHANGELOG.md for details."
```

Or merge directly if you have permissions:

```bash
git checkout main
git merge dev
git push origin main
```

### 6. Create GitHub Release

Create a GitHub release from the tag:

```bash
gh release create vX.Y.Z \
  --title "v.Y.Z" \
  --notes-file <(sed -n '/## \[X.Y.Z\]/,/## \[/p' CHANGELOG.md | head -n -1)
```

Or create manually via the GitHub UI:
1. Go to https://github.com/chriskoch/ngx-renamer/releases/new
2. Select the tag `vX.Y.Z`
3. Set release title: `vX.Y.Z`
4. Copy the relevant section from CHANGELOG.md as the description
5. Click "Publish release"

## Manual Version Update (Not Recommended)

If you need to manually update the version:

1. Edit `VERSION` file
2. Edit `.bumpversion.cfg` to update `current_version`
3. Update `CHANGELOG.md` manually
4. Commit and tag manually:

```bash
git add VERSION .bumpversion.cfg CHANGELOG.md
git commit -m "Bump version: X.Y.Z → X.Y.Z+1"
git tag -a vX.Y.Z+1 -m "Release vX.Y.Z+1"
```

## Version Checking

To check the current version:

```bash
cat VERSION
```

Or check the latest git tag:

```bash
git describe --tags --abbrev=0
```

## Hotfix Process

For urgent fixes to the main branch:

1. Create a hotfix branch from main:
   ```bash
   git checkout main
   git checkout -b hotfix/v.Y.Z+1
   ```

2. Make and commit your fixes

3. Bump the patch version:
   ```bash
   bump2version patch
   ```

4. Push and create PR to main:
   ```bash
   git push origin hotfix/vX.Y.Z+1
   gh pr create --base main --title "Hotfix vX.Y.Z+1"
   ```

5. After merging to main, also merge back to dev:
   ```bash
   git checkout dev
   git merge main
   git push origin dev
   ```

## Pre-release Versions

For alpha, beta, or release candidate versions, manually edit VERSION:

- Alpha: `1.0.0-alpha.1`
- Beta: `1.0.0-beta.1`
- Release Candidate: `1.0.0-rc.1`

Then create and push the tag manually:

```bash
git tag -a v1.0.0-beta.1 -m "Beta release 1.0.0-beta.1"
git push origin v1.0.0-beta.1
```

## Troubleshooting

### Tag already exists

If the tag already exists:

```bash
git tag -d vX.Y.Z  # Delete local tag
git push origin :vX.Y.Z  # Delete remote tag
bump2version [patch|minor|major]  # Try again
```

### Wrong version bumped

To undo a version bump before pushing:

```bash
git reset --hard HEAD~1  # Reset the commit
git tag -d vX.Y.Z  # Delete the tag
```

Then bump the correct version type.

### CHANGELOG conflicts

If CHANGELOG.md has conflicts during merge:
1. Manually resolve the conflicts
2. Ensure both version sections are preserved
3. Keep chronological order (newest first)
4. Update the version comparison links at the bottom
