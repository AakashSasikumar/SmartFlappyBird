# Smart FlappyBird

A small implementation of neuroevolution. A combination of genetic algorithms and neural networks would be used to find make a neural network learn how to play flappy bird

## Requirements
1. python 3.6
2. ple


## Note
- I decided to use multiprocessing to create multiple flappy birds (I wanted to learn multiprocessing in python)
- I realized that the pygame is getting created and stopped completely each time a bird dies and is spawned again
- This project will work completely fine, but the population size might have to be a bit low and the time taken to train (reach super human levels) might take a long time

## TODO
- Change the spawning process such that the game window isn't closed completely each time, and that the same window is reused
## Disclaimer


**This project is still a work in progress**

- I tried using OpenAI gym's flappy bird, but I couldn't get it to work on Windows, so PLE was the best alternative (works on all major OSs).
- PLE proved to be a huge problem to multi-thread so I forked [sourabhv's version of flappy bird](https://github.com/sourabhv/FlapPyBird/) and I've been trying to modify that to suit my needs.