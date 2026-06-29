// puzzle.cpp
#include <iostream>
#include <vector>
#include <string>
#include <random>
#include <chrono>
#include <thread>
#include <fstream>
#include <json/json.h>
#include <termios.h>
#include <unistd.h>
#include <fcntl.h>

using namespace std;

const string RESET = "\033[0m";
const string RED = "\033[91m";
const string GREEN = "\033[92m";
const string YELLOW = "\033[93m";
const string BLUE = "\033[94m";
const string MAGENTA = "\033[95m";
const string CYAN = "\033[96m";
const string WHITE = "\033[97m";
const string GRAY = "\033[90m";
const string BOLD = "\033[1m";

string colorize(const string& text, const string& color) {
    return color + text + RESET;
}

string getHomeDir() {
    const char* home = getenv("HOME");
    if (!home) home = getenv("USERPROFILE");
    return string(home);
}

string getRecordFile() {
    return getHomeDir() + "/.puzzle_records.json";
}

class Puzzle {
public:
    int size;
    vector<vector<int>> board;
    pair<int,int> empty;
    int moves;
    time_t startTime;

    Puzzle(int sz, const vector<vector<int>>& state = {}) : size(sz), moves(0), startTime(0) {
        if (!state.empty()) {
            board = state;
            for (int i = 0; i < size; ++i)
                for (int j = 0; j < size; ++j)
                    if (board[i][j] == 0) empty = {i, j};
        } else {
            board.resize(size, vector<int>(size));
            for (int i = 0; i < size; ++i)
                for (int j = 0; j < size; ++j)
                    board[i][j] = i*size + j + 1;
            board[size-1][size-1] = 0;
            empty = {size-1, size-1};
        }
    }

    string render() const {
        string result;
        result += colorize("┌" + string(size*4-1, '─') + "┐", GRAY) + "\n";
        for (int i = 0; i < size; ++i) {
            result += colorize("│", GRAY);
            for (int j = 0; j < size; ++j) {
                int val = board[i][j];
                if (val == 0) result += "   ";
                else {
                    vector<string> colors = {RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, GRAY};
                    string col = colors[val % 7];
                    result += colorize(to_string(val) + (val < 10 ? " " : ""), col);
                    if (val < 10) result += " ";
                }
            }
            result += colorize("│", GRAY) + "\n";
        }
        result += colorize("└" + string(size*4-1, '─') + "┘", GRAY);
        return result;
    }

    bool isSolved() const {
        int target = 1;
        for (int i = 0; i < size; ++i)
            for (int j = 0; j < size; ++j) {
                if (i == size-1 && j == size-1) {
                    if (board[i][j] != 0) return false;
                } else {
                    if (board[i][j] != target) return false;
                    target++;
                }
            }
        return true;
    }

    bool isSolvable() const {
        vector<int> flat;
        for (int i = 0; i < size; ++i)
            for (int j = 0; j < size; ++j)
                if (board[i][j] != 0) flat.push_back(board[i][j]);
        int inversions = 0;
        for (size_t i = 0; i < flat.size(); ++i)
            for (size_t j = i+1; j < flat.size(); ++j)
                if (flat[i] > flat[j]) inversions++;
        if (size % 2 == 1) return inversions % 2 == 0;
        else {
            int emptyRow = empty.first;
            if (emptyRow % 2 == 0) return inversions % 2 == 1;
            else return inversions % 2 == 0;
        }
    }

    void shuffle(int movesCount = 100) {
        random_device rd;
        mt19937 gen(rd());
        uniform_int_distribution<> dirDist(0, 3);
        vector<pair<int,int>> dirs = {{0,1},{0,-1},{1,0},{-1,0}};
        for (int i = 0; i < movesCount; ++i) {
            int r = empty.first, c = empty.second;
            int idx = dirDist(gen);
            for (int attempt = 0; attempt < 4; ++attempt) {
                int d = (idx + attempt) % 4;
                int nr = r + dirs[d].first;
                int nc = c + dirs[d].second;
                if (nr >= 0 && nr < size && nc >= 0 && nc < size) {
                    swap(board[r][c], board[nr][nc]);
                    empty = {nr, nc};
                    break;
                }
            }
        }
        moves = 0;
        startTime = 0;
    }

    bool move(int dr, int dc) {
        int r = empty.first, c = empty.second;
        int nr = r + dr, nc = c + dc;
        if (nr >= 0 && nr < size && nc >= 0 && nc < size) {
            swap(board[r][c], board[nr][nc]);
            empty = {nr, nc};
            moves++;
            if (startTime == 0) startTime = time(nullptr);
            return true;
        }
        return false;
    }
};

char getch() {
    struct termios oldt, newt;
    char ch;
    tcgetattr(STDIN_FILENO, &oldt);
    newt = oldt;
    newt.c_lflag &= ~(ICANON | ECHO);
    tcsetattr(STDIN_FILENO, TCSANOW, &newt);
    ch = getchar();
    tcsetattr(STDIN_FILENO, TCSANOW, &oldt);
    return ch;
}

void clearScreen() {
    cout << "\033[2J\033[1;1H";
}

int main(int argc, char* argv[]) {
    int size = 4;
    if (argc > 1) {
        size = stoi(argv[1]);
        if (size < 3 || size > 5) {
            cout << "Размер должен быть от 3 до 5" << endl;
            return 1;
        }
    }
    Puzzle game(size);
    game.shuffle();
    // Проверка решаемости (уже гарантировано shuffle, но на всякий случай)
    while (!game.isSolvable()) game.shuffle();

    while (!game.isSolved()) {
        clearScreen();
        cout << colorize("ПЯТНАШКИ", BOLD) << endl;
        cout << colorize("Размер: " + to_string(size) + "x" + to_string(size), BLUE) << endl;
        cout << game.render() << endl;
        int elapsed = (game.startTime == 0) ? 0 : (int)(time(nullptr) - game.startTime);
        cout << colorize("Ходы: " + to_string(game.moves) + "  Время: " + to_string(elapsed) + " сек", YELLOW) << endl;
        cout << colorize("Управление: стрелки (WASD), R - перемешать, Q - выход", GRAY) << endl;
        char key = getch();
        bool moved = false;
        switch (key) {
            case 'q': case 'Q': cout << "Выход." << endl; return 0;
            case 'r': case 'R': game.shuffle(); continue;
            case 'w': case 'W': moved = game.move(-1, 0); break;
            case 's': case 'S': moved = game.move(1, 0); break;
            case 'a': case 'A': moved = game.move(0, -1); break;
            case 'd': case 'D': moved = game.move(0, 1); break;
            default: break;
        }
        if (!moved && (key == 'w' || key == 'W' || key == 's' || key == 'S' || key == 'a' || key == 'A' || key == 'd' || key == 'D'))
            cout << "Невозможный ход." << endl;
    }

    clearScreen();
    cout << colorize("🎉 Поздравляем! Вы собрали головоломку!", GREEN) << endl;
    int elapsed = (game.startTime == 0) ? 0 : (int)(time(nullptr) - game.startTime);
    cout << colorize("Ходов: " + to_string(game.moves) + "  Время: " + to_string(elapsed) + " сек", YELLOW) << endl;
    // Рекорды
    string key = to_string(size) + "x" + to_string(size);
    // Для простоты пропустим сохранение рекорда в C++ (можно реализовать через jsoncpp)
    return 0;
}
