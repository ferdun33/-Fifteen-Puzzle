// puzzle.js
#!/usr/bin/env node
'use strict';

const readline = require('readline');
const fs = require('fs');
const path = require('path');
const os = require('os');

const COLORS = {
    reset: '\x1b[0m',
    red: '\x1b[91m',
    green: '\x1b[92m',
    yellow: '\x1b[93m',
    blue: '\x1b[94m',
    magenta: '\x1b[95m',
    cyan: '\x1b[96m',
    white: '\x1b[97m',
    gray: '\x1b[90m',
    bold: '\x1b[1m'
};

function colorize(text, color) {
    return COLORS[color] + text + COLORS.reset;
}

class Puzzle {
    constructor(size, state = null) {
        this.size = size;
        if (state) {
            this.board = state.map(row => [...row]);
            this.findEmpty();
        } else {
            this.board = [];
            for (let i = 0; i < size; i++) {
                const row = [];
                for (let j = 0; j < size; j++) {
                    row.push(i * size + j + 1);
                }
                this.board.push(row);
            }
            this.board[size-1][size-1] = 0;
            this.emptyR = size-1;
            this.emptyC = size-1;
        }
        this.moves = 0;
        this.startTime = null;
    }

    findEmpty() {
        for (let i = 0; i < this.size; i++) {
            for (let j = 0; j < this.size; j++) {
                if (this.board[i][j] === 0) {
                    this.emptyR = i;
                    this.emptyC = j;
                    return;
                }
            }
        }
    }

    render() {
        const lines = [];
        lines.push(colorize('┌' + '─'.repeat(this.size * 4 - 1) + '┐', 'gray'));
        for (let i = 0; i < this.size; i++) {
            let line = colorize('│', 'gray');
            for (let j = 0; j < this.size; j++) {
                const val = this.board[i][j];
                if (val === 0) {
                    line += '   ';
                } else {
                    const colors = ['red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white', 'gray'];
                    const col = colors[val % 7];
                    line += colorize(String(val).padStart(2) + ' ', col);
                }
            }
            line += colorize('│', 'gray');
            lines.push(line);
        }
        lines.push(colorize('└' + '─'.repeat(this.size * 4 - 1) + '┘', 'gray'));
        return lines.join('\n');
    }

    isSolved() {
        let target = 1;
        for (let i = 0; i < this.size; i++) {
            for (let j = 0; j < this.size; j++) {
                if (i === this.size-1 && j === this.size-1) {
                    if (this.board[i][j] !== 0) return false;
                } else {
                    if (this.board[i][j] !== target) return false;
                    target++;
                }
            }
        }
        return true;
    }

    isSolvable() {
        const flat = [];
        for (let i = 0; i < this.size; i++) {
            for (let j = 0; j < this.size; j++) {
                if (this.board[i][j] !== 0) flat.push(this.board[i][j]);
            }
        }
        let inversions = 0;
        for (let i = 0; i < flat.length; i++) {
            for (let j = i+1; j < flat.length; j++) {
                if (flat[i] > flat[j]) inversions++;
            }
        }
        if (this.size % 2 === 1) {
            return inversions % 2 === 0;
        } else {
            if (this.emptyR % 2 === 0) {
                return inversions % 2 === 1;
            } else {
                return inversions % 2 === 0;
            }
        }
    }

    shuffle(moves = 100) {
        const dirs = [[0,1],[0,-1],[1,0],[-1,0]];
        for (let i = 0; i < moves; i++) {
            const r = this.emptyR, c = this.emptyC;
            const shuffled = dirs.sort(() => Math.random() - 0.5);
            for (const d of shuffled) {
                const nr = r + d[0], nc = c + d[1];
                if (nr >= 0 && nr < this.size && nc >= 0 && nc < this.size) {
                    [this.board[r][c], this.board[nr][nc]] = [this.board[nr][nc], this.board[r][c]];
                    this.emptyR = nr;
                    this.emptyC = nc;
                    break;
                }
            }
        }
        this.moves = 0;
        this.startTime = null;
    }

    move(dr, dc) {
        const r = this.emptyR, c = this.emptyC;
        const nr = r + dr, nc = c + dc;
        if (nr >= 0 && nr < this.size && nc >= 0 && nc < this.size) {
            [this.board[r][c], this.board[nr][nc]] = [this.board[nr][nc], this.board[r][c]];
            this.emptyR = nr;
            this.emptyC = nc;
            this.moves++;
            if (!this.startTime) this.startTime = Date.now();
            return true;
        }
        return false;
    }
}

function clearScreen() {
    console.clear();
}

async function main() {
    const args = process.argv.slice(2);
    let size = 4;
    if (args.length > 0) {
        const v = parseInt(args[0]);
        if (!isNaN(v) && v >= 3 && v <= 5) size = v;
    }
    const game = new Puzzle(size);
    game.shuffle(100);

    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });

    const question = (query) => new Promise(resolve => rl.question(query, resolve));

    while (!game.isSolved()) {
        clearScreen();
        console.log(colorize('ПЯТНАШКИ', 'bold'));
        console.log(colorize(`Размер: ${size}x${size}`, 'blue'));
        console.log(game.render());
        const elapsed = game.startTime ? Math.floor((Date.now() - game.startTime) / 1000) : 0;
        console.log(colorize(`Ходы: ${game.moves}  Время: ${elapsed} сек`, 'yellow'));
        console.log(colorize('Управление: стрелки (WASD), R - перемешать, Q - выход', 'gray'));
        const input = await question('Введите ход: ');
        const cmd = input.trim().toLowerCase();
        if (cmd === 'q') {
            console.log('Выход.');
            rl.close();
            process.exit(0);
        } else if (cmd === 'r') {
            game.shuffle(100);
            continue;
        }
        let moved = false;
        if (['up','w'].includes(cmd)) moved = game.move(-1, 0);
        else if (['down','s'].includes(cmd)) moved = game.move(1, 0);
        else if (['left','a'].includes(cmd)) moved = game.move(0, -1);
        else if (['right','d'].includes(cmd)) moved = game.move(0, 1);
        else {
            console.log('Неизвестная команда.');
            await new Promise(resolve => setTimeout(resolve, 500));
            continue;
        }
        if (!moved) {
            console.log('Невозможный ход.');
            await new Promise(resolve => setTimeout(resolve, 500));
        }
    }
    clearScreen();
    console.log(colorize('🎉 Поздравляем! Вы собрали головоломку!', 'green'));
    const elapsed = game.startTime ? Math.floor((Date.now() - game.startTime) / 1000) : 0;
    console.log(colorize(`Ходов: ${game.moves}  Время: ${elapsed} сек`, 'yellow'));
    rl.close();
}

main().catch(console.error);
