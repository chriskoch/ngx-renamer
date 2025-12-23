# Documentation Automation

This document describes the automated systems that keep documentation up-to-date.

## Overview

The ngx-renamer project uses multiple automation layers to ensure documentation stays current:

1. **bump2version** - Automatic version updates during releases
2. **Manual update script** - Quick manual version synchronization
3. **GitHub Actions CI** - Validation on every PR/push

---

## 1. Automatic Version Updates (bump2version)

### How It Works

When you run `bump2version patch/minor/major`, it automatically updates:
- ✅ `VERSION` file
- ✅ `CHANGELOG.md` (adds new version section)
- ✅ `AGENTS.md` (version footer)
- ✅ `ARCHITECTURE.md` (version footer)
- ✅ Creates git commit and tag

### Configuration

See `.bumpversion.cfg`:
```ini
[bumpversion:file:AGENTS.md]
search = **Version**: {current_version}
replace = **Version**: {new_version}

[bumpversion:file:ARCHITECTURE.md]
search = **Version**: {current_version}
replace = **Version**: {new_version}
```

### Usage

```bash
# For bug fixes (1.2.2 → 1.2.3)
bump2version patch

# For new features (1.2.2 → 1.3.0)
bump2version minor

# For breaking changes (1.2.2 → 2.0.0)
bump2version major
```

---

## 2. Manual Update Script

For manual version synchronization outside of releases.

### Usage

```bash
# Update from VERSION file
./scripts/update-docs-version.sh

# Update to specific version
./scripts/update-docs-version.sh 1.3.0
```

### What It Does

1. Reads version from `VERSION` file (or argument)
2. Updates `AGENTS.md` version footer
3. Updates `ARCHITECTURE.md` version footer
4. Shows summary of changes

### When To Use

- After manually editing VERSION file
- To fix version inconsistencies
- When bump2version isn't available

---

## 3. GitHub Actions Validation

Runs automatically on every PR and push to main/dev branches.

### Checks Performed

#### ✅ Version Consistency
- Ensures `AGENTS.md` version matches `VERSION` file
- Ensures `ARCHITECTURE.md` version matches `VERSION` file
- Fails build if versions are inconsistent

#### ✅ Placeholder Detection
- Scans for `<repository-url>` and similar placeholders
- Prevents accidental commits of template content

#### ✅ Documentation Links
- Verifies referenced files exist
- Checks internal links are valid

### Configuration

See `.github/workflows/docs-validation.yml`

### Viewing Results

1. Go to GitHub Actions tab on your repo
2. Click on latest workflow run
3. View "Documentation Validation" job
4. See detailed check results

---

## Troubleshooting

### Version Mismatch Error in CI

**Error:**
```
Version mismatch in AGENTS.md
Expected: **Version**: 1.3.0
Found: **Version**: 1.2.2
```

**Fix:**
```bash
# Option 1: Use update script
./scripts/update-docs-version.sh

# Option 2: Run bump2version again
bump2version patch

# Option 3: Manually edit AGENTS.md and ARCHITECTURE.md
```

### Script Permission Denied

**Error:**
```
bash: ./scripts/update-docs-version.sh: Permission denied
```

**Fix:**
```bash
chmod +x scripts/update-docs-version.sh
```

### bump2version Not Found

**Install:**
```bash
pip install bump2version
# or
pip install -r requirements-dev.txt
```

---

## Best Practices

1. **Always use bump2version for releases**
   - Ensures all files are updated consistently
   - Creates proper git tags automatically

2. **Run update script after manual edits**
   - If you manually edit VERSION file
   - Keeps documentation in sync

3. **Check CI before merging**
   - GitHub Actions will catch inconsistencies
   - Fix issues before merging PRs

4. **Don't edit version numbers manually**
   - Use bump2version or update script
   - Manual edits are error-prone

---

## Files Involved

| File | Purpose | Updated By |
|------|---------|------------|
| `VERSION` | Single source of truth | bump2version, manual |
| `AGENTS.md` | AI agent documentation | bump2version, update script |
| `ARCHITECTURE.md` | Architecture documentation | bump2version, update script |
| `CHANGELOG.md` | Version history | bump2version, manual |
| `.bumpversion.cfg` | bump2version configuration | manual (rarely) |
| `scripts/update-docs-version.sh` | Manual update tool | N/A |
| `.github/workflows/docs-validation.yml` | CI validation | N/A |

---

## Adding New Files to Auto-Update

To add a new file to automatic version updates:

1. Edit `.bumpversion.cfg`
2. Add a new section:
   ```ini
   [bumpversion:file:YOUR_FILE.md]
   search = Version: {current_version}
   replace = Version: {new_version}
   ```
3. Update `scripts/update-docs-version.sh` if needed
4. Test with: `bump2version patch --dry-run --verbose`

---

## Testing Changes

### Test bump2version
```bash
# Dry run (no changes made)
bump2version patch --dry-run --verbose

# See what would be updated
bump2version patch --dry-run --allow-dirty
```

### Test Update Script
```bash
# Run script and check output
./scripts/update-docs-version.sh
git diff AGENTS.md ARCHITECTURE.md
```

### Test CI Locally
```bash
# Check version consistency
VERSION=$(cat VERSION)
grep "**Version**: $VERSION" AGENTS.md ARCHITECTURE.md

# Check for placeholders
grep -E "<[^>]+>" README.md AGENTS.md ARCHITECTURE.md
```

---

## Related Documentation

- [RELEASING.md](../../RELEASING.md) - Complete release process
- [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md) - Quick release checklist
- [AGENTS.md](../../AGENTS.md) - AI agent development guide

---

**Last Updated**: 2024-12-23
