# Lab 5: Static Code Analysis — Issue Documentation

**Repository:** `L5_38_tournament_scoreboard`  
**Target File:** `tournament_scoreboard.py`  
**Python Version:** Python 3.12.10  
**Tools Evaluated:** Pylint 4.1.3, Bandit 1.9.4, Flake8 7.4.1  

---

## 1. Summary of Analysis Results

| Static Analysis Tool | Before Fixes | After Fixes | Status |
|----------------------|--------------|-------------|--------|
| **Bandit** | 4 issues (1 High, 1 Medium, 2 Low) | 0 High, 0 Medium (Low informational subprocess warnings documented) | Vulnerabilities Eliminated |
| **Flake8** | 4 issues (E203, E302, E231, E261) | 0 issues | Clean PEP 8 Compliance |
| **Pylint** | Score: **4.75 / 10** | Score: **10.00 / 10** (+5.25 improvement) | Clean Quality Rating |

---

## 2. Documented Issues and Fix Approaches

| # | Issue | Tool | Type | Severity | Original Line(s) | Description | Fix Approach | Verification Result |
|---|-------|------|------|----------|------------------|-------------|--------------|---------------------|
| 1 | **Command Injection via Shell** (`B605`, CWE-78) | Bandit | Security Vulnerability | **High** | 71 | `publishTable` used `os.system("scp table.json " + server + ":/var/www/")` with string concatenation. If `server` contains shell metacharacters (e.g. `; rm -rf /`), arbitrary commands are executed. | Replaced `os.system` with `subprocess.run` using a resolved executable path (`shutil.which("scp") or "/usr/bin/scp"`) and argument list (`shell=False`). | **Fixed**: B605 eliminated. No shell invoked. |
| 2 | **Insecure Temporary File Creation** (`B306`, CWE-377) | Bandit | Security Vulnerability | **Medium** | 66 | `tableFilePath` used `tempfile.mktemp(suffix=".json")`. `mktemp` returns a filename without creating it, introducing a Time-of-Check to Time-of-Use (TOCTOU) race condition vulnerable to symlink attacks. | Replaced `tempfile.mktemp()` with `tempfile.NamedTemporaryFile(suffix=".json", delete=False)` which creates the file atomically with secure file permissions. | **Fixed**: B306 eliminated in Bandit. |
| 3 | **Mutable Default Argument** (`W0102`) | Pylint | Bug / Logic Defect | Medium | 11 | `def addTeam(teamName, players=[]):` uses an empty list as default. Python evaluates default arguments once at definition time, causing the list to be shared across all subsequent calls that omit `players`. | Changed default argument to `players=None` and initialized `players = []` inside the function body when `players is None`. | **Fixed**: W0102 eliminated in Pylint. |
| 4 | **Hardcoded Plaintext Password** (`B105`, CWE-259) | Bandit | Security Vulnerability | Low | 6 | `REFEREE_PASSWORD = "referee-demo"` hardcoded credentials directly into source code, exposing sensitive data in version control. | Replaced hardcoded literal with `os.getenv("REFEREE_PASSWORD", "")` to read credentials dynamically from environment variables. | **Fixed**: B105 eliminated in Bandit. |
| 5 | **Cryptographically Insecure RNG** (`B311`, CWE-330) | Bandit | Security / Weakness | Low | 61 | `tossCoin` used `random.choice(["Heads", "Tails"])`. The `random` module uses the Mersenne Twister PRNG, which is deterministic and predictable. | Replaced `random.choice` with `secrets.choice` from Python's standard `secrets` module for cryptographically strong randomness. | **Fixed**: B311 eliminated in Bandit. |
| 6 | **Whitespace Before Colon** (`E203`) | Flake8 | Style / PEP 8 | Low | 5 | `POINTS = {"win" : 3, "draw": 1, "loss": 0}` contained illegal whitespace before the colon in dictionary key. | Removed space before colon: `{"win": 3, ...}`. | **Fixed**: E203 eliminated in Flake8. |
| 7 | **Missing Blank Lines Between Functions** (`E302`) | Flake8 | Style / PEP 8 | Low | 60 | Only one blank line preceded the top-level function `tossCoin` instead of the two required by PEP 8. | Added two blank lines before function definition. | **Fixed**: E302 eliminated in Flake8. |
| 8 | **Missing Whitespace After Comma** (`E231`) | Flake8 | Style / PEP 8 | Low | 79 | `recordMatch("Royal Strikers", "City Rovers", 2,1)` lacked whitespace after `,`. | Added space after comma: `2, 1`. | **Fixed**: E231 eliminated in Flake8. |
| 9 | **Insufficient Spaces Before Inline Comment** (`E261`) | Flake8 | Style / PEP 8 | Low | 87 | Only one space preceded inline comment `# one row per team` instead of the required two spaces. | Ensured at least two spaces precede the inline comment. | **Fixed**: E261 eliminated in Flake8. |
| 10 | **Missing Module & Function Docstrings** (`C0114`, `C0116`) | Pylint | Quality / Documentation | Convention | 1, 11-74 | Missing module docstring and docstrings for all top-level functions (`add_team`, `match_result`, `record_match`, etc.). | Added comprehensive descriptive docstrings to module header and every function. | **Fixed**: C0114 and C0116 eliminated in Pylint. |
| 11 | **Non-snake_case Identifiers** (`C0103`) | Pylint | Style / Naming | Convention | 11-74 | Function and argument names used camelCase (`addTeam`, `teamName`, `matchResult`, etc.) instead of PEP 8 snake_case. | Renamed functions and arguments to PEP 8 snake_case conventions (`add_team`, `team_name`, `match_result`, etc.). | **Fixed**: All C0103 naming warnings eliminated. |
| 12 | **Unnecessary `elif` After `return`** (`R1705`) | Pylint | Code Refactoring | Refactor | 17 | `matchResult` had unnecessary `elif` and `else` branches following unconditional `return` statements. | Simplified control flow to sequential guard `if` clauses and a default return. | **Fixed**: R1705 eliminated in Pylint. |
| 13 | **Consider Merging Comparisons with `in`** (`R1714`) | Pylint | Code Refactoring | Refactor | 58 | `teamName == table[0] or teamName == table[1]` repeated equality tests on same variable. | Refactored to `team_name in (table[0], table[1])`. | **Fixed**: R1714 eliminated in Pylint. |

---

## 3. False Positives and Audit Findings Analysis

- **Bandit B404 (`blacklist_imports: subprocess`) & B603 (`subprocess_without_shell_equals_true`):**
  - **Context:** In `publish_table(server)`, Bandit flags importing `subprocess` and calling `subprocess.run` with Low severity audit warnings.
  - **Analysis:** Bandit issues B603 as a generic advisory whenever `subprocess` is invoked without `shell=True`. Because `shell=False` is used, arguments are passed as an explicit list `[scp_bin, "table.json", f"{server}:/var/www/"]`, and the executable path is resolved via `shutil.which("scp")`, shell command injection (the original High-severity vulnerability B605) is completely neutralized. This finding is an informational audit reminder rather than an active exploit.
