# Package Manager Worksheet — Day 013

Fill this in for **your** machine using the read-only commands from the lab.
Do **not** run any install command — this worksheet only records what you find
and what you *would* type.

## 1. Which package managers does your machine have?

Run `command -v brew apt apt-get winget pip pip3 npm` (or `bash examples/detect_pkg_manager.sh`)
and list every one it found:

- Package manager(s) found: `__________________________`

## 2. Your default system package manager

Based on your operating system, which is the *default* system package manager?
(macOS → Homebrew; Debian/Ubuntu → apt; Windows → winget.)

- My operating system: `__________________________`
- My default system package manager: `__________________________`

## 3. How you would install `wget` (write it — do NOT run it)

Write the exact command you *would* use to install the `wget` package on your
operating system. Do not run it.

- Install command for `wget`: `__________________________`

  (macOS: `brew install wget` · Debian/Ubuntu: `sudo apt install wget` · Windows: `winget install wget`)

## 4. One package you already have installed

List one package that is already installed, from `brew list`,
`apt list --installed`, or `winget list`:

- A package I already have: `__________________________`

## 5. Short reflection (4–6 sentences)

In your own words, explain why installing that one package with a package
manager was safer and more repeatable than downloading it by hand. Name
**dependency resolution**, **integrity verification**, and **record-keeping**
explicitly.

```
Your paragraph here:



```
