#!/usr/bin/env python

from optparse import OptionParser
import os, logging
import utils
import collections
from itertools import islice
import re

def take(n, iterable):
    "Return first n items of the iterable as a list"
    return list(islice(iterable, n))

class Token:
    def __init__(self, word, tag):
        self.word = word
        self.tag = tag

    def __str__(self):
        return "%s/%s" % (self.word, self.tag)

def create_model(sentences):
    #Create dictionaries for tag counts, and tag bigram counts, respectively
    tag_uni = collections.defaultdict(int)
    tag_bi = collections.defaultdict(lambda: collections.defaultdict(int))
    #Create a dictionary of word counts per tag
    tag_words = collections.defaultdict(lambda: collections.defaultdict(int))

    for sentence in sentences:                  # Updating counts of unigrams, tags and words, and tag bigrams
        sentence.insert(0, Token('', '<s>'))    # Temporarily inserting a sentence-start character so we can count words at beginning of sentence.
        for i, token in enumerate(sentence, 0):
            tag_uni[token.tag] += 1                 # Unigrams
            tag_words[token.tag][token.word] += 1   # Tags and words
            if (i+1) < len(sentence):               # Tag bigrams
                tag_bi[token.tag][sentence[i+1].tag] += 1
        sentence.pop(0)                         # Removing our sentence-start token again.

    #Defining dictionaries into which to populate probabilities of all delicious Viterbi ingredients
    transition = collections.defaultdict(lambda: collections.defaultdict(int))
    emission = collections.defaultdict(lambda: collections.defaultdict(int))

    for i, item in enumerate(tag_bi.items(), 0):        # Calculating transition probabilities
        org = item[0]
        bi = item[1].items()
        count_1 = tag_uni.items()[i][1]
        #print(org, bi, count_1)
        for n in bi:
            count_2 = n[1]
            prob = (float(count_2)+1) / (float(count_1)+45)
            n = n[0]
            transition[org][n] = prob

    for i, item in enumerate(tag_words.items(), 0):     #Calculating emission probabilities
        org = item[0]
        bi = item[1].items()
        count_1 = tag_uni.items()[i][1]
        for n in bi:
            count_2 = n[1]
            prob = float(count_2) / float(count_1)
            n = n[0]
            emission[org][n] = prob
    print(emission)
    model = transition, emission                        #Passing both back to our model
    return model

def predict_tags(sentences, model):

    tagset = ['NN', 'CC', 'CD', 'DT', 'EX', 'FW', 'IN', 'JJ', 'JJR', 'JJS', 'LS', 'MD', 'NNS', 'NNP', 'NNPS', 'PDT', 'POS', 'PRP', 'PRP$', 'RB', 'RBR', 'RBS', 'RP', 'SYM', 'TO', 'UH', 'VB', 'VBD', 'VBN', 'VBP', 'VBG', 'VBZ', 'WDT', 'WP', 'WP$', 'WRB', '.', ',', '``', "''", ')', '(', '$', ':', '#']

    sent_c =0                           #This is just so you don't go nuts watching my slow code run
    for sentence in sentences:          #Code runs in 12 minutes on the CSE servers - both training + testing
        if (sent_c % 100) == 0:
            print "sentence", sent_c
        sent_c+=1

        words = [token.word for token in sentence]  #Grabbing a list of words in sentence.
        viterbi = {}                                #Creating the blank dictionary for this sentence.

        for t in tagset:
            viterbi[t] = [0] * len(sentence)    # Creating the matrix with a width of len(sentence)

        for i, word in enumerate(words, 0):     # Looping through the sentence
            v = 0

            for t in tagset:
                em_prob = model[1][t][word]     # Grabbing the correct emission probability for word given t
                if em_prob == 0:                # Taking care of unseen words in testing, part 1
                    em_prob = float(0.0000001)
                marker_t = ''
                baseline = 0

                for tag in tagset:

                    tr_prob = model[0][tag][t]          # Grabbing the correct transition probability for current tag "t" given each previous tag "tag"
                    if i == 0:                          # If it's the first word in the sentence, we calculate differently.
                        tr_prob = model[0]['<s>'][t]
                        consider = em_prob * tr_prob

                    if i >= 1:                          # For all subsequent words
                        prev = viterbi[tag][i-1][0]
                        consider = em_prob * tr_prob * prev

                    if (consider > baseline):
                        baseline = consider
                        marker_t = t

                # Taking care of unknown words in testing, Part 2
                if marker_t == '':
                    if word == "Yeah" or word == "Ah" or word == "Okay":
                        marker_t = 'UH'
                    elif re.match(r'[0-9]+[,/\.]?[0-9]*', word) or 'million' in word or 'billion' in word:
                        marker_t = 'CD'
                    elif word.endswith('ough'):
                        marker_t = 'IN'
                    elif word == 'I' or word.lower() == 'we' or word.lower() == 'it':
                        marker_t = 'PRP'
                    elif word.istitle() or word.isupper() or word[0].isupper() or re.match(r'[A-Z]', word) or word.endswith('i') or word.endswith('o'):
                        marker_t = 'NNP'
                    elif word.endswith('s'):
                        marker_t = 'NNS'
                    elif word.endswith('ly') or word.endswith('wise'):
                        marker_t = 'RB'
                    elif word.endswith('al') or word.endswith('able') or '-' in word:
                        marker_t = 'JJ'
                    elif word.endswith('ing'):
                        marker_t = 'VBG'
                    elif word.endswith('ed'):
                        marker_t = 'VBD'
                    elif word.endswith('est'):
                        marker_t = 'JJS'
                    elif word.endswith('er'):
                        marker_t = 'JJR'
                    elif word == '$':
                        marker_t = '$'
                    elif word == '(' or word == '{':            #Including these because apparently the curly brackets weren't seen in the
                        marker_t = '('      #training set
                    elif word == ')' or word == '}':
                        marker_t = '('
                    elif word == '&':                           #Neither was "&" as "and"
                        marker_t = 'CC'
                    elif word == "'":
                        marker_t = 'POS'    #The system didn't know how to handle the plural possessive
                    elif word.endswith('ould'):
                        marker_t = 'MD'
                    else:
                        marker_t = 'NN'      #Default case for unknown words

                if baseline > v:
                    v = baseline
                    final = marker_t

                viterbi[t][i] = (baseline, marker_t)         # Update your Viterbi cell here after getting the max!!

            if i == len(sentence)-1:
                sentence[i].tag = final       # Save the final tag so we can add it to our taglist.

        ###########################################
        tags = [] # Starting our backpointer method
        m = 0
        tag = ''

        for i in range((len(sentence)-1), -1, -1):  #Iterating backward through the list
            if i == (len(sentence)-1):              # Appending the last tag in the sentence to our list
                tags.append(sentence[i].tag)
            else:                                   # For all subsequent words, working backwards
                for t in tagset:
                    temp = viterbi[t][i][0]
                    if temp != 0:
                        if viterbi[t][i][0] > m:
                            m = viterbi[t][i][0]
                            tag = viterbi[t][i][1]
                if m == 0:                      #If we originally had "blank" values - for unknown words.
                    for t in tagset:
                        if viterbi[t][i][1] != '':
                            tag = viterbi[t][i][1]


                tags.append(tag)                #Add the final tag value to our reversed list

        tags.reverse()                          #Reversing the list from R-L to L-R
        for i in range(len(sentence)):
            sentence[i].tag = tags[i]           #Zipping the taglist back up to the sentence

    return sentences

if __name__ == "__main__":
    usage = "usage: %prog [options] GOLD TEST"
    parser = OptionParser(usage=usage)

    parser.add_option("-d", "--debug", action="store_true",
                      help="turn on debug mode")

    (options, args) = parser.parse_args()
    if len(args) != 2:
        parser.error("Please provide required arguments")

    if options.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.CRITICAL)

    training_file = args[0]
    training_sents = utils.read_tokens(training_file)
    test_file = args[1]
    test_sents = utils.read_tokens(test_file)

    model = create_model(training_sents)

    ## read sentences again because predict_tags(...) rewrites the tags
    sents = utils.read_tokens(training_file)
    predictions = predict_tags(sents, model)
    accuracy = utils.calc_accuracy(training_sents, predictions)
    print "Accuracy in training [%s sentences]: %s" % (len(sents), accuracy)

    ## read sentences again because predict_tags(...) rewrites the tags
    sents = utils.read_tokens(test_file)
    predictions = predict_tags(sents, model)
    accuracy = utils.calc_accuracy(test_sents, predictions)
    print "Accuracy in testing [%s sentences]: %s" % (len(sents), accuracy)
