# C4-модель (углубление): Хранилище и потоки данных

## Контекст
```mermaid
graph TD
  Service[Monitoring Service] -->|Пишет результаты| DB[(SQLite health_history.db)]
  Service -->|Пишет| Report[health_report.json]
  Service -->|Webhook| Slack[Slack]
```

## Контейнеры
```mermaid
graph TD
  subgraph Host
    CLI[CLI]
    App[MonitoringService]
    Repo[SQLiteResultsRepository]
    File[health_report.json]
  end
  App --> Repo
  App --> File
```

## Компоненты и схемы таблиц
```mermaid
classDiagram
class SQLiteResultsRepository {
  +save_results(checked_at, results)
}

class results {
  int id PK
  text check_time
  text name
  text url
  text method
  int expected_status
  int actual_status
  int response_time_ms
  text status
  text error
}
```

## Поток
1. MonitoringService собирает результаты проверок.
2. Сохраняет пачкой в таблицу results.
3. Пишет агрегированный health_report.json для операторов/CI.
4. Отправляет уведомление в Slack/консоль.

## Наблюдения
- SQLite выбран как легковесный журнал. При росте можно заменить на Postgres, реализовав другой ResultsRepository.
- Чтения из БД для принятия решений легко добавить, не затрагивая основной сервис.

