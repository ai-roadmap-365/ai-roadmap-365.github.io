# Package Manager Command Cheat Sheet

The same task, three managers. Learn the model once and read across the row.
Commands that change the system are marked; this lab runs only the read-only
ones (search, list, version, info).

| Task | Homebrew (macOS) | apt (Debian/Ubuntu) | winget (Windows) |
| --- | --- | --- | --- |
| Show the manager's version | `brew --version` | `apt --version` | `winget --version` |
| Refresh the repository index | `brew update` | `sudo apt update` | (automatic) |
| Search for a package | `brew search wget` | `apt search wget` | `winget search wget` |
| Show info about a package | `brew info wget` | `apt show wget` | `winget show wget` |
| **Install** a package | `brew install wget` | `sudo apt install wget` | `winget install wget` |
| List installed packages | `brew list` | `apt list --installed` | `winget list` |
| **Upgrade** everything | `brew upgrade` | `sudo apt upgrade` | `winget upgrade --all` |
| **Remove** a package | `brew uninstall wget` | `sudo apt remove wget` | `winget uninstall wget` |
| Show a package's dependencies | `brew deps --tree wget` | `apt-cache depends wget` | (see `winget show`) |

## Notes

- **sudo:** apt installs system-wide, so its *changing* commands (install,
  upgrade, remove) need administrator rights via `sudo`. Homebrew installs into
  your user space and normally does not. On Windows, winget may prompt for
  elevation for some installers.
- **update vs upgrade (apt):** `apt update` refreshes the local copy of the
  repository index; `apt upgrade` actually moves installed packages to newer
  versions. They are different commands — do not confuse them.
- **Read-only vs changing:** version, search, info, list, and dependency
  queries change nothing and are safe to explore with. Install, upgrade, and
  remove change your system — run them deliberately.
- **Language managers:** `pip install <name>` (Python) and `npm install <name>`
  (Node.js) follow the same model one layer down, for code libraries rather
  than whole applications. You will meet them in a later lesson.
