from ple.games.flappybird import FlappyBird
from ple import PLE
import NeuralNetwork as nn

class Bird():
    def __init__(self, index):
        self.index = index
        self.game = FlappyBird()
        self.birdBrain = nn.NeuralNetwork(4, 4, 2)
        self.score = 0
        self.fitness = 0

    def startPlaying(self):
        print("started")
        self.p = PLE(self.game, fps=30, display_screen=True, force_fps= False)
        self.p.init()
        self.state = self.game.getGameState()
        print("inited")
        while not self.game.game_over():
            self.newState = self.game.getGameState()
            # if self.state['player_y'] == self.newState['player_y']:
            #     self.game = FlappyBird()
            #     self.p = PLE(self.game, fps=30, display_screen=True, force_fps= False)
            #     self.p.init()
            self.input = [self.newState['player_y'], self.newState['next_pipe_dist_to_player'], self.newState['next_pipe_top_y'], self.newState['next_pipe_bottom_y']]
            print("got state")
            print(self.newState)
            self.predictedValue = self.birdBrain.predict(self.input)
            print("predicted")
            if self.predictedValue[0] > self.predictedValue[1]:
                self.p.act(119)
        self.score = self.game.getScore()
        print(self.score)