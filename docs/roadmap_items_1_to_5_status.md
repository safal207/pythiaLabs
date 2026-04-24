# Статус реализации пунктов 1–5 (на 2026-04-24)

## Итог

Пункты **1–5 реализованы по коду и артефактам**. Остались только организационные/процессные подтверждения (доступ к Hex в окружении, подтверждение отсутствия P0 в backlog).

---

## Пункт 1 — Стабилизация ядра

**Сделано:**
- Исправлены edge-cases fallback Levenshtein для пустых строк.
- Удалён дублирующий compile task.
- Добавлены unit-тесты для Planner/Executor/KernelsFallback.

**Артефакты:**
- `lib/pythia/kernels_fallback.ex`
- `test/kernels_fallback_test.exs`
- `test/executor_test.exs`
- `test/planner_test.exs`

---

## Пункт 2 — Надёжность и безопасность worker

**Сделано:**
- Убраны panic-пути обработки входа в Rust worker.
- Введена валидация shape/значений/границ.
- Добавлены лимиты размеров и структурированные ошибки.
- Добавлены Rust unit-тесты.

**Артефакты:**
- `workers/solver_port/src/main.rs`

---

## Пункт 3 — Наблюдаемость

**Сделано:**
- Добавлены telemetry события planner step/stop.
- Добавлено логирование с `trace_id`.
- Добавлены тесты эмиссии telemetry.

**Артефакты:**
- `lib/pythia/planner.ex`
- `test/planner_test.exs`
- `mix.exs` (`:telemetry`)

---

## Пункт 4 — Продуктовая обвязка v1

**Сделано:**
- Добавлен узкий API-вход `Pythia.refine_v1/1`.
- Описан контракт v1 и пример в документации.
- Добавлены golden scenarios для валидации ожидаемого поведения.

**Артефакты:**
- `lib/pythia.ex`
- `docs/api_v1.md`
- `test/golden_refine_test.exs`

---

## Пункт 5 — Gate перед пилотом

**Сделано:**
- Добавлен checklist pre-pilot gate.
- CI обновлён: запуск `mix test` и `cargo test`.

**Артефакты:**
- `docs/pilot_readiness_checklist.md`
- `.github/workflows/ci.yml`

---

## Остаточные блокеры

1. Локальный запуск `mix test` в текущем контейнере блокируется отсутствием Hex/deps bootstrap.
2. Пункт "нет известных P0" должен быть подтверждён владельцем backlog/PM.
