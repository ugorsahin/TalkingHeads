# Given an existing complete statement or question, generates variations of the sentences using synonym matching.
# Synonym matching code from nickloewen (https://github.com/nickloewen/thesaurus)
# Can either run script and pass arguments in Terminal / Command Prompt, or imported as library.

import sys
import nltk
from nltk.corpus import wordnet
from nltk.tokenize import RegexpTokenizer
import re
nltk.download('wordnet')
class TextRegenerator(object):

    words_to_preserve = []
    words_to_preserve_default = ["a", "the", "in", "of", "at", "does"]
    words_to_preserve.extend([w.title() for w in words_to_preserve])
    punctuation = [".", ",", ":", ";", "?", "!"]


    def __init__(self):

        self.str_base = ""
        self.new_str = ""
        self.new_str_list = []


    def createWordSynonyms(self, word):
        synsets = wordnet.synsets(word)
        synonyms = [word]

        if word not in TextRegenerator.words_to_preserve:
            for s in synsets:
                for l in s.lemmas():
                    synonyms.append(l.name())

        # if there are no synonyms, put the original word in
        synonyms.append(word)
        return self.uniq(synonyms)


    def createPhraseSynonyms(self, _str_base):
        """Finds synonyms for every word in the input. Returns a list, containing a
        list of synonyms for every word in the input."""

        tokenizer = RegexpTokenizer('\w+|\$[\d\.]+|\S+')
        tokens = tokenizer.tokenize(_str_base)

        # synonyms for all words: each word is a list of synonyms inside this one
        synonyms = []
        for t in tokens:
            synonyms.append(self.createWordSynonyms(t))
        return synonyms


    def stripUnderscores(self, word):
        return re.sub("_", " ", word)

    def tidyPunctuation(self, word):
        return re.sub(r'\s([?.!"](?:\s|$))', r'\1', word)

    def uniq(self, seq):
        seen = set()
        seen_add = seen.add
        return [ x for x in seq if x not in seen and not seen_add(x)]


    def permuteAllSynonyms(self, phrase_synonyms):

        output = []

        """Determine which token has the most phrase_synonyms."""
        longest = ""
        for item in phrase_synonyms:
            if len(item) > len(longest):
                longest = item

        # Loop for each synonym in 'longest' list.
        for i in range(len(longest)):
            """Build a new phrase using the first word of each list, then remove
               that word, unless it is the last one."""

            phrase = ""
            for s in phrase_synonyms:
                phrase = phrase + " " + str(s[0])
                if len(s) > 1:
                    s.pop(0)
            output.append(phrase.strip())

        return output


    def generateStrVariations(self, _str_base):

        """Generates variations (through synonym matching) of an inputted string, ignoring
           list of stop words."""

        print('\n\tNow generating variations of: "' + _str_base + '"..')

        #   Use the code block below jf you want to make a list of variations using synonym matching (many of the variations don't make sense)
        output = self.createPhraseSynonyms(_str_base)
        output = self.permuteAllSynonyms(output)
        for phrase in output[0:1]:
            return str(self.tidyPunctuation(self.stripUnderscores(phrase)))


    def addStopWords(self, l_param):

        """Takes in a 'string' (enclosed in quotes, and meant to be typed as a list of words separated
           by commas and spaces) to parse and append to the stop (ignored) words."""
        try:
            l_param = l_param.lower().split(', ')
        except:
            pass
        # print("\n\t" + "Default list of stop words: " + str(TextRegenerator.words_to_preserve_default))
        TextRegenerator.words_to_preserve = list(l_param)
        TextRegenerator.words_to_preserve.extend(x for x in TextRegenerator.words_to_preserve_default if x not in TextRegenerator.words_to_preserve)
        print("\n< < <\n\t")
        print("Final list of stop words: " + str(TextRegenerator.words_to_preserve))


if __name__ == '__main__':
    try:
        l_param = str(sys.argv[2])
    except:
        l_param = []
        pass
    try:
        str_base = str(sys.argv[1]).lower()
    except IndexError as err:
        print("\n\n\tError initializing TextRegenerator: {0}".format(err))
        print("\n\tPossible invalid or no parameter supplied.\n\n\tRun the script again, with either the complete string"
        "you want to generate mass varifations of as the only argument, or the second argument of a list of words to ignore (not" +
        "replace), separated by commas and spaces and enclosed in quotes.")
        print("\n\tExiting..")
        sys.exit(0)
    except:
        print("\n\n\tUnexpected error:", sys.exc_info()[0])
        print("\n\tExiting..")
        sys.exit(0)
    print(l_param)
    trgnr = TextRegenerator()
    trgnr.addStopWords(l_param)
    print(trgnr.generateStrVariations(str_base))
else:
    trgnr = TextRegenerator()
    l_param = []
    trgnr.addStopWords(l_param)