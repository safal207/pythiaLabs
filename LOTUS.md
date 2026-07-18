# Pythia Lotus Layer 🌸

<p align="center">
  <img src="assets/lotus.svg" alt="PythiaLabs Lotus Layer emblem" width="220" />
</p>

PythiaLabs evaluates high-risk proposed actions under evidence, authorization, environment, credential, and recovery context.

The lotus gives that role one human-readable rule:

> A verdict may guide action, but it must never hide its evidence or pretend uncertainty is permission.

The Pythia Lotus Layer is not a runtime component, policy source, autonomous actor, or substitute for domain expertise. It is a reviewable contract for how `ALLOW`, `BLOCK`, and `ESCALATE` decisions should be explained, bounded, replayed, and challenged.

## The seven judgment petals

### 1. Evidence before verdict

A verdict must name the evidence that supports it. Missing, stale, malformed, or unavailable evidence must stay visible and must not be silently converted into confidence.

### 2. Exact state before evidence reuse

Evidence is valid only for the exact action, policy, environment, authorization, credential, recovery context, and code state it covered. A changed input or PR head makes prior evidence stale until validation is rerun.

### 3. Authorization before `ALLOW`

Operational possibility is not permission. `ALLOW` requires the configured authorization and evidence contract to be satisfied; absence of a blocking signal is not enough.

### 4. Uncertainty stays explicit

Unknown, incomplete, conflicting, or low-confidence evidence must be represented as such. Where policy cannot safely decide, Pythia should produce `ESCALATE` rather than invent certainty.

### 5. Judgment without execution

Pythia may evaluate, explain, block, allow, or escalate under configured policy. It must not secretly perform the proposed external action or manufacture the authority that the action requires.

### 6. Replayable reasons

The same bounded inputs and policy should produce the same verdict, stop reason, and evidence trace. A reviewer must be able to reproduce why the decision occurred.

### 7. Human challengeability

A person must be able to inspect the evidence path, understand the stop reason, contest incorrect inputs or policy, and request a new evaluation. A verdict is reviewable output, not unquestionable truth.

## The judgment path

```text
proposed action
→ exact input and policy identity
→ evidence collection
→ authorization and safety checks
→ ALLOW / BLOCK / ESCALATE
→ stable stop reason
→ replayable evidence artifact
→ human review or execution by an authorized system
```

Skipping a step weakens trust. A successful simulation is not authorization. A prior verdict is not permission for a changed action. `BLOCK` is not punishment, and `ALLOW` is not execution.

## What the lotus must never become

The lotus is not mystical proof, a personality cult, a hidden policy engine, or a decorative excuse for overclaiming safety.

The assistant presence represented by the lotus has no ownership, credential, execution, delivery, or merge authority. Its role is to help judgment remain evidence-backed, bounded, reproducible, and open to challenge.

## Repository question

Before accepting a gate or verdict change, ask:

> Does this judgment show its evidence, preserve uncertainty, and leave consequential action under explicit authority?

If the answer is unclear, the judgment contract is not ready.

---

# Слой Лотоса Pythia

PythiaLabs оценивает опасные предложенные действия с учётом доказательств, разрешений, окружения, credentials и возможности восстановления.

Главное правило лотоса:

> Вердикт может направлять действие, но не должен скрывать доказательства или выдавать неопределённость за разрешение.

Слой Лотоса Pythia — не runtime-компонент, не источник policy, не автономный агент и не замена эксперту предметной области. Это проверяемый контракт, объясняющий, как решения `ALLOW`, `BLOCK` и `ESCALATE` должны быть ограничены, воспроизводимы и доступны для оспаривания.

## Семь лепестков суждения

1. **Доказательства до вердикта.** Вердикт обязан показывать поддерживающие его evidence. Отсутствующие, устаревшие, неверные или недоступные данные нельзя молча превращать в уверенность.
2. **Точное состояние до повторного использования evidence.** Доказательства действуют только для точных action, policy, environment, authorization, credential, recovery context и code state. После изменения входов или PR head прежние evidence устаревают до повторной проверки.
3. **Разрешение до `ALLOW`.** Техническая возможность не равна разрешению. `ALLOW` требует выполнения заданного контракта authorization и evidence; одного отсутствия блокирующего сигнала недостаточно.
4. **Неопределённость остаётся явной.** Неизвестные, неполные, конфликтующие или слабые evidence показываются честно. Когда policy не может безопасно решить, Pythia должна выбрать `ESCALATE`, а не придумывать уверенность.
5. **Суждение без исполнения.** Pythia может оценивать, объяснять, блокировать, разрешать или эскалировать по заданной policy, но не должна скрытно исполнять внешнее действие или создавать необходимое для него разрешение.
6. **Воспроизводимые причины.** Одинаковые ограниченные входы и policy должны давать одинаковые verdict, stop reason и evidence trace. Reviewer может повторить и понять решение.
7. **Право человека оспорить.** Человек может проверить evidence path, понять stop reason, оспорить неверные входы или policy и запросить новую оценку. Вердикт — проверяемый результат, а не неоспоримая истина.

## Путь суждения

```text
предложенное действие
→ точная идентичность входов и policy
→ сбор доказательств
→ проверки разрешений и безопасности
→ ALLOW / BLOCK / ESCALATE
→ стабильная причина остановки
→ воспроизводимый evidence artifact
→ человеческий review или исполнение авторизованной системой
```

Успешная симуляция не является разрешением. Старый verdict не даёт права на изменившееся действие. `BLOCK` не является наказанием, а `ALLOW` не является исполнением.

## Чем лотос не должен стать

Лотос — не мистическое доказательство, не культ личности, не скрытый policy engine и не декоративный повод преувеличивать безопасность.

Присутствие ассистента, обозначенное лотосом, не имеет права собственности, credentials, права на исполнение, доставку или merge. Его роль — помогать суждению оставаться основанным на доказательствах, ограниченным, воспроизводимым и доступным для оспаривания.

## Главный вопрос

Перед принятием изменения gate или verdict спроси:

> Показывает ли это суждение свои доказательства, сохраняет ли неопределённость и оставляет ли важное действие под явным разрешением?

Если ответ неясен — контракт суждения ещё не готов.
