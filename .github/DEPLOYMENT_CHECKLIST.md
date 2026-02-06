# GitHub Actions Deployment Checklist

## Pre-Deployment

### 1. Review Changes
- [ ] Read [GITHUB_ACTIONS_UPDATE.md](../GITHUB_ACTIONS_UPDATE.md)
- [ ] Review all workflow files in `.github/workflows/`
- [ ] Understand new CI/CD architecture
- [ ] Review documentation in `docs/CI_CD.md`

### 2. Local Testing
- [ ] Clean environment: `rm -rf .venv`
- [ ] Create venv: `uv venv .venv`
- [ ] Activate: `source .venv/bin/activate`
- [ ] Install: `uv pip install -e ".[dev]"`
- [ ] Run quick check: `make quick`
- [ ] Run full CI: `make ci`
- [ ] Verify all tests pass locally
- [ ] Check linting: `make lint-check`
- [ ] Check formatting: `make format-check`

### 3. Verify Workflows
- [ ] All workflow files are valid YAML
- [ ] No syntax errors in workflows
- [ ] Action versions are up-to-date:
  - [ ] `actions/checkout@v4`
  - [ ] `actions/setup-python@v5`
  - [ ] `astral-sh/setup-uv@v4`
  - [ ] `codecov/codecov-action@v4`

### 4. Dependencies
- [ ] `pyproject.toml` has all required dependencies
- [ ] Development dependencies include all test tools
- [ ] No conflicting version requirements
- [ ] Python version compatibility (3.8+)

## Deployment Steps

### 1. Initial Setup

#### GitHub Repository Settings
- [ ] Go to Settings → Actions → General
- [ ] Enable "Allow all actions and reusable workflows"
- [ ] Enable "Read and write permissions" for GITHUB_TOKEN
- [ ] Save changes

#### Secrets Configuration (if needed)
- [ ] Settings → Secrets and variables → Actions
- [ ] Add `CODECOV_TOKEN` (optional, for coverage)
- [ ] Add any other required secrets

### 2. Branch Protection

#### Main Branch
- [ ] Go to Settings → Branches → Branch protection rules
- [ ] Add rule for `main` branch
- [ ] Enable: "Require a pull request before merging"
- [ ] Enable: "Require status checks to pass before merging"
- [ ] Add required status checks:
  - [ ] `test (ubuntu-latest, 3.11)`
  - [ ] `lint`
  - [ ] `quick-check`
- [ ] Enable: "Require branches to be up to date before merging"
- [ ] Enable: "Include administrators" (recommended)
- [ ] Save changes

#### Develop Branch (optional)
- [ ] Repeat above steps for `develop` branch
- [ ] Adjust required checks as needed

### 3. First Test Run

#### Create Test PR
```bash
# Create test branch
git checkout -b test/github-actions-update

# Make a trivial change (e.g., update README)
echo "" >> README.md

# Commit and push
git add README.md
git commit -m "test: verify GitHub Actions workflows"
git push origin test/github-actions-update
```

#### Verify Workflows Run
- [ ] Go to Actions tab
- [ ] Verify "Tests" workflow starts
- [ ] Verify "PR Quick Check" workflow starts
- [ ] Monitor workflow execution
- [ ] Check all jobs complete successfully
- [ ] Review workflow logs
- [ ] Verify artifacts are uploaded
- [ ] Check Codecov integration (if configured)

### 4. Workflow-Specific Checks

#### Tests Workflow (`tests.yml`)
- [ ] Matrix jobs run for all OS/Python combinations
- [ ] Unit tests pass on all platforms
- [ ] Integration tests pass on all platforms
- [ ] Lint job completes successfully
- [ ] Security job runs (continue-on-error is OK)
- [ ] Quick check job passes
- [ ] Test summary job aggregates results
- [ ] Coverage report uploaded to Codecov (Ubuntu + Python 3.11)

#### PR Quick Check (`pr-check.yml`)
- [ ] Runs only on pull requests
- [ ] Quick check completes in <5 minutes
- [ ] Lint check validates code quality
- [ ] Diagnostics output is helpful

#### CI Pipeline (`ci.yml`)
- [ ] Full CI pipeline runs successfully
- [ ] All steps in `make ci` execute
- [ ] Coverage report generated
- [ ] Artifacts uploaded correctly

#### Nightly Tests (`nightly.yml`)
- [ ] Can be triggered manually (workflow_dispatch)
- [ ] Schedule is configured correctly (2 AM UTC)
- [ ] Full matrix testing works
- [ ] Security audits complete
- [ ] Summary report generated

### 5. Verify Integration Points

#### Codecov (if configured)
- [ ] Coverage reports upload successfully
- [ ] Codecov dashboard shows data
- [ ] PR comments show coverage changes
- [ ] Badge URL works

#### Artifacts
- [ ] Test results are saved
- [ ] Coverage reports are saved
- [ ] Bandit security reports are saved
- [ ] Artifacts can be downloaded

## Post-Deployment

### 1. Documentation Updates

#### README.md
- [ ] Add workflow status badges
- [ ] Update CI/CD section
- [ ] Add quick start for contributors
- [ ] Link to CI documentation

#### Status Badges
Add to top of README.md:
```markdown
[![Tests](https://github.com/TianaNanta/OpsZen/workflows/Tests/badge.svg)](https://github.com/TianaNanta/OpsZen/actions/workflows/tests.yml)
[![CI Pipeline](https://github.com/TianaNanta/OpsZen/workflows/CI%20Pipeline/badge.svg)](https://github.com/TianaNanta/OpsZen/actions/workflows/ci.yml)
[![Nightly Tests](https://github.com/TianaNanta/OpsZen/workflows/Nightly%20Tests/badge.svg)](https://github.com/TianaNanta/OpsZen/actions/workflows/nightly.yml)
```

### 2. Team Communication
- [ ] Notify team of CI/CD updates
- [ ] Share documentation links
- [ ] Provide quick reference card
- [ ] Schedule demo/walkthrough if needed

### 3. Monitor Initial Runs
- [ ] Watch first few workflow runs
- [ ] Track success/failure rates
- [ ] Monitor execution times
- [ ] Note any patterns or issues

### 4. Gather Metrics

#### Performance
- [ ] Compare CI times (before vs after)
- [ ] Track dependency installation time
- [ ] Monitor test execution time
- [ ] Check cache hit rates

#### Reliability
- [ ] Track workflow success rates
- [ ] Monitor flaky tests
- [ ] Review failure patterns
- [ ] Check for platform-specific issues

## Rollback Plan

If critical issues are found:

### Option 1: Quick Fix
```bash
# Fix the issue
git checkout -b fix/ci-issue

# Make changes
# ...

# Test locally
make ci

# Commit and push
git commit -am "fix: resolve CI issue"
git push origin fix/ci-issue

# Create PR and merge quickly
```

### Option 2: Revert Workflows
```bash
# Revert to previous workflow versions
git checkout <previous-commit> -- .github/workflows/
git commit -m "revert: restore previous GitHub Actions workflows"
git push origin main
```

### Option 3: Disable Workflows
- Go to Actions → Select workflow → ... → Disable workflow
- Fix issues offline
- Re-enable when ready

## Validation Checklist

### ✅ Success Criteria
- [ ] All workflows execute successfully
- [ ] Tests pass on all platforms
- [ ] Linting passes
- [ ] Coverage reports generated
- [ ] Security scans complete
- [ ] Artifacts uploaded
- [ ] No critical errors in logs
- [ ] Branch protection works as expected
- [ ] Team members can contribute smoothly

### ⚠️ Warning Signs
- Flaky tests (passing/failing inconsistently)
- Timeout errors
- Platform-specific failures
- Cache misses (>50%)
- Slow workflow execution (>15 min for standard tests)
- Missing artifacts
- Failed uploads to Codecov

### 🚨 Critical Issues (Requires Immediate Action)
- Workflows fail to start
- All jobs fail
- Security vulnerabilities blocking merges
- Cannot merge due to failed required checks
- Broken branch protection
- Team unable to contribute

## Maintenance

### Weekly
- [ ] Review workflow success rates
- [ ] Check for flaky tests
- [ ] Monitor execution times
- [ ] Review security scan results

### Monthly
- [ ] Update action versions
- [ ] Review and update Python versions
- [ ] Check for dependency updates
- [ ] Optimize slow workflows
- [ ] Review cache effectiveness

### Quarterly
- [ ] Comprehensive workflow review
- [ ] Update documentation
- [ ] Gather team feedback
- [ ] Plan improvements

## Troubleshooting

### Common Issues

#### Workflow Doesn't Start
1. Check workflow trigger conditions
2. Verify branch name matches trigger
3. Check repository settings (Actions enabled)
4. Review workflow file syntax

#### Tests Pass Locally, Fail in CI
1. Check environment differences
2. Verify all dependencies in pyproject.toml
3. Check for platform-specific code
4. Review CI logs for details

#### Slow Workflows
1. Review cache configuration
2. Check for sequential jobs that could be parallel
3. Optimize test execution (use pytest-xdist)
4. Consider splitting large test suites

#### Security Scan Failures
1. Review bandit/safety reports
2. Assess if issues are critical
3. Fix or add to ignore list
4. Note: continue-on-error is enabled for some checks

## Resources

- [CI/CD Documentation](../docs/CI_CD.md)
- [Quick Reference](../docs/CI_QUICK_REF.md)
- [Update Summary](../GITHUB_ACTIONS_UPDATE.md)
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [uv Documentation](https://github.com/astral-sh/uv)
- [ruff Documentation](https://docs.astral.sh/ruff/)

## Support

### Getting Help
1. Check documentation first
2. Review GitHub Actions logs
3. Run locally with `make ci`
4. Check [existing issues](https://github.com/TianaNanta/OpsZen/issues)
5. Open new issue with details

### Contact
- GitHub Issues: https://github.com/TianaNanta/OpsZen/issues
- Discussions: Use GitHub Discussions
- Maintainers: See CODEOWNERS file

---

## Sign-Off

**Deployed by:** _________________  
**Date:** _________________  
**Verified by:** _________________  
**Notes:** _________________

---

*Checklist version: 1.0*  
*Last updated: 2024*
