from Bird import FlappyBird


populationCount = 10
def main():
    birds = [FlappyBird(i) for i in range(populationCount)]
    
    for bird in birds:
        bird.init()
    
    for bird in birds:
        bird.process.join()

    

if __name__ == '__main__':
    main()