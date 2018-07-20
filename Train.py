import Bird

populationCount = 10

birds = [Bird.Bird(i+1) for i in range(populationCount)]


for bird in birds:
    bird.startPlaying()
    print("Bird {} done".format(bird.index))