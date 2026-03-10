# Деплой через Helm (Apache Airflow)

## Шаблоны
- Секреты: `deploy/k8s/secrets.example.yaml`
- Values: `deploy/k8s/values.example.yaml`
- Job‑инициализатор переменных Airflow: `deploy/k8s/job-airflow-init.yaml`

## Шаги
1) Создать секреты
```
kubectl apply -n airflow -f deploy/k8s/secrets.example.yaml
```

2) Задать values для чарта Airflow
```
helm upgrade --install airflow apache-airflow/airflow \
  -n airflow --create-namespace \
  -f deploy/k8s/values.example.yaml
```

3) Применить job‑инициализатор (опционально)
```
kubectl apply -n airflow -f deploy/k8s/job-airflow-init.yaml
```
Job выполнит `airflow variables set ...` внутри контейнера Airflow, используя секреты и значения из env.

4) Синхронизация DAG
В values включен gitSync: укажите свой репозиторий (repo/branch). DAG и конфиги будут подтянуты автоматически.

## Примечания
- PVC `airflow-data-pvc` должен существовать или замените имя на ваше.
- Храните вебхуки/токены только в Secret.
- Для прод‑БД замените SQLite‑репозиторий на Postgres‑реализацию.

