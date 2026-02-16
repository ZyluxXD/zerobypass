# Zerobypass

![GitHub stars](https://img.shields.io/github/stars/ZyluxXD/zerobypass?style=social)
![PyPI](https://img.shields.io/pypi/v/zerobypass)
![License](https://img.shields.io/github/license/ZyluxXD/zerobypass)

Proof of concept tool to bypass document replay technology (such as GPTZero). Uses Playwright automation to simulate
human typing behavior.
___

## Requirements

- Python 3.11 or newer
- Display and clipboard access.

___

> [!CAUTION]
>
> **Disclaimer - Research and Testing Only**  
> This project and its contents are provided strictly for research and testing purposes. They are not intended for
> educational use, including but not limited to classroom assignments, coursework, exams, tutorials, or any form of
> formal
> instruction or certification.  
> Do not use, submit, distribute, or present this code or its outputs as part of academic work or educational materials
> without explicit permission from the project maintainers and any affected parties. The authors and maintainers make no
> representations or warranties regarding suitability for educational use.  
> Use of this project is at your own risk. The authors and contributors accept no liability for any damages, legal
> consequences, or disciplinary actions that may arise from misuse, including presenting this work in an academic
> context
> where it is not allowed.  
> If you require a version of this project for legitimate educational purposes, please contact the devs.

___

## Installation

**Install using pipx** (recommended)

```bash
pipx install zerobypass
```

**Install using uv**

```bash
uv tool install zerobypass
```

**Install using pip** (not recommended)

```bash
pip install zerobypass #--break-system-packages
```

**Install from source**

``` bash
git clone https://github.com/ZyluxXD/zerobypass.git`
cd zerobypass
```

___

## Quick Start

Run:

```bash
zerobypass
```

or

```bash
python -m zerobypass
```

___

## Arguments

`browser-data-dir`
Specifies a custom browser profile directory.

⚠️ **Warning**:

Do **not** point this to an existing personal browser profile. Doing so may corrupt your data.

Always use a cloned directory or a backup.
___


## Notes

- This is still a **Work In Progress** and is **not** finished.
- The Playwright user data directory lives at: `~/.zerobypass`. Delete it to reset the profile.
- Rich text formatting is **not yet supported** — contributions welcome!
___

## Contributing

- Feel free to make pull requests to contribute! There are various TODO's scattered throughout the project, and it would
  be great to help with those!

___
