# -*- coding: utf-8 -*-
"""
 novelWriter – Text Analysis Class
===================================
 Class for analysing bits of text.

 File History:
 Created: 2018-09-22 [0.0.1]

"""

import logging
import nw

from time import time

logger = logging.getLogger(__name__)

class TextAnalysis():

    def __init__(self, theText, langCode):
        self.theText  = theText
        self.langCode = langCode
        return

    def getStats(self):
        tStart = time()
        wordCount = self._countWords()
        tEnd   = time()-tStart
        logger.verbose("Words:       %7d in %8.3f ms" % (wordCount,tEnd*1e3))
        tStart = time()
        sentCount = self._countSentences()
        tEnd   = time()-tStart
        logger.verbose("Sentences:   %7d in %8.3f ms" % (sentCount,tEnd*1e3))
        tStart = time()
        paraCount = self._countParagraphs()
        tEnd   = time()-tStart
        logger.verbose("Paragraphs:  %7d in %8.3f ms" % (paraCount,tEnd*1e3))
        return wordCount, sentCount, paraCount

    def getReadabilityScore(self):
        """Calculate Flesch--Kincaid Readability Score.
        """
        tStart = time()
        wordCount = self._countWords()
        sentCount = self._countSentences()
        if self.langCode[:3] == "en_":
            ratSyllWord = self._countSyllablesEN()
        else:
            ratSyllWord = -1.0
        rScore = 206.835 - 1.015*(wordCount/sentCount) - 84.6*(ratSyllWord)
        gLevel = -15.59  + 0.390*(wordCount/sentCount) + 11.8*(ratSyllWord)
        tEnd   = time()-tStart
        logger.verbose("Readability: %7.3f in %8.3f ms" % (rScore,tEnd*1e3))
        logger.verbose("Grade Level: %7.3f in %8.3f ms" % (gLevel,tEnd*1e3))
        logger.verbose("Assessment:  %s" % self.getReadabilityText(rScore))

        return rScore, gLevel

    def getReadabilityText(self, rScore):
        if rScore >= 90.0:
            return "Very Easy"
        elif rScore >= 80.0:
            return "Easy"
        elif rScore >= 70.0:
            return "Fairly Easy"
        elif rScore >= 60.0:
            return "Average"
        elif rScore >= 50.0:
            return "Fairly Difficult"
        elif rScore >= 30.0:
            return "Difficult"
        else:
            return "Very Difficult"

    #
    #  Internal Functions
    #

    def _countWords(self):
        """Counts the number of words in a text by simply splitting on
        all white spaces.
        """
        return len(self.theText.strip().split())

    def _countSentences(self):
        """Counts the number of non-repeated sentence endings seen in
        the text. Note: This will count filenames and urls as multiple
        sentences.
        """
        nSent  = 0
        sawEnd = False
        for ch in self.theText.strip():
            if ch in ".!?":
                if not sawEnd:
                    sawEnd = True
                    nSent += 1
            else:
                sawEnd = False
        return nSent

    def _countParagraphs(self, pThreshold=2):
        """Counts the number of paragraphs by counting repeated line
        breaks.
        """
        nPara  = 1
        sawEnd = 0
        for ch in self.theText.strip():
            if ch == "\r": # Ignore Windows line end chars
                continue
            if ch == "\n": # Count endlines
                sawEnd += 1
            else: # If non-endline is encountered, check condition for paragraph
                if sawEnd >= pThreshold:
                    nPara += 1
                    sawEnd = 0
        return nPara

    def _countSyllablesEN(self):
        """Attempt to count the syllables in a piece of English language
        text. This function tends to slightly over-estimate the number
        of syllables as it doesn't handle the complexity of silent
        vowels in endings very well. It will count them all.
        """

        cleanText = ""
        for ch in self.theText:
            if ch in "abcdefghijklmnopqrstuvwxyz'’":
                cleanText += ch
            else:
                cleanText += " "

        asVow = "aeiouy'’"
        dExept = ("ei","ie","ua","ia","eo")
        theWords = cleanText.lower().split()
        allSylls = 0
        for inWord in theWords:
            nChar  = len(inWord)
            nSyll  = 0
            wasVow = False
            wasY   = False
            if nChar == 0:
                continue
            if inWord[0] in asVow:
                nSyll += 1
                wasVow = True
                wasY   = inWord[0] == "y"
            for c in range(1,nChar):
                isVow  = False
                if inWord[c] in asVow:
                    nSyll += 1
                    isVow = True
                if isVow and wasVow:
                    nSyll -= 1
                if isVow and wasY:
                    nSyll -= 1
                if inWord[c:c+2] in dExept:
                    nSyll += 1
                wasVow = isVow
                wasY   = inWord[c] == "y"
            if inWord.endswith(("e")):
                nSyll -= 1
            if inWord.endswith(("le","ea","io")):
                nSyll += 1
            if nSyll < 1:
                nSyll = 1
            allSylls += nSyll

        return allSylls/len(theWords)

# END Class TextAnalysis
