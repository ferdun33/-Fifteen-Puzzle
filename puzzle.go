// puzzle.go
package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"math/rand"
	"os"
	"os/exec"
	"runtime"
	"strconv"
	"strings"
	"time"
)

const (
	reset  = "\033[0m"
	red    = "\033[91m"
	green  = "\033[92m"
	yellow = "\033[93m"
	blue   = "\033[94m"
	magenta= "\033[95m"
	cyan   = "\033[96m"
	white  = "\033[97m"
	gray   = "\033[90m"
	bold   = "\033[1m"
)

func colorize(text, color string) string {
	return color + text + reset
}

type Puzzle struct {
	size      int
	board     [][]int
	emptyR, emptyC int
	moves     int
	startTime time.Time
}

func NewPuzzle(size int, state [][]int) *Puzzle {
	p := &Puzzle{size: size, moves: 0}
	if state != nil {
		p.board = make([][]int, size)
		for i := 0; i < size; i++ {
			p.board[i] = make([]int, size)
			copy(p.board[i], state[i])
			for j := 0; j < size; j++ {
				if p.board[i][j] == 0 {
					p.emptyR, p.emptyC = i, j
				}
			}
		}
	} else {
		p.board = make([][]int, size)
		for i := 0; i < size; i++ {
			p.board[i] = make([]int, size)
			for j := 0; j < size; j++ {
				p.board[i][j] = i*size + j + 1
			}
		}
		p.board[size-1][size-1] = 0
		p.emptyR, p.emptyC = size-1, size-1
	}
	return p
}

func (p *Puzzle) render() string {
	var lines []string
	lines = append(lines, colorize("┌"+strings.Repeat("─", p.size*4-1)+"┐", gray))
	for i := 0; i < p.size; i++ {
		line := colorize("│", gray)
		for j := 0; j < p.size; j++ {
			val := p.board[i][j]
			if val == 0 {
				line += "   "
			} else {
				colors := []string{red, green, yellow, blue, magenta, cyan, white, gray}
				col := colors[val%7]
				line += colorize(fmt.Sprintf("%2d ", val), col)
			}
		}
		line += colorize("│", gray)
		lines = append(lines, line)
	}
	lines = append(lines, colorize("└"+strings.Repeat("─", p.size*4-1)+"┘", gray))
	return strings.Join(lines, "\n")
}

func (p *Puzzle) isSolved() bool {
	target := 1
	for i := 0; i < p.size; i++ {
		for j := 0; j < p.size; j++ {
			if i == p.size-1 && j == p.size-1 {
				if p.board[i][j] != 0 {
					return false
				}
			} else {
				if p.board[i][j] != target {
					return false
				}
				target++
			}
		}
	}
	return true
}

func (p *Puzzle) isSolvable() bool {
	flat := []int{}
	for i := 0; i < p.size; i++ {
		for j := 0; j < p.size; j++ {
			if p.board[i][j] != 0 {
				flat = append(flat, p.board[i][j])
			}
		}
	}
	inversions := 0
	for i := 0; i < len(flat); i++ {
		for j := i + 1; j < len(flat); j++ {
			if flat[i] > flat[j] {
				inversions++
			}
		}
	}
	if p.size%2 == 1 {
		return inversions%2 == 0
	} else {
		if p.emptyR%2 == 0 {
			return inversions%2 == 1
		} else {
			return inversions%2 == 0
		}
	}
}

func (p *Puzzle) shuffle(moves int) {
	dirs := [][2]int{{0, 1}, {0, -1}, {1, 0}, {-1, 0}}
	for i := 0; i < moves; i++ {
		r, c := p.emptyR, p.emptyC
		rand.Shuffle(len(dirs), func(i, j int) { dirs[i], dirs[j] = dirs[j], dirs[i] })
		for _, d := range dirs {
			nr, nc := r+d[0], c+d[1]
			if nr >= 0 && nr < p.size && nc >= 0 && nc < p.size {
				p.board[r][c], p.board[nr][nc] = p.board[nr][nc], p.board[r][c]
				p.emptyR, p.emptyC = nr, nc
				break
			}
		}
	}
	p.moves = 0
	p.startTime = time.Time{}
}

func (p *Puzzle) move(dr, dc int) bool {
	r, c := p.emptyR, p.emptyC
	nr, nc := r+dr, c+dc
	if nr >= 0 && nr < p.size && nc >= 0 && nc < p.size {
		p.board[r][c], p.board[nr][nc] = p.board[nr][nc], p.board[r][c]
		p.emptyR, p.emptyC = nr, nc
		p.moves++
		if p.startTime.IsZero() {
			p.startTime = time.Now()
		}
		return true
	}
	return false
}

func clearScreen() {
	cmd := exec.Command("clear")
	if runtime.GOOS == "windows" {
		cmd = exec.Command("cmd", "/c", "cls")
	}
	cmd.Stdout = os.Stdout
	cmd.Run()
}

func main() {
	rand.Seed(time.Now().UnixNano())
	size := 4
	if len(os.Args) > 1 {
		if v, err := strconv.Atoi(os.Args[1]); err == nil {
			size = v
			if size < 3 || size > 5 {
				fmt.Println("Размер должен быть от 3 до 5")
				os.Exit(1)
			}
		}
	}
	game := NewPuzzle(size, nil)
	game.shuffle(100)
	for !game.isSolved() {
		clearScreen()
		fmt.Println(colorize("ПЯТНАШКИ", bold))
		fmt.Println(colorize(fmt.Sprintf("Размер: %dx%d", size, size), blue))
		fmt.Println(game.render())
		elapsed := 0
		if !game.startTime.IsZero() {
			elapsed = int(time.Since(game.startTime).Seconds())
		}
		fmt.Println(colorize(fmt.Sprintf("Ходы: %d  Время: %d сек", game.moves, elapsed), yellow))
		fmt.Println(colorize("Управление: стрелки (WASD), R - перемешать, Q - выход", gray))
		reader := bufio.NewReader(os.Stdin)
		key, _ := reader.ReadString('\n')
		key = strings.TrimSpace(key)
		var moved bool
		switch key {
		case "q", "Q":
			fmt.Println("Выход.")
			return
		case "r", "R":
			game.shuffle(100)
			continue
		case "w", "W":
			moved = game.move(-1, 0)
		case "s", "S":
			moved = game.move(1, 0)
		case "a", "A":
			moved = game.move(0, -1)
		case "d", "D":
			moved = game.move(0, 1)
		default:
			fmt.Println("Неизвестная команда.")
			time.Sleep(500 * time.Millisecond)
			continue
		}
		if !moved && (key == "w" || key == "W" || key == "s" || key == "S" || key == "a" || key == "A" || key == "d" || key == "D") {
			fmt.Println("Невозможный ход.")
			time.Sleep(500 * time.Millisecond)
		}
	}
	clearScreen()
	fmt.Println(colorize("🎉 Поздравляем! Вы собрали головоломку!", green))
	elapsed := 0
	if !game.startTime.IsZero() {
		elapsed = int(time.Since(game.startTime).Seconds())
	}
	fmt.Println(colorize(fmt.Sprintf("Ходов: %d  Время: %d сек", game.moves, elapsed), yellow))
}
