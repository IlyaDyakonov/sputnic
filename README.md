## Тестовое задание на позицию Fullstack разработчика (Python + React)

**Вводные:**
1. Здесь представлен MVP проект файлообменника. Он позволяет загружать файлы, проверяет их на подозрительный контент и отправляет алерты;
2. Репозиторий содержит в себе бэкенд и фронтенд части;
3. В обоих частях присутствуют баги, неоптимизированный код, неудачные архитектурные решения.

**Задачи:**
1. Проведите рефакторинг бэкенда, не ломая бизнес-логики: предложите свое видение архитектуры и реализуйте его;
2. (Дополнительно) На бэкенде есть возможность неочевидной оптимизации - выполните ее;
3. (Дополнительно) Разбейте логику фронтенда на слои;

**Запуск:**
1. ```docker compose -f docker-compose.dev.yml up```
2. ```docker exec -it backend alembic upgrade head```


**Открыть фронт:** ```http://localhost:3000/test``` 

**Открыть бэк:** ```http://localhost:8000/docs```


**Что подправил:**
1. Исправил падение сборки фронтенда в Docker: подправил `COPY --from=builder /app/.env.production ./.env.production`, который валился, если файла нет.
2. Настроил автоприменение миграций: в `docker-compose.dev.yml` backend сначала выполняет `alembic upgrade head`, потом запускает `uvicorn`.
3. Для frontend убрал API-адреса: теперь используется `NEXT_PUBLIC_API_BASE_URL` (с fallback на `http://localhost:8000`).
4. Добавил пример переменных окружения для production: `frontend/.env.production.example`.
5. Установил типы для React в frontend: @types/react и @types/react-dom.
6. Сделал первый этап рефакторинга backend без изменения бизнес-логики: вынес `config`, DB session, local storage, repositories, celery app/workers, доменные threat-правила и use-cases. `src/service.py` и `src/tasks.py` специально оставил как backward-compatible фасады, чтобы не ломать текущие импорты, entrypoint воркера и API-контракт.
   Почему это лучше: код стал предсказуемее по зонам ответственности - бизнес-правила лежат отдельно от инфраструктуры, а сценарии работы (use-cases) отдельно от роутов и SQL-деталей. Важное решение здесь - не переписывать всё сразу, а перейти на новую структуру через совместимые фасады. За счет этого можно развивать проект по шагам, не рискуя стабильностью, и проще покрывать изменения тестами.
7. Сделал оптимизацию на уровне БД: добавил индексы `ix_files_created_at`, `ix_alerts_created_at`, `ix_alerts_file_id` (и в SQLAlchemy-моделях, и в отдельной Alembic-миграции). Это ускоряет основные списочные запросы (`/files`, `/alerts`) и будущие выборки по `file_id` при росте данных, уменьшая full scan и сортировки на больших таблицах.
8. Сделал рефакторинг frontend: `page.tsx` оставил контейнером (state + orchestration), а базовые элементы вынес в отдельные слои - UI-компоненты (`PageHeader`, `FilesTable`, `AlertsTable`, `UploadFileModal`), API-слой (`src/lib/api.ts`), утилиты форматирования/статусов (`src/lib/format.ts`, `src/lib/status.ts`) и типы (`src/types`). Такой код компактнее и заметно проще поддерживать.


**Карта проекта:**
```
├─ README.md
├─ docker-compose.dev.yml
├─ .env.dev
├─ backend/
│  ├─ Dockerfile
│  ├─ pyproject.toml
│  ├─ alembic.ini
│  ├─ migrations/
│  │  ├─ env.py
│  │  └─ versions/
│  │     ├─ 0d6439d2e79f_init.py
│  │     └─ 1d8f2a7b3c4e_add_query_indexes.py
│  └─ src/
│     ├─ app.py                        # FastAPI entrypoint
│     ├─ config.py                     # настройки
│     ├─ models.py / schemas.py        # ORM + API схемы
│     ├─ service.py                    # backward-compatible facade
│     ├─ tasks.py                      # celery facade/entrypoint
│     ├─ api/routes/
│     │  ├─ files.py
│     │  └─ alerts.py
│     ├─ application/use_cases/
│     │  ├─ files.py
│     │  └─ scan_pipeline.py
│     ├─ domain/services/
│     │  └─ threat_rules.py
│     └─ infrastructure/
│        ├─ db/session.py
│        ├─ repositories/
│        │  ├─ file_repo.py
│        │  └─ alert_repo.py
│        ├─ storage/local_storage.py
│        └─ tasks/
│           ├─ celery_app.py
│           └─ workers.py
└─ frontend/
   └─ src/
      ├─ app/
      │  ├─ layout.tsx
      │  └─ page.tsx                   # page-container
      ├─ components/
      │  ├─ page-header.tsx
      │  ├─ upload-file-modal.tsx
      │  ├─ files-table.tsx
      │  └─ alerts-table.tsx
      ├─ lib/
      │  ├─ api.ts
      │  ├─ config.ts
      │  ├─ format.ts
      │  └─ status.ts
      └─ types/
         ├─ file.ts
         └─ alert.ts
```