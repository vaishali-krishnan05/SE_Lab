# Static Code Analysis — Issues Found

| Issue | Type | Line(s) | Description | Fix Approach |
|---|---|---|---|---|
| Unsafe shell command | Security | Check Bandit report | `os.system()` executes a shell command constructed using a filename. | Replace shell execution with a safe Python file-reading approach. |
| Bare exception | Code quality | Check Pylint report | `except:` catches all exceptions and hides unexpected errors. | Catch the specific exception expected and handle it explicitly. |
| Mutable default argument | Bug | Check Pylint report | `equipment_list=[]` reuses a mutable list as the default argument. | Use `None` as the default and create a new list inside the function. |
| Unclosed file handling | Code quality | Check Pylint report | Files are opened and closed manually, so errors can prevent proper closing. | Use `with open(...)` context managers. |
| Incorrect input type | Bug | Check program and reports | `schedule_room()` is called with an integer slot, but later code expects a string. | Validate inputs and reject invalid slot types. |
| Equipment availability | Bug | Check program behavior | Equipment counts can become negative when more equipment is requested than is available. | Validate equipment names and stock before making a reservation. |
