import re
import csv
import argparse
import os

def sortRules(ruleList):
    """Return sorted list of rules.

    Rules should be in a tab-delimited format: 'rule\t\t[four letter negation tag]'
    Sorts list of rules descending based on length of the rule,
    splits each rule into components, converts pattern to regular expression,
    and appends it to the end of the rule. """
    ruleList.sort(key=len, reverse=True)
    sortedList = []
    for rule in ruleList:
        s = rule.strip().split('\t')
        splitTrig = s[0].split()
        trig = r'\s+'.join(splitTrig)
        pattern = r'\b(' + trig + r')\b'
        s.append(re.compile(pattern, re.IGNORECASE))
        sortedList.append(s)
    return sortedList


### functions I added - start
def convert_csv_to_txt(csv_file, txt_file, separator):
    with open(csv_file, 'r', encoding="utf-8") as file:
        csv_reader = csv.reader(file)
        data = list(csv_reader)

    with open(txt_file, 'w', encoding="utf-8") as file:
        for row in data:
            line = separator.join(row)
            file.write(line + '\n')


def convert_txt_to_csv(txt_file, csv_file):
    with open(txt_file, 'r') as file:
        lines = file.readlines()

    with open(csv_file, 'w', newline='') as file:
        csv_writer = csv.writer(file)
        for line in lines:
            row = line.strip().split('\t')
            csv_writer.writerow(row)


def create_csv_with_selected_columns(input_csv, output_csv, selected_columns):
    with open(input_csv, 'r') as input_file:
        with open(output_csv, 'w', newline='') as output_file:
            reader = csv.reader(input_file)
            writer = csv.writer(output_file)

            for row in reader:
                selected_row = [row[column] for column in selected_columns]
                writer.writerow(selected_row)


### functions I added - end

"""# negTagger class"""


class negTagger(object):
    '''Take a sentence and tag negation terms and negated phrases.

    Keyword arguments:
    sentence -- string to be tagged
    phrases  -- list of phrases to check for negation
    rules    -- list of negation trigger terms from the sortRules function
    negP     -- tag 'possible' terms as well (default = True)    '''

    def __init__(self, sentence='', phrases=None, rules=None,
                 negP=True):
        self.__sentence = sentence
        self.__phrases = phrases
        self.__rules = rules
        self.__negTaggedSentence = ''
        self.__scopesToReturn = []
        self.__negationFlag = None

        filler = '_'

        for rule in self.__rules:
            reformatRule = re.sub(r'\s+', filler, rule[0].strip())
            self.__sentence = rule[3].sub(' ' + rule[2].strip()
                                          + reformatRule
                                          + rule[2].strip() + ' ', self.__sentence)
        for phrase in self.__phrases:
            phrase = re.sub(r'([.^$*+?{\\|()[\]])', r'\\\1', phrase)
            splitPhrase = phrase.split()
            joiner = r'\W+'
            joinedPattern = r'\b' + joiner.join(splitPhrase) + r'\b'
            reP = re.compile(joinedPattern, re.IGNORECASE)
            m = reP.search(self.__sentence)
            if m:
                self.__sentence = self.__sentence.replace(m.group(0), '[PHRASE]'
                                                          + re.sub(r'\s+', filler, m.group(0).strip())
                                                          + '[PHRASE]')

        #        Exchanges the [PHRASE] ... [PHRASE] tags for [NEGATED] ... [NEGATED]
        #        based on PREN, POST rules and if negPoss is set to True then based on
        #        PREP and POSP, as well.
        #        Because PRENEGATION [PREN} is checked first it takes precedent over
        #        POSTNEGATION [POST]. Similarly POSTNEGATION [POST] takes precedent over
        #        POSSIBLE PRENEGATION [PREP] and [PREP] takes precedent over POSSIBLE
        #        POSTNEGATION [POSP].

        overlapFlag = 0
        prenFlag = 0
        postFlag = 0
        prePossibleFlag = 0
        postPossibleFlag = 0

        sentenceTokens = self.__sentence.split()
        sentencePortion = ''
        aScopes = []
        sb = []
        # check for [PREN]
        for i in range(len(sentenceTokens)):
            if sentenceTokens[i][:6] == '[PREN]':
                prenFlag = 1
                overlapFlag = 0

            if sentenceTokens[i][:6] in ['[CONJ]', '[PSEU]', '[POST]', '[PREP]', '[POSP]']:
                overlapFlag = 1

            if i + 1 < len(sentenceTokens):
                if sentenceTokens[i + 1][:6] == '[PREN]':
                    overlapFlag = 1
                    if sentencePortion.strip():
                        aScopes.append(sentencePortion.strip())
                    sentencePortion = ''

            if prenFlag == 1 and overlapFlag == 0:
                sentenceTokens[i] = sentenceTokens[i].replace('[PHRASE]', '[NEGATED]')
                sentencePortion = sentencePortion + ' ' + sentenceTokens[i]

            sb.append(sentenceTokens[i])

        if sentencePortion.strip():
            aScopes.append(sentencePortion.strip())

        sentencePortion = ''
        sb.reverse()
        sentenceTokens = sb
        sb2 = []
        # Check for [POST]
        for i in range(len(sentenceTokens)):
            if sentenceTokens[i][:6] == '[POST]':
                postFlag = 1
                overlapFlag = 0

            if sentenceTokens[i][:6] in ['[CONJ]', '[PSEU]', '[PREN]', '[PREP]', '[POSP]']:
                overlapFlag = 1

            if i + 1 < len(sentenceTokens):
                if sentenceTokens[i + 1][:6] == '[POST]':
                    overlapFlag = 1
                    if sentencePortion.strip():
                        aScopes.append(sentencePortion.strip())
                    sentencePortion = ''

            if postFlag == 1 and overlapFlag == 0:
                sentenceTokens[i] = sentenceTokens[i].replace('[PHRASE]', '[NEGATED]')
                sentencePortion = sentenceTokens[i] + ' ' + sentencePortion

            sb2.insert(0, sentenceTokens[i])

        if sentencePortion.strip():
            aScopes.append(sentencePortion.strip())

        sentencePortion = ''
        self.__negTaggedSentence = ' '.join(sb2)

        if negP:
            sentenceTokens = sb2
            sb3 = []
            # Check for [PREP]
            for i in range(len(sentenceTokens)):
                if sentenceTokens[i][:6] == '[PREP]':
                    prePossibleFlag = 1
                    overlapFlag = 0

                if sentenceTokens[i][:6] in ['[CONJ]', '[PSEU]', '[POST]', '[PREN]', '[POSP]']:
                    overlapFlag = 1

                if i + 1 < len(sentenceTokens):
                    if sentenceTokens[i + 1][:6] == '[PREP]':
                        overlapFlag = 1
                        if sentencePortion.strip():
                            aScopes.append(sentencePortion.strip())
                        sentencePortion = ''

                if prePossibleFlag == 1 and overlapFlag == 0:
                    sentenceTokens[i] = sentenceTokens[i].replace('[PHRASE]', '[POSSIBLE]')
                    sentencePortion = sentencePortion + ' ' + sentenceTokens[i]

                sb3 = sb3 + ' ' + sentenceTokens[i]

            if sentencePortion.strip():
                aScopes.append(sentencePortion.strip())

            sentencePortion = ''
            sb3.reverse()
            sentenceTokens = sb3
            sb4 = []
            # Check for [POSP]
            for i in range(len(sentenceTokens)):
                if sentenceTokens[i][:6] == '[POSP]':
                    postPossibleFlag = 1
                    overlapFlag = 0

                if sentenceTokens[i][:6] in ['[CONJ]', '[PSEU]', '[PREN]', '[PREP]', '[POST]']:
                    overlapFlag = 1

                if i + 1 < len(sentenceTokens):
                    if sentenceTokens[i + 1][:6] == '[POSP]':
                        overlapFlag = 1
                        if sentencePortion.strip():
                            aScopes.append(sentencePortion.strip())
                        sentencePortion = ''

                if postPossibleFlag == 1 and overlapFlag == 0:
                    sentenceTokens[i] = sentenceTokens[i].replace('[PHRASE]', '[POSSIBLE]')
                    sentencePortion = sentenceTokens[i] + ' ' + sentencePortion

                sb4.insert(0, sentenceTokens[i])

            if sentencePortion.strip():
                aScopes.append(sentencePortion.strip())

            self.__negTaggedSentence = ' '.join(sb4)

        if '[NEGATED]' in self.__negTaggedSentence:
            self.__negationFlag = 'Negated'
        elif '[POSSIBLE]' in self.__negTaggedSentence:
            self.__negationFlag = 'Possible'
        else:
            self.__negationFlag = 'Affirmed'

        self.__negTaggedSentence = self.__negTaggedSentence.replace(filler, ' ')

        for line in aScopes:
            tokensToReturn = []
            thisLineTokens = line.split()
            for token in thisLineTokens:
                if token[:6] not in ['[PREN]', '[PREP]', '[POST]', '[POSP]']:
                    tokensToReturn.append(token)
            self.__scopesToReturn.append(' '.join(tokensToReturn))

    def getNegTaggedSentence(self):
        return self.__negTaggedSentence

    def getNegationFlag(self):
        return self.__negationFlag

    def getScopes(self):
        return self.__scopesToReturn

    def __str__(self):
        text = self.__negTaggedSentence
        text += '\t' + self.__negationFlag
        text += '\t' + '\t'.join(self.__scopesToReturn)


"""# Implementation

Need to import two .csv files:
1. `negex_triggers.csv`:
	This file lists the rules that were used to test negex.py. 
2. `Annotations-1-120.csv`: The test kit. Format of the test kit and files with sentences to check negations for follows this structure: Number, Phrase, Sentence, Ground truth.
3. `phrases.csv`: List of medical phrases that we are interested in checking whether they have been negated.
"""


parser = argparse.ArgumentParser(
    prog='negex',
    description='Gets a list of medical terms and returns the constraint for a SQL query')
parser.add_argument('negex_triggers', type=str, help='This file lists the negation rules that were used.')
parser.add_argument('sentences', type=str,
                    help='The test kit. Format of the test kit and files with sentences to check negations for follows this structure: Number, Phrase, Sentence, Ground truth.')
parser.add_argument('phrases', type=str,
                     help='List of medical phrases that we are interested in checking whether they have been negated.')

args = parser.parse_args()
negex = args.negex_triggers
sentences = args.sentences
phrases = args.phrases

convert_csv_to_txt(negex, 'negex_triggers.txt', '\t')  # \t\t
rfile = open(r'negex_triggers.txt')
irules = sortRules(rfile.readlines())
reports = csv.reader(open(sentences))
next(reports, None)  # skip the headers
reportNum = 0
correctNum = 0
ofile = open(r'negex_output.txt', 'w', newline='')
output = []
outputfile = csv.writer(ofile, delimiter='\t')

### The section below replace the "Concept" column in the original "sentences" file with the "phrases" file:
data = []
with open('phrases.csv') as csvfile:
    csvreader = csv.reader(csvfile)
    next(csvreader, None)  # skip the header
    for row in csvreader:
        data.append(row)
list_of_phrases = [cell for row in data for cell in row]
###

for report in reports:
    rphrases = list_of_phrases
    tagger = negTagger(sentence=report[0], phrases=rphrases, rules=irules, negP=False)
    report.append(tagger.getNegTaggedSentence())
    report.append(tagger.getNegationFlag())
    output.append(report)
for row in output:
    if row:
        outputfile.writerow(row)
ofile.close()

# if __name__ == '__main__': main()

"""# Additional code to export .csv file with relevant columns

The file will have the following structure:
Sentence, Sentence.with.tags, Prediction
"""

selected_columns = [0, 2]  # update if needed
convert_txt_to_csv('negex_output.txt', 'negex_output.csv')
create_csv_with_selected_columns('negex_output.csv', 'output.csv', selected_columns)
print("The output.csv file was saved in the folder.")


open(r'negex_output.txt', 'r').close()
os.remove('negex_output.txt')
open(r'negex_output.csv', 'r').close()
os.remove('negex_output.csv')
rfile.close()
os.remove('negex_triggers.txt')
