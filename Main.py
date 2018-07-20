from ple.games.flappybird import FlappyBird
import time
from ple import PLE
import NeuralNetwork as nn

game = FlappyBird()
p = PLE(game, fps=30, display_screen=True,
            force_fps= False)
p.init()
print(game.getGameState())

brain = nn.NeuralNetwork(4, 4, 2)
for i in range(10000):
    if p.game_over():
        p.reset_game()
    state = game.getGameState()
    input = [state['player_y'] / 512, (state['next_pipe_dist_to_player'] - 65) / 288, state['next_pipe_top_y'] / 512, state['next_pipe_bottom_y'] / 512]
    predictedValue = brain.predict(input)
    print(predictedValue)
    if predictedValue[0] > predictedValue[1]:
        print(p.act(119))
