# SAM3D Blender 

A small Blender add-on and tooling to turn images into 3D assets.

---

# Developer Setup

## Prerequisites

Clone the required repositories and start their API servers.

#### 1. Clone repositories
- **Sam3** 
```bash
git clone https://github.com/gaiadilorenzo/sam3.git
cd sam3
git checkout feat/api
```

- **Sam3D**
```bash
git clone https://github.com/gaiadilorenzo/sam-3d-objects.git
cd sam-3d-objects
git checkout feat/api
```

#### 2. Start the servers

Follow the instructions in the README files to start the REST API servers:

- [SAM3 segmentation server](https://github.com/gaiadilorenzo/sam3/tree/feat/api#rest-api-server)

- [SAM3 3D object generation server](https://github.com/gaiadilorenzo/sam-3d-objects/tree/feat/api#rest-api-server)

Make sure both servers are running before using the Blender add-on.


## Blender Add-on Development

### VS Code Setup

Install the VS Code extension:

- Blender Development  
  Extension ID: JacquesLucke.blender-development

### Starting Blender

1. Open VS Code
2. Press Cmd + Shift + P (macOS) or Ctrl + Shift + P (Windows/Linux)
3. Run: `> Blender: Start`

Select your Blender executable when prompted.

The add-on will be loaded automatically when Blender starts.


### Hot Reloading the Add-on

To reload the add-on during development (no Blender restart needed): `> Blender: Auto Reload`

This disables and re-enables the add-on internally, calling `unregister()` and `register()`.

Ensure your add-on initializes all state inside `register()` so reload works correctly.


### Configuration

In Blender:

1. Open Edit → Preferences → Add-ons
2. Find your add-on
3. Set the API endpoints for:
   - SAM3 segmentation server
   - SAM3 3D object generation server

These should match the servers started from the `Installation` section.


## Linters & Formatting

This project uses Ruff for linting and formatting and provides a pre-commit configuration.

### Recommended environment setup

python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install ruff pre-commit

### Enable pre-commit hooks

Run once per repository:

pre-commit install

Hooks will now run automatically on every commit.

### Run all checks manually

Recommended before opening a PR:

pre-commit run --all-files

If Ruff reports fixable issues, the hooks will:
- apply automatic fixes (ruff check --fix)
- run the formatter

Review the changes and commit them.

### Run Ruff directly (optional)

ruff format .
ruff check .

---

# Contributing 

Feel free to open issues or PRs; include a short description of the change and which files you ran `ruff format` on (if applicable).