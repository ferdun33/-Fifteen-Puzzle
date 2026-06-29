#!/usr/bin/env ruby
# puzzle.rb
# encoding: UTF-8

require 'io/console'
require 'time'
require 'json'
require 'fileutils'

COLORS = {
  reset: "\e[0m",
  red: "\e[91m",
  green: "\e[92m",
  yellow: "\e[93m",
  blue: "\e[94m",
  magenta: "\e[95m",
  cyan: "\e[96m",
  white: "\e[97m",
  gray: "\e[90m",
  bold: "\e[1m"
}

def colorize(text, color)
  "#{COLORS[color]}#{text}#{COLORS[:reset]}"
end

class Puzzle
  attr_reader :size, :moves, :start_time, :board

  def initialize(size, state = nil)
    @size = size
    @moves = 0
    @start_time = nil
    if state
      @board = state.map(&:dup)
      find_empty
    else
      @board = (0...size).map do |i|
        (0...size).map { |j| i*size + j + 1 }
      end
      @board[size-1][size-1] = 0
      @empty_r, @empty_c = size-1, size-1
    end
  end

  def find_empty
    @board.each_with_index do |row, i|
      row.each_with_index do |val, j|
        if val == 0
          @empty_r, @empty_c = i, j
          return
        end
      end
    end
  end

  def render
    lines = []
    lines << colorize('┌' + '─' * (@size * 4 - 1) + '┐', :gray)
    @size.times do |i|
      line = colorize('│', :gray)
      @size.times do |j|
        val = @board[i][j]
        if val == 0
          line += '   '
        else
          colors = [:red, :green, :yellow, :blue, :magenta, :cyan, :white, :gray]
          col = colors[val % 7]
          line += colorize("%2d " % val, col)
        end
      end
      line += colorize('│', :gray)
      lines << line
    end
    lines << colorize('└' + '─' * (@size * 4 - 1) + '┘', :gray)
    lines.join("\n")
  end

  def solved?
    target = 1
    @size.times do |i|
      @size.times do |j|
        if i == @size-1 && j == @size-1
          return false if @board[i][j] != 0
        else
          return false if @board[i][j] != target
          target += 1
        end
      end
    end
    true
  end

  def solvable?
    flat = []
    @size.times do |i|
      @size.times do |j|
        flat << @board[i][j] if @board[i][j] != 0
      end
    end
    inversions = 0
    (0...flat.size).each do |i|
      (i+1...flat.size).each do |j|
        inversions += 1 if flat[i] > flat[j]
      end
    end
    if @size % 2 == 1
      inversions.even?
    else
      if @empty_r % 2 == 0
        inversions.odd?
      else
        inversions.even?
      end
    end
  end

  def shuffle(moves = 100)
    dirs = [[0,1],[0,-1],[1,0],[-1,0]]
    moves.times do
      r, c = @empty_r, @empty_c
      dirs.shuffle.each do |dr, dc|
        nr, nc = r + dr, c + dc
        if nr >= 0 && nr < @size && nc >= 0 && nc < @size
          @board[r][c], @board[nr][nc] = @board[nr][nc], @board[r][c]
          @empty_r, @empty_c = nr, nc
          break
        end
      end
    end
    @moves = 0
    @start_time = nil
  end

  def move(dr, dc)
    r, c = @empty_r, @empty_c
    nr, nc = r + dr, c + dc
    if nr >= 0 && nr < @size && nc >= 0 && nc < @size
      @board[r][c], @board[nr][nc] = @board[nr][nc], @board[r][c]
      @empty_r, @empty_c = nr, nc
      @moves += 1
      @start_time ||= Time.now
      true
    else
      false
    end
  end
end

def clear_screen
  system('clear') || system('cls')
end

def main
  size = ARGV[0] ? ARGV[0].to_i : 4
  size = 4 if size < 3 || size > 5
  game = Puzzle.new(size)
  game.shuffle(100)

  loop do
    break if game.solved?
    clear_screen
    puts colorize("ПЯТНАШКИ", :bold)
    puts colorize("Размер: #{size}x#{size}", :blue)
    puts game.render
    elapsed = game.start_time ? (Time.now - game.start_time).to_i : 0
    puts colorize("Ходы: #{game.moves}  Время: #{elapsed} сек", :yellow)
    puts colorize("Управление: стрелки (WASD), R - перемешать, Q - выход", :gray)
    print "Введите ход: "
    input = STDIN.gets.chomp.downcase
    case input
    when 'q'
      puts "Выход."
      exit
    when 'r'
      game.shuffle(100)
      next
    when 'w'
      moved = game.move(-1, 0)
    when 's'
      moved = game.move(1, 0)
    when 'a'
      moved = game.move(0, -1)
    when 'd'
      moved = game.move(0, 1)
    else
      puts "Неизвестная команда."
      sleep 0.5
      next
    end
    unless moved
      puts "Невозможный ход."
      sleep 0.5
    end
  end

  clear_screen
  puts colorize("🎉 Поздравляем! Вы собрали головоломку!", :green)
  elapsed = game.start_time ? (Time.now - game.start_time).to_i : 0
  puts colorize("Ходов: #{game.moves}  Время: #{elapsed} сек", :yellow)
end

main if __FILE__ == $0
