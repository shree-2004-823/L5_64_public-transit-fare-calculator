| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| Daily fare cap is ignored | High | dailyTotal | The function sums each journey and never applies the daily cap to the total, so a day can exceed the legal maximum. | Calculate the total of all fares and return `min(total, DAILY_CAP)` instead of modifying the loop variable. |
| Unsafe SSH gate upload | High | pushFaresToGate | The remote command is built by concatenating untrusted input into a shell command, which can enable command injection. | Validate host and file names, sanitize them, and avoid executing shell commands with raw user input. |
| Weak ticket checksum algorithm | Medium | ticketChecksum | MD5 is cryptographically weak and should not be used for fare integrity checks. | Replace MD5 with SHA-256 and return the hex digest. |
| Mutable default argument in tapOut | Medium | tapOut | A default `categories=[]` is shared between calls, which can leak state across journeys. | Use `None` and create a new list inside the function when needed. |
| Missing validation for concession categories | Medium | journeyFare | Unknown categories cause poor behavior or an exception instead of a controlled result. | Look up the category with `.get(...)` and raise a clear `ValueError` for unsupported values. |
| Unsafe XML parsing | Medium | loadStops | XML parsing is done without a hardened parser and may be exposed to malformed or malicious data. | Use `defusedxml.ElementTree` to parse the XML safely and only keep valid stop names. |

The fixes above were implemented in `fare_calculator.py`, and the program continues to run with the correct daily cap and safe validation logic.
