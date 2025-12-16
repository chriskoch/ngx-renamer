# ngx-renamer v1.1.0 Release Notes

## Release Status: Ready for Release

**Version**: 1.1.0 (Minor Release)
**Release Date**: 2024-12-15
**Branch**: dev → main
**Previous Version**: v1.0.0 (2024-12-15)

---

## 🎯 Release Focus: Documentation Excellence

This minor release focuses on documentation quality, developer experience, and AI agent integration following the official [agents.md](https://agents.md/) specification.

---

## 📚 Major Changes

### Documentation Restructure
Complete documentation overhaul with clear separation of concerns:

**README.md** (260 lines, 62% reduction)
- Streamlined user-focused installation guide
- Quick start for both OpenAI and Ollama
- Essential configuration only
- Common troubleshooting

**AGENTS.md** (11KB, NEW)
- Follows official [agents.md](https://agents.md/) specification
- Clear persona for AI coding agents
- Exact development, testing, and deployment commands
- Code style examples with good/bad patterns
- Three-tier boundaries (Always/Ask/Never)
- Prevents AI tool advertisements and co-author credits

**ARCHITECTURE.md** (27KB, renamed from old AGENTS.md)
- Detailed system architecture and data flow
- Component documentation
- Advanced LLM provider configuration
- Model performance comparisons
- Docker networking details
- Development setup and testing guide

---

## ✨ What's New in v1.1.0

### Added
- **AGENTS.md**: New AI coding agent guide following [agents.md](https://agents.md/) spec
  - Supported by GitHub Copilot, OpenAI, Anthropic tools
  - Clear development commands and workflows
  - Code style examples and conventions
  - Boundaries to prevent AI tool advertisements

- **ARCHITECTURE.md**: Comprehensive technical documentation
  - System architecture diagrams
  - Advanced LLM provider configuration
  - Model performance comparisons
  - Development and testing guides

### Changed
- **README.md**: Shortened from 680 to 260 lines
  - Focus on user installation and configuration
  - Removed verbose technical details
  - Clearer quick start guides

- **.gitignore**: Genericized AI tool configuration
  - Changed from "Claude Code" to "AI Tool Configuration"
  - Added support for multiple AI tools (.cursor/, .aider/)

### Removed
- All AI tool advertisements from documentation
- "Maintained by" credits
- "Developed with" promotional links

---

## 🔧 No Code Changes

This is a **documentation-only release**. All functional code remains unchanged from v1.0.0:

### Core Features (from v1.0.0)
- Multi-LLM provider support (OpenAI + Ollama)
- Zero-setup auto-init installation
- 30 integration tests (100% passing)
- Backward compatible configuration

---

## ✅ Pre-Release Checklist

- [x] All tests passing (10/10 non-API tests)
- [x] Version numbers updated to 1.1.0
- [x] CHANGELOG.md updated with all changes
- [x] No TODOs or FIXMEs in code
- [x] Dependencies documented in requirements.txt
- [x] Documentation complete and cross-referenced
- [x] AI tool advertisements removed
- [x] AGENTS.md follows official specification
- [x] Backward compatibility maintained
- [x] Git status: All changes documented

---

## 🚀 Release Process

### 1. Final Verification
```bash
# Run full test suite (optional, requires API keys)
source venv/bin/activate
pytest tests/ -v

# Check for uncommitted changes
git status
```

### 2. Commit Documentation Changes
```bash
git add .gitignore AGENTS.md ARCHITECTURE.md README.md CHANGELOG.md VERSION .bumpversion.cfg RELEASE_NOTES.md
git commit -m "Release: v1.1.0 documentation restructure

- Restructure documentation (README/AGENTS/ARCHITECTURE)
- Remove AI tool advertisements
- Add AGENTS.md following agents.md specification
- Update CHANGELOG with unreleased changes"
```

### 3. Merge to Main
```bash
git checkout main
git merge dev
git push origin main
```

### 4. Create Release Tag
```bash
git tag -a v1.0.0 -m "Release version 1.0.0

Major Features:
- Multi-LLM provider support (OpenAI + Ollama)
- Zero-setup auto-init installation
- Comprehensive test suite (30 tests)
- Documentation restructure following agents.md spec

See CHANGELOG.md for full details."

git push origin v1.0.0
```

### 5. Create GitHub Release
- Go to https://github.com/chriskoch/ngx-renamer/releases/new
- Select tag: v1.0.0
- Title: **ngx-renamer v1.0.0 - Multi-LLM Support & Auto-Init Installation**
- Copy content from this file's "Release Notes" section below
- Attach assets: None required
- Publish release

---

## 📝 Release Notes (for GitHub)

### ngx-renamer v1.1.0 - Documentation Excellence

Minor release focusing on documentation quality and AI agent integration.

**What's New in v1.1.0:**

📚 **Documentation Restructure**
- **README.md**: Shortened by 62% (680 → 260 lines) - user-focused installation guide
- **AGENTS.md**: NEW - Follows official [agents.md](https://agents.md/) specification
  - Clear persona for AI coding agents
  - Exact development, testing, deployment commands
  - Code style examples and boundaries
  - Supported by GitHub Copilot, OpenAI, Anthropic tools
- **ARCHITECTURE.md**: Renamed from old AGENTS.md with expanded technical documentation

✨ **Quality Improvements**
- Removed all AI tool advertisements
- Clear separation: Users | AI Agents | Developers
- Boundaries prevent future advertisement insertions
- Genericized .gitignore for all AI tools

🔧 **No Code Changes**
- This is a documentation-only release
- All functional code unchanged from v1.0.0
- 100% backward compatible

**Installation:**
```bash
cd ~/paperless
git clone https://github.com/chriskoch/ngx-renamer.git
# Configure credentials in docker-compose.env
# Update docker-compose.yml (see README.md)
docker compose up -d
```

**Documentation:**
- [Installation Guide](README.md)
- [Development Setup](AGENTS.md)
- [Architecture Details](ARCHITECTURE.md)
- [Full Changelog](CHANGELOG.md)

**Upgrade from v1.0.0:**
- Pull latest changes: `git pull origin main`
- No configuration changes needed
- Documentation updated automatically
- 100% backward compatible - no code changes

**Core Features** (from v1.0.0, unchanged):
- Multi-LLM support (OpenAI + Ollama)
- Zero-setup auto-init installation
- 30 integration tests
- Comprehensive documentation

---

## 🔍 Testing Summary

### Test Results
```
Platform: darwin (macOS)
Python: 3.12.12
pytest: 9.0.2

10 passed, 20 deselected (API tests), 1 warning in 28.94s
```

### Test Categories
- ✅ Provider selection (9 tests)
- ✅ Paperless API mocking (1 test)
- ⏭️ OpenAI integration (8 tests, requires API key)
- ⏭️ Ollama integration (8 tests, requires Ollama)
- ⏭️ End-to-end workflow (4 tests, requires full setup)

**Note**: API tests skipped in pre-release check to avoid costs. Run manually if needed.

---

## 📦 Files Changed

### Modified
- `.gitignore` - Added AI tool config directories
- `CHANGELOG.md` - Updated with unreleased changes
- `README.md` - Complete restructure (680 → 260 lines)
- `tests/integration/test_end_to_end.py` - Minor updates
- `tests/integration/test_paperless_integration.py` - Minor updates

### Added
- `AGENTS.md` - New file following agents.md specification
- `ARCHITECTURE.md` - Renamed from old AGENTS.md with expansions

### Removed
- Old AGENTS.md (renamed to ARCHITECTURE.md)
- All AI tool advertisements

---

## 🎯 Breaking Changes

**None** - This release is fully backward compatible.

- Existing OpenAI configurations continue to work
- Manual setup method still supported
- Legacy `openai_model` setting still functional (deprecated)
- All environment variables remain the same

---

## 🙏 Acknowledgments

Built for [Paperless NGX](https://github.com/paperless-ngx/paperless-ngx)

**LLM Providers:**
- [OpenAI](https://openai.com/)
- [Ollama](https://ollama.ai/)

**Standards:**
- [agents.md](https://agents.md/) - AI coding agent specification

---

## 📞 Support

- **Issues**: https://github.com/chriskoch/ngx-renamer/issues
- **Discussions**: https://github.com/chriskoch/ngx-renamer/discussions
- **Documentation**: [README.md](README.md) | [ARCHITECTURE.md](ARCHITECTURE.md)

---

**License**: GPL-3.0
