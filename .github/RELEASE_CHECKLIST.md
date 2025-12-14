# Release Checklist for v1.0.0

This is a quick checklist for releasing v1.0.0 from the dev branch.

## Pre-Release Checklist

- [ ] All tests passing (`pytest`)
- [ ] CHANGELOG.md updated with all changes
- [ ] README.md is up to date
- [ ] All features documented
- [ ] No outstanding critical bugs
- [ ] All commits pushed to dev branch

## Release Steps

### 1. Verify Current State

```bash
git checkout dev
git status  # Should be clean
git pull origin dev
```

### 2. Run Tests

```bash
# Install dev dependencies if not already installed
pip install -r requirements-dev.txt

# Run test suite
pytest

# Verify coverage (optional)
pytest --cov=. --cov-report=html
```

### 3. Review CHANGELOG

Open [CHANGELOG.md](../../CHANGELOG.md) and verify:
- All changes are documented under `[1.0.0] - 2025-12-15`
- Changes are categorized correctly (Added, Changed, Fixed, etc.)
- Version links at bottom are correct

### 4. Create Release (First Time - Manual)

Since this is the first release and the tag/version are already set up:

```bash
# Verify VERSION file
cat VERSION  # Should show: 1.0.0

# Create and push the tag
git tag -a v1.0.0 -m "Release version 1.0.0

First official release with multi-LLM support, auto-init installation, and comprehensive test suite.

See CHANGELOG.md for full details."

git push origin v1.0.0
```

The GitHub Action will automatically create the release when the tag is pushed.

### 5. Merge to Main

```bash
# Create PR from dev to main
gh pr create --base main --head dev \
  --title "Release v1.0.0" \
  --body "# Release v1.0.0

First official release of ngx-renamer with semantic versioning.

## Highlights
- Multi-LLM provider support (OpenAI + Ollama)
- Zero-setup auto-init installation
- Comprehensive test suite
- Full backward compatibility

See [CHANGELOG.md](https://github.com/chriskoch/ngx-renamer/blob/dev/CHANGELOG.md) for complete details."

# Or merge directly:
git checkout main
git merge --no-ff dev -m "Merge dev into main for v1.0.0 release"
git push origin main
```

### 6. Verify Release

- [ ] Check GitHub releases page: https://github.com/chriskoch/ngx-renamer/releases
- [ ] Verify release notes are correct
- [ ] Verify tag is visible: https://github.com/chriskoch/ngx-renamer/tags
- [ ] Test installation from the tag in a clean environment

### 7. Post-Release

```bash
# Switch back to dev for continued development
git checkout dev

# Sync dev with main if you merged
git merge main
git push origin dev
```

## Future Releases

For subsequent releases, use bump2version:

```bash
# For bug fixes
bump2version patch  # 1.0.0 -> 1.0.1

# For new features
bump2version minor  # 1.0.0 -> 1.1.0

# For breaking changes
bump2version major  # 1.0.0 -> 2.0.0
```

See [RELEASING.md](../../RELEASING.md) for complete documentation.

## Rollback

If something goes wrong:

```bash
# Delete the tag locally and remotely
git tag -d v1.0.0
git push origin :refs/tags/v1.0.0

# Delete the release on GitHub
gh release delete v1.0.0

# Fix the issues, then retry
```

## Notes

- The GitHub Action will automatically create a release when you push a tag
- Release notes are extracted from CHANGELOG.md
- Pre-release versions (v1.0.0-alpha.1, v1.0.0-beta.1) are marked as pre-release
- Always test in a clean environment before releasing
