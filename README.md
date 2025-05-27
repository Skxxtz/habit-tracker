# Planing

## Componentes

### Classes

#### Habit

Fields:

- longest streak: u32
- current streak: u32
- interval: String (either month or day)
- start: date (if start.[interval] != now.[interval] => update)
- history (list of bool?)
- completed: bool

#### User

Fields:

- longest streak: Habit
- longest streak habit - type habit

### Workflows

#### Saving

- Using json for habits into habits.json
- Using json for user into user.json

#### Management

- Add habit
- Remove habit
- Edit habit

#### Analytics

-
