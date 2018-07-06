from ple.games.flappybird import FlappyBird
import time
from ple import PLE
import NeuralNetwork as nn

game = FlappyBird()
p = PLE(game, fps=30, display_screen=True,
        reward_values=
        {
            "positive": 1.0,
            "negative": -1.0
        },
            force_fps= False)
p.init()
print(game.getGameState())

brain = nn.NeuralNetwork(4, 4, 1)
for i in range(10000):
    if p.game_over():
        p.reset_game()
    state = game.getGameState()
    input = [state['player_y'], state['next_pipe_dist_to_player'], state['next_pipe_top_y'], state['next_pipe_bottom_y']]
    predictedValue = brain.predict(input)
    print(predictedValue)
    if predictedValue[0] > 0.5:
        p.act(119)
