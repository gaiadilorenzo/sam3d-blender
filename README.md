# SAM3D Blender 

A small Blender add-on and tooling to turn images into 3D assets.

Quick guide
------------------------------------

This project uses Ruff for formatting and lint checks and provides a `pre-commit` configuration so checks run automatically on commit.

Set up your environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install ruff pre-commit
```

Enable the pre-commit hooks in your local repo (runs on every commit):

```bash
pre-commit install
```

To run the hooks once across the whole repository (recommended before making a PR):

```bash
pre-commit run --all-files
```

If Ruff reports errors you can fix automatically, the pre-commit hook is configured to attempt fixes (`ruff-check --fix`) and then run the formatter. After `pre-commit run --all-files` you can review changes and commit them.

If you'd rather run Ruff directly:

```bash
ruff format .
ruff check .
```

Contributing 
------------------------------------


Feel free to open issues or PRs; include a short description of the change and which files you ran `ruff format` on (if applicable).