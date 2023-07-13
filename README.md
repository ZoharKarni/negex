Forked from chapmanbe/negex.

negex.py -- A python module to implement Wendy Chapman's NegEx algorithm.

A code that mark the negation of medical expressions in sentences.

Unlike the original repository, this one doesn't require ground truth of the negation - it will simply return "Negated" if the expression is negated or "Affirmed" if it is not.
Another addition - this code also works in the Hebrew language, adapted for Python 3 version, and reads from .csv files (instead of .txt).
Unlike the original repository, this code can search for several different medical expressions per sentence (rather than just one term per sentence).
