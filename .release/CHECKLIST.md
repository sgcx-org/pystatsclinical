# Release Checklist

> The automated path (`release.py --commit`) handles everything except
> the README and the GitHub release. Work top to bottom.

## Release flow

1. **Write the "what's new" prose in README.md** — version badges and
   install snippets are usually dynamic, but the feature summary is
   judgment work that no script does for you.
2. **Stage the README:** `git add README.md`
3. **Run `python .release/release.py --commit X.Y.Z`** — this:
   - bumps `__version__` in `pyproject.toml` and `<package>/__init__.py`
   - prepends the new entry to `CHANGELOG.md` from `UNRELEASED.md`
   - resets `UNRELEASED.md`
   - commits everything staged (README included) with message `Release vX.Y.Z`
   - creates tag `vX.Y.Z`
   - pushes the branch and the tag
4. **`gh release create vX.Y.Z --title 'vX.Y.Z' --notes-file CHANGELOG.md`**
   — this is what triggers `publish.yml` → PyPI.

## Items `release.py --commit` does NOT handle

- ⚠️⚠️ **README.md** — pre-stage before running --commit
- ⚠️ **GitHub release creation** — intentionally manual (kept as a
  sanity checkpoint before anything hits PyPI)

## One-time PyPI setup (per project)

`publish.yml` uses PyPI **trusted publishing** (OIDC, no API token). Before the
first publish works, configure it once:

1. On PyPI, register the project's trusted publisher: the GitHub repo, the
   workflow file `publish.yml`, and the environment name `pypi`.
2. In the GitHub repo settings, create an Environment named `pypi`.

After that, every `gh release create vX.Y.Z` publishes automatically.

## Non-automated fallback

If you don't want to use `--commit` (e.g. reviewing the diff first),
run `python .release/release.py X.Y.Z` and follow the manual checklist
it prints.
