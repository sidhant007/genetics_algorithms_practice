import random as rand

class game:

    def __init__(self, rows, cols, num_fires, start_x, start_y):
        self.grid = [['N' for x in range(rows)] for y in range(cols)]
        self.r = rows
        self.c = cols
        self.player = player(start_x, start_y)
        self.setFire(num_fires)
        self.grid[self.player.x][self.player.y] = 'P'

    def setFire(self, n):
        i = 0
        while(i < n):
            row = rand.randint(0, self.r - 1) 
            col = rand.randint(0, self.c - 1)
            if(self.grid[row][col] == 'N' and (row != self.player.x or col != self.player.y)):
                self.grid[row][col] = 'F'
                i+=1

    def spreadFire(self):
        fires = list()
        for r in range(self.r):
            for c in range(self.c):
                if(self.grid[r][c] == 'F'):
                    fires.append([r,c])
        for fire in fires:
            r = fire[0]
            c = fire[1]
            if r + 1 < self.r:
                self.grid[r+1][c] = 'F'
            if r - 1 >= 0:
                self.grid[r-1][c] = 'F'
            if c + 1 < self.c:
                self.grid[r][c+1] = 'F'
            if c - 1 >= 0:
                self.grid[r][c-1] = 'F'
    
    def waterBomb(self):
        print("Player used power bomb!")
        px = self.player.x
        py = self.player.y
        for x in range(px - 1, px + 2):
            for y in range(py - 1, py + 2):
                self.grid[x][y] = 'N'
        self.grid[px][py] = 'P'

    def actPlayer(self):
        opx = self.player.x
        opy = self.player.y
        playerMove = self.player.makeMove(self.r, self.c)
        npx = playerMove[0]
        npy = playerMove[1]
        if npx == 0 and npy == 0:
            self.waterBomb()
        else:
            self.grid[opx][opy] = 'N'
            self.grid[self.player.x][self.player.y] = 'P' if self.grid[self.player.x][self.player.y] != 'F' else 'F'
    
    def rewardPlayer(self):
        px = self.player.x
        py = self.player.y
        if px < 0 or px == self.r or py < 0 or py == self.c:
            return 1000
        elif self.grid[px][py] == 'F':
            return -10000
        else:
            nf = 0
            for x in range(px - 1, px + 2):
                for y in range(py - 1, py + 2):
                    if x >= 0 and x < self.r and y >=0 and y < self.c and self.grid[x][y] == 'F':
                        nf += 1
            return -50 * nf - 10

    def printGrid(self):
        print('\n'.join([''.join(['{:4}'.format(item) for item in row]) for row in self.grid]))

class player:
    
    def __init__(self, sx, sy):
        self.x = sx
        self.y = sy
        self.score = 0

    def makeMove(self, bx, by):
        moves = [[0,0], [0,1], [0,-1], [1,0], [-1,0]]
        move = moves[0]
        while(not self.update(move, bx, by)):
            move = rand.choice(moves)
        return move

    def update(self, nextMove, bx, by):
        nx = self.x + nextMove[0]
        ny = self.y + nextMove[1]
        if nx >= 0 and nx < bx and ny >= 0 and ny < by:
            self.x = nx
            self.y = ny
            return True
        else:
            return False

    def updateReward(self, reward):
        self.score += reward


g = game(8, 8, 3, 4, 4)
for i in range(10):
    g.printGrid()
    print("Moving player")
    g.actPlayer()
    g.printGrid()
    print("Spreading Fire")
    g.spreadFire()
    g.printGrid()
    reward = g.rewardPlayer()
    g.player.updateReward(reward)
    print("Player has " + str(g.player.score) + " points")
    if reward == -10000:
        print("Game over")
        break
    
