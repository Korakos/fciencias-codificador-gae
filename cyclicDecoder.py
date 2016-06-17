from polynomialOperations import divideBytes
import random

class CyclicDecoder:
    fileArray = []
    decoderPoly = 0

    def decodeFile(self):
        decodedFile = []
        word = 0
        second = False
        for byte in self.fileArray:
            decodedWord = self.decodeWord(byte)

            if second:
                word = word | (decodedWord << 4)
                decodedFile.append(word)
                word = 0
                second = False
            else:
                word = decodedWord
                second = True

        return decodedFile

    def decodeWord(self,word):
        #word = self.addError(word)
        correctWord = self.correctError(word)
        return correctWord >> 3

    def correctError(self, word):
        word = word & 127
        quotient, remainder = divideBytes(word, self.decoderPoly)
        if remainder == 0:
            return word
        else:
            for i in range(7):
                polynomial = 1 << i
                q2, r2 = divideBytes(polynomial, self.decoderPoly)
                if r2 == remainder:
                    return word ^ polynomial

    def addError(self, word):
        return word ^ (1 << random.randint(0,7))

    def __init__(self, fileArray, decoderPoly):
        self.fileArray = fileArray
        self.decoderPoly = decoderPoly