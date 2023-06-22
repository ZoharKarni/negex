forked from chapmanbe/negex.
negex.py -- A python module to implement Wendy Chapman's NegEx algorithm.
The original NegEx algorithm is published at:
http://www.dbmi.pitt.edu/chapman/NegEx.html

This folder includes 5 files.
1) 	negex.py: Python implementation of NegEx.
	It can tag definitive negations only or both definitive and possible negations.
2) 	negex_triggers.csv:
	This file lists the rules that were used to test negex.py. Users are free to use anything as a rule but they should follow the style of the example rule file.
3) 	annotations.csv:
	The sentences to check negations.
4) 	phrases.csv:
	List of medical phrases that we are interested in checking whether they have been negated.
5)	README: This file.

The output will be called output.csv and will automatically saved in the folder. It will have the following structure:
Sentence, Sentence.with.tags, Decision

The code was written in Python 3.10.

Tags are:    [PREN] - Prenegation rule tag
             [POST] - Postnegation rule tag
             [PREP] - Pre possible negation tag
             [POSP] - Post possible negation tag
             [PSEU] - Pseudo negation tag
             [CONJ] - Conjunction tag
             [PHRASE] - Term is rcognized from the term list, we search negation for but was NOT negated
             [NEGATED] - Term was recognized from term list, and it was found being negated
             [POSSIBLE] - Term was recognized from term list, and was found as possible negation
