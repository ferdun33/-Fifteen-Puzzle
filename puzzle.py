# puzzle.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import random
import time
import json
import argparse
from pathlib import Path

# ANSI colors
COLORS = {
    'reset': '\033[0m',
    'red': '\033[91m',
    'green': '\033[92m',
    'yellow': '\033[93m',
    'blue': '\033[94m',
    'magenta': '\033[95m',
    'cyan': '\033[96m',
    'white': '\033[97m',
    'gray': '\033[90m',
    'bold': '\033[1m'
}

def colorize(text, color):
    return f"{COLORS.get(color, '')}{text}{COLORS['reset']}"

# Конфигурация
RECORD_FILE = Path.home() / '.puzzle_records.json'

def load_records():
    if RECORD_FILE.exists():
        try:
            with open(RECORD_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}

def save_records(records):
    with open(RECORD_FILE, 'w') as f:
        json.dump(records, f, indent=2)

class Puzzle:
    def __init__(self, size=4, state=None):
        self.size = size
        self.empty = (size-1, size-1)
        if state:
            self.board = [row[:] for row in state]
            # Найдём пустую
            for i in range(size):
                for j in range(size):
                    if self.board[i][j] == 0:
                        self.empty = (i, j)
        else:
            # Создаём решённое состояние
            self.board = [[i*size + j + 1 for j in range(size)] for i in range(size)]
            self.board[-1][-1] = 0
            self.empty = (size-1, size-1)
        self.moves = 0
        self.start_time = None
        self.size_str = f"{size}x{size}"

    def __str__(self):
        return self.render()

    def render(self):
        result = []
        result.append(colorize('┌' + '─' * (self.size * 4 - 1) + '┐', 'gray'))
        for i in range(self.size):
            row = []
            for j in range(self.size):
                val = self.board[i][j]
                if val == 0:
                    row.append('   ')
                else:
                    color = ['red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white', 'gray'][val % 7]
                    row.append(colorize(f'{val:2} ', color))
            result.append(colorize('│', 'gray') + ''.join(row) + colorize('│', 'gray'))
        result.append(colorize('└' + '─' * (self.size * 4 - 1) + '┘', 'gray'))
        return '\n'.join(result)

    def is_solved(self):
        target = [[i*self.size + j + 1 for j in range(self.size)] for i in range(self.size)]
        target[-1][-1] = 0
        return self.board == target

    def is_solvable(self):
        # Преобразуем в список
        flat = [self.board[i][j] for i in range(self.size) for j in range(self.size) if self.board[i][j] != 0]
        inversions = 0
        for i in range(len(flat)):
            for j in range(i+1, len(flat)):
                if flat[i] > flat[j]:
                    inversions += 1
        if self.size % 2 == 1:
            return inversions % 2 == 0
        else:
            # Для чётного размера учитываем положение пустой
            empty_row = self.empty[0]
            if empty_row % 2 == 0:
                return inversions % 2 == 1
            else:
                return inversions % 2 == 0

    def shuffle(self, moves=100):
        # Делаем случайные ходы, чтобы перемешать
        dirs = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for _ in range(moves):
            r, c = self.empty
            random.shuffle(dirs)
            for dr, dc in dirs:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.size and 0 <= nc < self.size:
                    self.board[r][c], self.board[nr][nc] = self.board[nr][nc], self.board[r][c]
                    self.empty = (nr, nc)
                    break
        self.moves = 0
        self.start_time = None

    def move(self, dr, dc):
        r, c = self.empty
        nr, nc = r + dr, c + dc
        if 0 <= nr < self.size and 0 <= nc < self.size:
            self.board[r][c], self.board[nr][nc] = self.board[nr][nc], self.board[r][c]
            self.empty = (nr, nc)
            self.moves += 1
            if self.start_time is None:
                self.start_time = time.time()
            return True
        return False

def main():
    parser = argparse.ArgumentParser(description="Fifteen Puzzle – Пятнашки")
    parser.add_argument('size', nargs='?', type=int, default=4, help='Размер поля (3,4,5)')
    parser.add_argument('-s', '--seed', help='Строка с начальным состоянием через пробел')
    parser.add_argument('-r', '--record', action='store_true', help='Показать рекорд для данного размера')
    args = parser.parse_args()

    size = args.size
    if size < 3 or size > 5:
        print("Размер должен быть от 3 до 5")
        sys.exit(1)

    records = load_records()
    key = f"{size}x{size}"

    if args.record:
        if key in records:
            rec = records[key]
            print(colorize(f"Рекорд для {key}: {rec['moves']} ходов за {rec['time']} сек", 'green'))
        else:
            print(colorize(f"Нет рекорда для {key}", 'yellow'))
        sys.exit(0)

    # Создаём игру
    if args.seed:
        nums = list(map(int, args.seed.split()))
        if len(nums) != size*size:
            print("Неверное количество чисел")
            sys.exit(1)
        board = [nums[i*size:(i+1)*size] for i in range(size)]
        game = Puzzle(size, board)
    else:
        game = Puzzle(size)
        game.shuffle()

    # Проверка решаемости
    if not game.is_solvable():
        print("Эта комбинация нерешаема. Перемешиваем заново...")
        game = Puzzle(size)
        game.shuffle()

    # Цикл игры
    def clear_screen():
        os.system('clear' if os.name == 'posix' else 'cls')

    while not game.is_solved():
        clear_screen()
        print(colorize("ПЯТНАШКИ", 'bold'))
        print(colorize(f"Размер: {size}x{size}", 'blue'))
        print(game.render())
        elapsed = int(time.time() - game.start_time) if game.start_time else 0
        print(colorize(f"Ходы: {game.moves}  Время: {elapsed} сек", 'yellow'))
        print(colorize("Управление: стрелки (WASD), R - перемешать, Q - выход", 'gray'))
        try:
            key = input("Введите ход: ").strip().lower()
        except KeyboardInterrupt:
            print("\nВыход.")
            sys.exit(0)

        if key == 'q':
            print("Выход.")
            sys.exit(0)
        elif key == 'r':
            game.shuffle()
            continue
        elif key in ('up', 'w', '↑'):
            moved = game.move(-1, 0)
        elif key in ('down', 's', '↓'):
            moved = game.move(1, 0)
        elif key in ('left', 'a', '←'):
            moved = game.move(0, -1)
        elif key in ('right', 'd', '→'):
            moved = game.move(0, 1)
        else:
            print("Неизвестная команда.")
            time.sleep(0.5)
            continue
        if not moved:
            print("Невозможный ход.")
            time.sleep(0.5)

    # Победа
    clear_screen()
    print(colorize("🎉 Поздравляем! Вы собрали головоломку!", 'green'))
    elapsed = int(time.time() - game.start_time) if game.start_time else 0
    print(colorize(f"Ходов: {game.moves}  Время: {elapsed} сек", 'yellow'))
    # Обновление рекорда
    if key in records:
        if game.moves < records[key]['moves'] or (game.moves == records[key]['moves'] and elapsed < records[key]['time']):
            records[key] = {'moves': game.moves, 'time': elapsed}
            print(colorize("🏆 Новый рекорд!", 'green'))
        else:
            print(colorize(f"Текущий рекорд: {records[key]['moves']} ходов за {records[key]['time']} сек", 'blue'))
    else:
        records[key] = {'moves': game.moves, 'time': elapsed}
        print(colorize("🏆 Новый рекорд!", 'green'))
    save_records(records)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nВыход.")
        sys.exit(0)
