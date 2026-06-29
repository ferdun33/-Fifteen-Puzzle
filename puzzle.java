// puzzle.java
import java.io.*;
import java.util.*;

public class puzzle {
    private static final String RESET = "\u001B[0m";
    private static final String RED = "\u001B[91m";
    private static final String GREEN = "\u001B[92m";
    private static final String YELLOW = "\u001B[93m";
    private static final String BLUE = "\u001B[94m";
    private static final String MAGENTA = "\u001B[95m";
    private static final String CYAN = "\u001B[96m";
    private static final String WHITE = "\u001B[97m";
    private static final String GRAY = "\u001B[90m";
    private static final String BOLD = "\u001B[1m";

    private static String colorize(String text, String color) {
        return color + text + RESET;
    }

    static class PuzzleGame {
        int size;
        int[][] board;
        int emptyR, emptyC;
        int moves;
        long startTime;

        PuzzleGame(int size, int[][] state) {
            this.size = size;
            moves = 0;
            startTime = 0;
            if (state != null) {
                board = new int[size][size];
                for (int i = 0; i < size; i++)
                    System.arraycopy(state[i], 0, board[i], 0, size);
                findEmpty();
            } else {
                board = new int[size][size];
                for (int i = 0; i < size; i++)
                    for (int j = 0; j < size; j++)
                        board[i][j] = i * size + j + 1;
                board[size-1][size-1] = 0;
                emptyR = size-1;
                emptyC = size-1;
            }
        }

        void findEmpty() {
            for (int i = 0; i < size; i++)
                for (int j = 0; j < size; j++)
                    if (board[i][j] == 0) { emptyR = i; emptyC = j; return; }
        }

        String render() {
            StringBuilder sb = new StringBuilder();
            sb.append(colorize("┌" + "─".repeat(size * 4 - 1) + "┐", GRAY)).append("\n");
            for (int i = 0; i < size; i++) {
                sb.append(colorize("│", GRAY));
                for (int j = 0; j < size; j++) {
                    int val = board[i][j];
                    if (val == 0) sb.append("   ");
                    else {
                        String[] colors = {RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, GRAY};
                        String col = colors[val % 7];
                        sb.append(colorize(String.format("%2d ", val), col));
                    }
                }
                sb.append(colorize("│", GRAY)).append("\n");
            }
            sb.append(colorize("└" + "─".repeat(size * 4 - 1) + "┘", GRAY));
            return sb.toString();
        }

        boolean isSolved() {
            int target = 1;
            for (int i = 0; i < size; i++) {
                for (int j = 0; j < size; j++) {
                    if (i == size-1 && j == size-1) {
                        if (board[i][j] != 0) return false;
                    } else {
                        if (board[i][j] != target) return false;
                        target++;
                    }
                }
            }
            return true;
        }

        boolean isSolvable() {
            List<Integer> flat = new ArrayList<>();
            for (int i = 0; i < size; i++)
                for (int j = 0; j < size; j++)
                    if (board[i][j] != 0) flat.add(board[i][j]);
            int inversions = 0;
            for (int i = 0; i < flat.size(); i++)
                for (int j = i+1; j < flat.size(); j++)
                    if (flat.get(i) > flat.get(j)) inversions++;
            if (size % 2 == 1) return inversions % 2 == 0;
            else {
                if (emptyR % 2 == 0) return inversions % 2 == 1;
                else return inversions % 2 == 0;
            }
        }

        void shuffle(int moves) {
            Random rand = new Random();
            int[][] dirs = {{0,1},{0,-1},{1,0},{-1,0}};
            for (int i = 0; i < moves; i++) {
                int r = emptyR, c = emptyC;
                List<int[]> list = Arrays.asList(dirs);
                Collections.shuffle(list);
                for (int[] d : list) {
                    int nr = r + d[0], nc = c + d[1];
                    if (nr >= 0 && nr < size && nc >= 0 && nc < size) {
                        int tmp = board[r][c];
                        board[r][c] = board[nr][nc];
                        board[nr][nc] = tmp;
                        emptyR = nr;
                        emptyC = nc;
                        break;
                    }
                }
            }
            this.moves = 0;
            startTime = 0;
        }

        boolean move(int dr, int dc) {
            int r = emptyR, c = emptyC;
            int nr = r + dr, nc = c + dc;
            if (nr >= 0 && nr < size && nc >= 0 && nc < size) {
                int tmp = board[r][c];
                board[r][c] = board[nr][nc];
                board[nr][nc] = tmp;
                emptyR = nr;
                emptyC = nc;
                moves++;
                if (startTime == 0) startTime = System.currentTimeMillis();
                return true;
            }
            return false;
        }
    }

    public static void main(String[] args) throws IOException {
        int size = 4;
        if (args.length > 0) {
            try {
                int v = Integer.parseInt(args[0]);
                if (v >= 3 && v <= 5) size = v;
            } catch (NumberFormatException e) {}
        }
        PuzzleGame game = new PuzzleGame(size, null);
        game.shuffle(100);
        BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));
        while (!game.isSolved()) {
            System.out.print("\033[H\033[2J");
            System.out.flush();
            System.out.println(colorize("ПЯТНАШКИ", BOLD));
            System.out.println(colorize("Размер: " + size + "x" + size, BLUE));
            System.out.println(game.render());
            long elapsed = game.startTime == 0 ? 0 : (System.currentTimeMillis() - game.startTime) / 1000;
            System.out.println(colorize("Ходы: " + game.moves + "  Время: " + elapsed + " сек", YELLOW));
            System.out.println(colorize("Управление: стрелки (WASD), R - перемешать, Q - выход", GRAY));
            System.out.print("Введите ход: ");
            String input = reader.readLine().trim().toLowerCase();
            boolean moved = false;
            switch (input) {
                case "q": System.out.println("Выход."); return;
                case "r": game.shuffle(100); continue;
                case "w": moved = game.move(-1, 0); break;
                case "s": moved = game.move(1, 0); break;
                case "a": moved = game.move(0, -1); break;
                case "d": moved = game.move(0, 1); break;
                default: System.out.println("Неизвестная команда."); Thread.sleep(500); continue;
            }
            if (!moved && (input.equals("w") || input.equals("s") || input.equals("a") || input.equals("d"))) {
                System.out.println("Невозможный ход.");
                Thread.sleep(500);
            }
        }
        System.out.print("\033[H\033[2J");
        System.out.flush();
        System.out.println(colorize("🎉 Поздравляем! Вы собрали головоломку!", GREEN));
        long elapsedFinal = game.startTime == 0 ? 0 : (System.currentTimeMillis() - game.startTime) / 1000;
        System.out.println(colorize("Ходов: " + game.moves + "  Время: " + elapsedFinal + " сек", YELLOW));
    }
}
