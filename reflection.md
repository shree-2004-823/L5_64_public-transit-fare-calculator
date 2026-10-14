1. What was the most important bug to fix?
   The daily fare-cap bug was the most important because it caused a day total to exceed the legal maximum. That breaks the business rule and can overcharge riders.

2. Which static analysis tools were most useful?
   Pylint helped catch naming and maintainability issues, Flake8 found style violations such as overlong lines, and Bandit highlighted the security risks in the gate upload and checksum logic. Together they gave both a quality and a security view of the code.

3. Why do security issues matter in a fare calculator?
   Even a small flaw in a transit system can lead to incorrect charges, data tampering, or remote command execution. Fare calculators are trusted systems, so a weak hash or unsafe SSH command can damage both customer trust and system integrity.

4. How would I prevent these issues in future?
   I would run linting and security scans in CI, write small tests around edge cases like daily caps and invalid fare categories, avoid mutable default arguments, and prefer hardened libraries like `defusedxml` and strong hashing algorithms such as SHA-256.
