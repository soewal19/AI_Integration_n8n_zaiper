# Автоматическая публикация в GitHub

Скрипты создают репозиторий через API и делают первый push, не раскрывая токен в командной строке.

## Подготовка
- Создайте Personal Access Token (scopes: `repo`) и экспортируйте как переменную окружения `GITHUB_TOKEN`.

## Bash
```
export GITHUB_TOKEN=ghp_xxx...
./scripts/github_init.sh <repo-name> [owner] [private:true|false]
```
- Если `owner` пустой — репозиторий создастся под вашим пользователем.

## PowerShell
```
$env:GITHUB_TOKEN="ghp_xxx..."
./scripts/github_init.ps1 -RepoName <repo-name> [-Owner <org-or-user>] [-Private]
```

## PowerShell (быстрый вариант — копировать и вставить)
```
$env:GITHUB_TOKEN="ghp_xxx..."
./scripts/github_init.ps1 -RepoName <repo-name> [-Owner <org-or-user>] [-Private]
```

## Примечания
- Скрипты устанавливают `origin` и пушат ветку `main`.
- Не храните токен в файлах. Используйте только переменные окружения/секреты.
