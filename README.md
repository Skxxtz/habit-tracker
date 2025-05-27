# Habit Tracker

A lightweight, terminal-based habit tracking application build with Python. It
allows users to keep track of different habit types, including daily, weekly,
and monthly habits. The app focuses on fast navigation with Vim-like key binds.
<div>
    <picture>
        <img alt="application screenshot linux" height="250" src="assets/sceenshot.png">
    </picture>
</div>

## 🚀 Getting Started

### Dependencies

- [Python](https://docs.python.org/3/using/index.html)

### Installation

1. Clone the directory

```bash
git clone https://github.com/Skxxtz/habit-tracker.git
```

## 🎛️ Usage

1. Navigate to the habit-tracker directory

```bash
cd /path/to/habit-tracker
```

2. Use python to run `main.py`

```bash
python main.py
```

🎉 You've now successfully started the app.

### Binds

There are several key binds used to navigate the habit tracker.<br>

**Navigation:**

| Bind | Function |
| -------------- | --------------- |
| `j` | Navigate down |
| `↓` | Navigate down |
| `k` | Navigate up |
| `↑` | Navigate up |
| `q` | Quit |
| `ctrl + c` | Quit |
| `ctrl + l` | Home |
| `h` | Show help |

**Habit Management:**

| Bind | Function |
| -------------- | --------------- |
| `c` | Complete habit |
| `r` | Remove habit |
| `o` | Add habit |
| `f` | Filter habits |
| `s` | Sort habits |
| `I` | Show app-wide statistics |

## 🧪 Tests

To run unit tests, the following command should be run:

```bash
python -m unittest discover tests/
```
