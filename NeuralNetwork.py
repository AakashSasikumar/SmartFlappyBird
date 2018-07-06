import numpy as np

class NeuralNetwork():

    def __init__(self, inputNodes, hiddenNodes, outputNodes):
        self.inputHiddenWeights = np.random.normal(size=(inputNodes, hiddenNodes))
        self.hiddenOutputWeights = np.random.normal(size=(hiddenNodes, outputNodes))

        self.hiddenBias = np.random.normal(size=(hiddenNodes, 1))
        self.outputBias = np.random.normal(size=(outputNodes, 1))
        
        

    def predict(self, input):
        self.hidden = np.dot(np.array(input).T, self.inputHiddenWeights).reshape((-1, 1))
        self.hidden = np.add(self.hidden, self.hiddenBias).reshape(-1)
        self.hidden = self.sigmoid(self.hidden)

        self.output = np.dot(self.hidden.T, self.hiddenOutputWeights).reshape((-1, 1))
        self.output = np.add(self.output, self.outputBias).reshape(-1)
        self.output = self.sigmoid(self.output)
        
        return list(self.output)

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))

    def relu(self, x):
        return np.maximum(x, 0, x)
