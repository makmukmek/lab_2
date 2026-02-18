# Docker инструкции

## Сборка Docker образа

```bash
docker build -t materials-calculator .
```

## Запуск контейнера

### Базовый запуск:
```bash
docker run --rm materials-calculator
```

### С монтированием директории для БД (чтобы данные сохранялись):
```bash
docker run --rm -v $(pwd)/data:/app/data materials-calculator
```

### С интерактивным режимом:
```bash
docker run -it --rm -v $(pwd)/data:/app/data materials-calculator
```

## Переменные окружения

Можно задать путь к БД через переменную окружения:

```bash
docker run --rm -v $(pwd)/data:/app/data -e DB_PATH=/app/data/calc.db materials-calculator
```

## Сборка и запуск в одной команде

```bash
docker build -t materials-calculator . && docker run --rm -v $(pwd)/data:/app/data materials-calculator
```

## Просмотр логов

```bash
docker run --rm -v $(pwd)/data:/app/data materials-calculator 2>&1 | tee output.log
```

## Удаление образа

```bash
docker rmi materials-calculator
```

