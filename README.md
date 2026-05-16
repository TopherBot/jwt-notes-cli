# jwt-notes-cli

A simple, self‑contained command‑line notes manager protected by JWT authentication.

## Features
- **Typed configuration** using Pydantic (`Settings`).
- **JWT‑secured** sessions (login / logout).
- **Typer** based CLI with sub‑commands `login`, `logout`, `add`, and `list`.
- Stores notes as plain text files under `~/.jwt_notes` (for demo purposes).

## Installation
```bash
# Clone the repository (or copy the files)
git clone https://github.com/yourname/jwt-notes-cli.git
cd jwt-notes-cli

# Create a virtual environment (optional but recommended)
python -m venv .venv && source .venv/bin/activate

# Install dependencies
pip install typer pydantic pyjwt
```

## Configuration
Create a `.env` file in the project root with a secret key used to sign JWTs:
```dotenv
JWT_NOTES_SECRET=your‑very‑secret‑key
```
You can also set the environment variable directly:
```bash
export JWT_NOTES_SECRET=your‑very‑secret‑key
```
The default token expiry is 60 minutes; adjust `token_expiry_minutes` in the `Settings` class if needed.

## Usage
```bash
# Login (creates a JWT stored in ~/.jwt_notes/token.jwt)
python main.py login

# Add a note
python main.py add "Remember to back up the database"

# List all notes
python main.py list

# Logout (removes the stored JWT)
python main.py logout
```

## License
MIT – see `LICENSE` for details.
