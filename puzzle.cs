// puzzle.cs
using System;
using System.Collections.Generic;
using System.Linq;
using System.IO;
using System.Text;
using System.Threading;

class Puzzle
{
    static string Colorize(string text, string color)
    {
        string col = color switch
        {
            "red" => "\x1b[91m",
            "green" => "\x1b[92m",
            "yellow" => "\x1b[93m",
            "blue" => "\x1b[94m",
            "magenta" => "\x1b[95m",
            "cyan" => "\x1b[96m",
            "white" => "\x1b[97m",
            "gray" => "\x1b[90m",
            "bold" => "\x1b[1m",
            _ => "\x1b[0m"
        };
        return col + text + "\x1b[0m";
    }

    private int size;
    private int[,] board;
    private int emptyR, emptyC;
    public int Moves { get; private set; }
    public DateTime StartTime { get; private set; }

    public Puzzle(int size, int[,] state = null)
    {
        this.size = size;
        Moves = 0;
        StartTime = DateTime.MinValue;
        if (state != null)
        {
            board = (int[,])state.Clone();
            FindEmpty();
        }
        else
        {
            board = new int[size, size];
            for (int i = 0; i < size; i++)
                for (int j = 0; j < size; j++)
                    board[i, j] = i * size + j + 1;
            board[size - 1, size - 1] = 0;
            emptyR = size - 1;
            emptyC = size - 1;
        }
    }

    private void FindEmpty()
    {
        for (int i = 0; i < size; i++)
            for (int j = 0; j < size; j++)
                if (board[i, j] == 0) { emptyR = i; emptyC = j; return; }
    }

    public string Render()
    {
        var sb = new StringBuilder();
        sb.AppendLine(Colorize("┌" + new string('─', size * 4 - 1) + "┐", "gray"));
        for (int i = 0; i < size; i++)
        {
            sb.Append(Colorize("│", "gray"));
            for (int j = 0; j < size; j++)
            {
                int val = board[i, j];
                if (val == 0) sb.Append("   ");
                else
                {
                    string[] colors = { "red", "green", "yellow", "blue", "magenta", "cyan", "white", "gray" };
                    string col = colors[val % 7];
                    sb.Append(Colorize(val.ToString("D2") + " ", col));
                }
            }
            sb.AppendLine(Colorize("│", "gray"));
        }
        sb.Append(Colorize("└" + new string('─', size * 4 - 1) + "┘", "gray"));
        return sb.ToString();
    }

    public bool IsSolved()
    {
        int target = 1;
        for (int i = 0; i < size; i++)
            for (int j = 0; j < size; j++)
            {
                if (i == size - 1 && j == size - 1)
                {
                    if (board[i, j] != 0) return false;
                }
                else
                {
                    if (board[i, j] != target) return false;
                    target++;
                }
            }
        return true;
    }

    public bool IsSolvable()
    {
        List<int> flat = new List<int>();
        for (int i = 0; i < size; i++)
            for (int j = 0; j < size; j++)
                if (board[i, j] != 0) flat.Add(board[i, j]);
        int inversions = 0;
        for (int i = 0; i < flat.Count; i++)
            for (int j = i + 1; j < flat.Count; j++)
                if (flat[i] > flat[j]) inversions++;
        if (size % 2 == 1) return inversions % 2 == 0;
        else
        {
            if (emptyR % 2 == 0) return inversions % 2 == 1;
            else return inversions % 2 == 0;
        }
    }

    public void Shuffle(int moves = 100)
    {
        var rand = new Random();
        var dirs = new (int, int)[] { (0, 1), (0, -1), (1, 0), (-1, 0) };
        for (int i = 0; i < moves; i++)
        {
            int r = emptyR, c = emptyC;
            var shuffled = dirs.OrderBy(x => rand.Next()).ToArray();
            foreach (var d in shuffled)
            {
                int nr = r + d.Item1, nc = c + d.Item2;
                if (nr >= 0 && nr < size && nc >= 0 && nc < size)
                {
                    int tmp = board[r, c];
                    board[r, c] = board[nr, nc];
                    board[nr, nc] = tmp;
                    emptyR = nr;
                    emptyC = nc;
                    break;
                }
            }
        }
        Moves = 0;
        StartTime = DateTime.MinValue;
    }

    public bool Move(int dr, int dc)
    {
        int r = emptyR, c = emptyC;
        int nr = r + dr, nc = c + dc;
        if (nr >= 0 && nr < size && nc >= 0 && nc < size)
        {
            int tmp = board[r, c];
            board[r, c] = board[nr, nc];
            board[nr, nc] = tmp;
            emptyR = nr;
            emptyC = nc;
            Moves++;
            if (StartTime == DateTime.MinValue) StartTime = DateTime.Now;
            return true;
        }
        return false;
    }

    static void Main(string[] args)
    {
        int size = 4;
        if (args.Length > 0 && int.TryParse(args[0], out int v) && v >= 3 && v <= 5) size = v;
        var game = new Puzzle(size);
        game.Shuffle(100);
        while (!game.IsSolved())
        {
            Console.Clear();
            Console.WriteLine(Colorize("ПЯТНАШКИ", "bold"));
            Console.WriteLine(Colorize($"Размер: {size}x{size}", "blue"));
            Console.WriteLine(game.Render());
            int elapsed = game.StartTime == DateTime.MinValue ? 0 : (int)(DateTime.Now - game.StartTime).TotalSeconds;
            Console.WriteLine(Colorize($"Ходы: {game.Moves}  Время: {elapsed} сек", "yellow"));
            Console.WriteLine(Colorize("Управление: стрелки (WASD), R - перемешать, Q - выход", "gray"));
            var key = Console.ReadKey(true).Key;
            bool moved = false;
            switch (key)
            {
                case ConsoleKey.Q: Console.WriteLine("Выход."); return;
                case ConsoleKey.R: game.Shuffle(100); continue;
                case ConsoleKey.UpArrow:
                case ConsoleKey.W: moved = game.Move(-1, 0); break;
                case ConsoleKey.DownArrow:
                case ConsoleKey.S: moved = game.Move(1, 0); break;
                case ConsoleKey.LeftArrow:
                case ConsoleKey.A: moved = game.Move(0, -1); break;
                case ConsoleKey.RightArrow:
                case ConsoleKey.D: moved = game.Move(0, 1); break;
                default: continue;
            }
            if (!moved && (key == ConsoleKey.UpArrow || key == ConsoleKey.DownArrow || key == ConsoleKey.LeftArrow || key == ConsoleKey.RightArrow || key == ConsoleKey.W || key == ConsoleKey.S || key == ConsoleKey.A || key == ConsoleKey.D))
            {
                Console.WriteLine("Невозможный ход.");
                Thread.Sleep(500);
            }
        }
        Console.Clear();
        Console.WriteLine(Colorize("🎉 Поздравляем! Вы собрали головоломку!", "green"));
        int elapsedFinal = game.StartTime == DateTime.MinValue ? 0 : (int)(DateTime.Now - game.StartTime).TotalSeconds;
        Console.WriteLine(Colorize($"Ходов: {game.Moves}  Время: {elapsedFinal} сек", "yellow"));
    }
}
