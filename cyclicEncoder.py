from polynomialOperations import divideBytes

class CyclicEncoder:
    fileArray = []
    generator = 0

    def encodeWord(self, word):
        quotient, remainder = divideBytes(word,self.generator)
        encodedWord = word ^ remainder
        return encodedWord

    def encodeFile(self):
        encodedFile = []
        word = 0
        k = 2
        for byte in self.fileArray:
            for i in range(8):
                k += 1
                word = word | (((byte >> i) & 1) << k)
                if k >= 6:
                    encodedWord = self.encodeWord(word)
                    print(encodedWord)
                    encodedFile.append(encodedWord)
                    word = 0
                    k = 2

        return encodedFile

    def __init__(self,fileArray, generator):
        self.fileArray = fileArray
        self.generator = generator

