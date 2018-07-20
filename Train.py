from Bird import FlappyBird


populationCount = 1
def main():
    birds = [FlappyBird(i) for i in range(populationCount)]
    
    for bird in birds:
        bird.init()
    while True:
        if 1.0 == birds[0].finalGameOver.value:
            break
        # print(birds[0].getGameState())
    for bird in birds:
        bird.process.join()

if __name__ == '__main__':
    main()