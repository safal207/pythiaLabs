# API v1: Controlled String Refinement

Дата: 2026-04-24

## Узкий use-case v1

`liminal-pythia` v1 фокусируется на одном сценарии:

> **Controlled string refinement**: итеративно улучшать `source` к `target` с прозрачным trace шагов и причиной остановки.

## Контракт запроса

Функция: `Pythia.refine_v1/1`

```elixir
%{
  source: String.t(),
  target: String.t(),
  options: [
    max_steps: pos_integer(),
    threshold: number(),
    no_improve_limit: pos_integer(),
    trace_id: integer()
  ]
}
```

Поля:
- `source` — исходная строка.
- `target` — целевая строка.
- `options` — опционально, дефолты берутся из `Planner.new/3`.

## Контракт ответа

Успех:

```elixir
{:ok,
 %{
   version: "v1",
   source: String.t(),
   target: String.t(),
   steps: non_neg_integer(),
   stop_reason: :threshold | :max_steps | :no_improve_limit,
   best: %{candidate: String.t(), score: non_neg_integer()},
   trace: list(map())
 }}
```

Ошибка валидации:

```elixir
{:error, :invalid_request}
```

## Пример

```elixir
iex> Pythia.refine_v1(%{source: "kitten", target: "sitting", options: [max_steps: 30]})
{:ok,
 %{
   version: "v1",
   source: "kitten",
   target: "sitting",
   steps: 7,
   stop_reason: :threshold,
   best: %{candidate: "sitting", score: 0},
   trace: [...]
 }}
```

## SLO-каркас для пилота

- `success_rate >= 99%` на валидных запросах.
- `p95 latency` для длины строк <= 128 символов: целевой порог определяется в staging baseline.
- Наличие `trace_id` для корреляции telemetry/logs.
