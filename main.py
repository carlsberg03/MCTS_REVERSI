import math

import pygame
import random
import sys
from pygame.locals import *


difficulty=500

class Node:
    def __init__(self, now_board, parent=None, action=None, color=""):
        self.visits = 0  # 访问次数
        self.reward = 0.0  # 胜利次数
        self.now_board = now_board  # 棋盘状态
        self.children = []  # 子节点
        self.parent = parent  # 父节点
        self.action = action  # 对应动作
        self.color = color  # 该节点玩家颜色

    def get_ucb(self):
        if self.visits == 0:
            return sys.maxsize  # 未访问的节点ucb为无穷大

        # ucb公式
        explore = math.sqrt(2.0 * math.log(self.parent.visits) / float(self.visits))
        now_ucb = self.reward / self.visits +  explore
        return now_ucb

    # 生个孩子
    def add_child(self, child_now_board, action, color):
        child_node = Node(child_now_board, parent=self, action=action, color=color)
        self.children.append(child_node)

    # 判断是否完全扩展
    def full_expanded(self):
        # 有孩子并且所有孩子都访问过了就是完全扩展
        if len(self.children) == 0:
            return False
        for child in self.children:
            if child.visits == 0:
                return False
        return True


def MCTS(root):
    for i in range(difficulty):
        selected_node = select(root)  # 选择
        leaf_node = expand(selected_node)  # 扩展
        reward = simulate(leaf_node)  # 模拟
        backup(leaf_node, reward)  # 回溯
    max_node = root.children[0]
    max_ucb = -1
    for child in root.children:
        child_ucb = child.get_ucb()
        if max_ucb < child_ucb:
            max_ucb = child_ucb
            max_node = child  # 指向ucb最大的子节点
    return max_node.action[0], max_node.action[1]


def select(node):  # 选择
    if len(node.children) == 0:  # 需要扩展
        return node
    if node.full_expanded():  # 完全扩展,选择ucb最大的子节点
        max_node = None
        max_ucb = -1
        for child in node.children:
            child_ucb = child.get_ucb()
            if max_ucb < child_ucb:
                max_ucb = child_ucb
                max_node = child  # max_node指向ucb最大的子节点
        return select(max_node)
    else:  # 未完全扩展，选取未访问过的节点
        for child in node.children:
            if child.visits == 0:
                return child


def expand(node):  # 扩展
    if node.visits == 0:  # 自身还没有被访问过，不扩展，直接模拟
        return node
    else:
        if node.color == 'b':
            new_color = 'w'
        else:
            new_color = 'b'
        for action in ValMove(board, new_color):  # 遍历所有有效的坐标，将其加入子节点
            new_board = getBoardCopy(node.now_board)
            goformove(new_board, new_color, action[0], action[1])
            node.add_child(new_board, action=action, color=new_color)
        if len(node.children) == 0:
            return node
        return node.children[0]  # 返回新的子列表的第一个，以供下一步模拟


def simulate(node):
    board = getBoardCopy(node.now_board)
    color = node.color
    while not isGameOver(board):
        action_list = ValMove(board, color)
        if not len(action_list) == 0:
            action = action_list[random.randint(0, len(action_list) - 1)]
            goformove(board, color, action[0], action[1])
            if color == 'b':
                color = 'w'
            else:
                color = 'b'
        else:  # 不能下，就交换选手
            if color == 'b':
                color = 'w'
            else:
                color = 'b'
            action_list = ValMove(board, color)
            if len(action_list) != 0:
                action = action_list[random.randint(0, len(action_list) - 1)]
                goformove(board, color, action[0], action[1])
            else:
                break
            if color == 'b':
                color = 'w'
            else:
                color = 'b'

    computerscore = getScoreOfBoard(board)[computerTile]
    playerscore = getScoreOfBoard(board)[playerTile]
    if playerscore < computerscore:
        reward = 1
    else:
        reward = 0
    return reward


def backup(node, reward):
    while node is not None:
        node.visits += 1
        if node.color == computerTile:
            node.reward += reward
        else:
            node.reward -= reward
        node = node.parent
    return 0


def AImove(board):
    root = Node(getBoardCopy(board), None, None, playerTile)
    action = MCTS(root)
    print("validmoves\trewards\tvisits")
    for child in root.children:
        print(child.action,'\t' ':', '\t',child.reward,'\t', child.visits)
    print("--------------------------")
    return action


def resetBoard(board):
    for x in range(8):
        for y in range(8):
            board[x][y] = ' '

    # Starting pieces:
    board[3][3] = 'b'
    board[3][4] = 'w'
    board[4][3] = 'w'
    board[4][4] = 'b'


# 开局时建立新棋盘
def getNewBoard():
    board = []
    for i in range(8):
        board.append([' '] * 8)

    return board


# 是否是合法走法
def validmove(board, color, xstart, ystart):
    if not OnBoard(xstart, ystart) or board[xstart][ystart] != ' ':
        return False

    board[xstart][ystart] = color

    if color == 'b':
        next_color = 'w'
    else:
        next_color = 'b'

    # 要被翻转的棋子
    lsflip = []
    for xdirection, ydirection in [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]:
        x, y = xstart, ystart
        x += xdirection
        y += ydirection
        if OnBoard(x, y) and board[x][y] == next_color:
            x += xdirection
            y += ydirection
            if not OnBoard(x, y):
                continue
            # 一直走到出界或不是对方棋子的位置
            while board[x][y] == next_color:
                x += xdirection
                y += ydirection
                if not OnBoard(x, y):
                    break
            # 出界了，则没有棋子要翻转OXXXXX
            if not OnBoard(x, y):
                continue
            # 是自己的棋子OXXXXXXO
            if board[x][y] == color:
                while True:
                    x -= xdirection
                    y -= ydirection
                    # 回到了起点则结束
                    if x == xstart and y == ystart:
                        break
                    # 需要翻转的棋子
                    lsflip.append([x, y])

    # 将前面临时放上的棋子去掉，即还原棋盘
    board[xstart][ystart] = ' '  # restore the empty space

    # 没有要被翻转的棋子，则走法非法。翻转棋的规则。
    if len(lsflip) == 0:
        return False
    return lsflip


# 是否出界
def OnBoard(x, y):
    return 0 <= x <= 7 and 0 <= y <= 7


# 获取可落子的位置
def ValMove(board, tile):
    goodmove = []

    for x in range(8):
        for y in range(8):
            if validmove(board, tile, x, y):
                goodmove.append([x, y])
    return goodmove


# 获取棋盘上黑白双方的棋子数
def getScoreOfBoard(board):
    xscore = 0
    oscore = 0
    for x in range(8):
        for y in range(8):
            if board[x][y] == 'b':
                xscore += 1
            if board[x][y] == 'w':
                oscore += 1
    return {'b': xscore, 'w': oscore}


# 谁先走
def whoGoesFirst():
    if random.randint(0, 1) == 0:
        print("AI先行")
        return 1
    else:
        print("玩家先行")
        return 0


# 将一个棋子放到(xstart, ystart)
def goformove(board, color, xstart, ystart):
    colorflip = validmove(board, color, xstart, ystart)

    if not colorflip:
        return False

    board[xstart][ystart] = color
    for x, y in colorflip:
        board[x][y] = color
    return True


# 复制棋盘
def getBoardCopy(board):
    dupeBoard = getNewBoard()

    for x in range(8):
        for y in range(8):
            dupeBoard[x][y] = board[x][y]

    return dupeBoard


# 是否在角上
def isOnCorner(x, y):
    return (x == 0 and y == 0) or (x == 7 and y == 0) or (x == 0 and y == 7) or (x == 7 and y == 7)


# 是否游戏结束
def isGameOver(board):
    score = getScoreOfBoard(board)
    if score['b'] == 0 or score['w'] == 0:
        return True

    for x in range(8):
        for y in range(8):
            if board[x][y] == ' ':
                return False
    return True


if __name__ == '__main__':
    # 初始化
    clock = 60
    pygame.init()
    mainClock = pygame.time.Clock()
    pygame.time.get_ticks()
    background = pygame.image.load('assets/bg.png')
    basicFont = pygame.font.SysFont(None, 48)
    gameoverStr = 'Game Over Score '
    board = getNewBoard()
    resetBoard(board)

    who = whoGoesFirst()
    if who == 0:
        playerTile = 'b'
        computerTile = 'w'
    else:
        playerTile = 'w'
        computerTile = 'b'

    # 设置窗口
    screen = pygame.display.set_mode((1000, 800))
    pygame.display.set_caption('MCTS_Reversi')
    text1 = basicFont.render("you", True, 'yellow')
    text2 = basicFont.render("AI", True, 'yellow')
    gameOver = False
    flag = 0
    oldcnt = 0
    # 游戏主循环
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if isGameOver(board) == False and who == 0 and event.type == MOUSEBUTTONDOWN and event.button == 1:
                x, y = pygame.mouse.get_pos()
                flag = 0
                col = int(x / 100)
                row = int(y / 100)
                if goformove(board, playerTile, col, row):
                    if ValMove(board, computerTile):
                        who = 1

            if event.type == KEYUP:
                if event.key == K_q:
                    who = 1
        cnt = int(pygame.time.get_ticks() / 1000)
        if oldcnt != cnt:
            oldcnt = cnt
            if flag != 60:
                flag = flag + 1

        text3 = basicFont.render(str(60 - flag), True, 'yellow')
        screen.fill([80, 80, 80])
        screen.blit(background, (0, 0))
        screen.blit(text1, (870, 730))
        screen.blit(text2, (880, 130))
        screen.blit(text3, (880, 430))
        if isGameOver(board) == False and who == 1:
            x, y = AImove(board)
            goformove(board, computerTile, x, y)
            x_old, y_old = x, y

            if ValMove(board, playerTile):
                who = 0

        score = getScoreOfBoard(board)
        if score['b'] == 0 or score['w'] == 0 or isGameOver(board):
            gameOver = True

        for x in range(8):
            for y in range(8):
                if board[x][y] == 'b':
                    pygame.draw.circle(screen, [0, 0, 0], [45 + 100 * x, 45 + 100 * y], 30, 30)
                elif board[x][y] == 'w':
                    pygame.draw.circle(screen, [255, 255, 255], [45 + 100 * x, 45 + 100 * y], 30, 30)
                elif validmove(board, playerTile, x, y):
                    pygame.draw.circle(screen, [0, 255, 0], [45 + 100 * x, 45 + 100 * y], 20, 20)
                if computerTile == 'b':
                    pygame.draw.circle(screen, [0, 0, 0], [900, 100], 20, 20)
                    pygame.draw.circle(screen, [255, 255, 255], [900, 700], 20, 20)
                if computerTile == 'w':
                    pygame.draw.circle(screen, [255, 255, 255], [900, 100], 20, 20)
                    pygame.draw.circle(screen, [0, 0, 0], [900, 700], 20, 20)
        if isGameOver(board) or flag == 60:
            scorePlayer = getScoreOfBoard(board)[playerTile]
            scoreComputer = getScoreOfBoard(board)[computerTile]
            if scorePlayer > scoreComputer or flag == 60:
                outputStr = "Win" + str(scorePlayer) + ":" + str(scoreComputer)
            elif scorePlayer == scoreComputer:
                outputStr = "draw. " + str(scorePlayer) + ":" + str(scoreComputer)
            else:
                outputStr = "Lose. " + str(scorePlayer) + ":" + str(scoreComputer)
            text = basicFont.render(outputStr, True, [0, 0, 0], [255, 255, 0])
            textRect = text.get_rect()
            textRect.centerx = screen.get_rect().centerx
            textRect.centery = screen.get_rect().centery
            screen.blit(text, textRect)
        pygame.display.update()
        mainClock.tick(40)
