### Reversi

基于蒙特卡洛搜索树实现的黑白棋AI，暂时只提供pygame实现的图形化版本

### 开始

```
pip install -r requirements.txt
python main.py
```

### 关于对战强度

你可以修改config.py的DIFFICULTY来修改游戏的难度（事实上这是蒙特卡洛树迭代的次数）

更大的数字意味着更高的难度，和更长的等待

默认搜索次数500

```
DIFFICULTY=500
```
