export const locales = {
  en: {
    htmlLang: "en",
    langLabel: "EN",
    meta: {
      title: "Pre-execution safety gate for AI agents — PythiaLabs",
      description:
        "PythiaLabs is the pre-execution safety gate for AI agents. Decides whether an agent's action should ALLOW, BLOCK, or ESCALATE — before it executes — with replayable evidence.",
    },
    nav: {
      problem: "Problem",
      idea: "Big idea",
      solution: "How it works",
      useCases: "Use cases",
      videos: "Videos",
      faq: "FAQ",
      contact: "Contact",
    },
    skipLink: "Skip to content",
    hero: {
      eyebrow: "Pre-execution safety layer · Open-source · Apache-2.0",
      headline: "Stop dangerous AI agent actions before they execute.",
      subtitle:
        "AI agents are moving from answers to actions. PythiaLabs decides whether those actions should execute.",
      body: "AI agents already modify code, run commands, touch infrastructure, and act in financial and governance workflows. PythiaLabs is a pre-execution safety layer that evaluates an action before the agent runs it.",
      tagline: "Not trust. Verification before execution.",
      starsAlt: "GitHub stars",
    },
    exampleDecision: {
      eyebrow: "Example decision",
      title: "An agent wants to move treasury funds. The gate stops first.",
      actionLabel: "Proposed action",
      action: "Transfer 25,000 USDC from treasury",
      decisionLabel: "Decision",
      decision: "ESCALATE",
      reasonLabel: "Reason",
      reason: "Missing quorum approval and stale policy state",
      evidenceLabel: "Evidence",
      evidence: "Replayable trace, check results, and tamper-checkable digest",
    },
    trustStrip: [
      "100% open-source",
      "Apache-2.0",
      "Deterministic — 0 LLM calls in the gate",
      "Self-hostable",
      "No telemetry",
    ],
    cta: {
      primary: "Watch the demo",
      secondary: "View GitHub repo",
      tertiary: "Join early access",
      pilot: "Apply as pilot partner",
      contact: "Contact",
    },
    videoBlock: {
      eyebrow: "Watch why this matters",
      title: "Should this AI agent action execute?",
      body: "When an AI agent gets the ability to act, a mistake is no longer a bad answer — it becomes a real action in the real world. PythiaLabs places a verifiable gate before execution: does the agent have the right to act, is there enough context, is the temporal/causal state valid, can the trace be replayed, and should this be allowed, blocked, or escalated to a human?",
      coreLabel: "Core message",
      core:
        "The future of agent safety is not after-the-fact debugging. It is pre-execution control.",
      fallback: "Watch on YouTube",
    },
    problem: {
      title: "The dangerous gap in agentic AI",
      intro: "AI agents can already:",
      items: [
        "modify production code",
        "run DevOps commands",
        "process banking and payment flows",
        "take workflow decisions",
        "act in Web3 treasury and governance",
        "execute via tools and APIs",
      ],
      punchline:
        "But most systems still verify outcomes after execution. That's like installing fire alarms after the building burned down.",
    },
    bigIdea: {
      eyebrow: "The big idea",
      title: "Before an agent acts, it must prove the action is allowed",
      lead: "PythiaLabs asks one critical question:",
      quote: "“Should this AI agent action execute?”",
      not: [
        "Not “does the answer look smart?”",
        "Not “is the model confident?”",
        "Not “does the reasoning sound right?”",
      ],
      but: "Does this action have the right to be executed, right now?",
    },
    solution: {
      title: "How PythiaLabs works",
      intro: "Four steps. Deterministic. Replayable.",
      steps: [
        {
          name: "Agent proposes an action",
          desc: "The AI agent proposes an action: change code, run a command, approve an operation, kick off a workflow.",
        },
        {
          name: "PythiaLabs checks the evidence",
          desc: "The gate evaluates context, permissions, risk, temporal state, and causal consistency.",
        },
        {
          name: "The action is decided before execution",
          desc: "The action gets one of: ALLOW · BLOCK · ESCALATE — and a replayable audit trace.",
        },
        {
          name: "Every decision leaves evidence",
          desc: "PythiaLabs emits a transparent trail: why the action was allowed, blocked, or escalated.",
        },
      ],
      checksTitle: "Checks",
      checks: [
        "authorization",
        "evidence freshness",
        "decision-time context",
        "permission boundaries",
        "credentials",
        "recovery assumptions",
        "action risk",
      ],
      returnsTitle: "Returns",
    },
    artifact: {
      title: "Inspectable decision artifacts",
      intro:
        "Every decision produces a JSON artifact: stable stop reasons, per-check results, a replayable trace ID, and a tamper-checkable digest. This is what reviewers and auditors actually read.",
    },
    valueStack: {
      title: "Stop dangerous agent actions before they happen",
      intro:
        "PythiaLabs helps teams build AI agents that can't just be trusted on their word. Instead, you get:",
      items: [
        "Deterministic safety gates — same input, same decision, every time",
        "Replayable traces with stable stop reasons",
        "Human-review workflow for escalations",
        "Audit evidence reviewers and auditors can read",
        "Apache-2.0 — fork it, run it on your infra, audit every line",
        "Zero vendor lock-in: no SaaS dependency, no telemetry, no phone-home",
      ],
      footer: "All of this · $0 · Open source",
    },
    comparison: {
      title: "Before vs. with PythiaLabs",
      withoutTitle: "Without an evidence gate",
      withoutItems: [
        "Agents act first, you investigate after — incidents are post-hoc",
        "Custom guards drift across teams and break invariants silently",
        "“Why was this allowed?” requires forensic log digging",
        "Reviewers get inconsistent, unreplayable evidence",
      ],
      withTitle: "With PythiaLabs",
      withItems: [
        "Decisions are evaluated before execution — no surprise actions",
        "One deterministic engine, one set of checks, applied everywhere",
        "Every decision has a stop reason, a trace, and a verifiable digest",
        "Reviewers get the same artifact every time, replay included",
      ],
    },
    useCases: {
      title: "Where this becomes critical",
      items: [
        {
          name: "DevOps / Infrastructure",
          desc: "Before an agent deletes a volume, restarts a service, or changes configuration, PythiaLabs verifies whether it has the right to do so.",
        },
        {
          name: "Banking / FinTech",
          desc: "Before approving a risky operation, the gate checks evidence, limits, context, and temporal validity.",
        },
        {
          name: "Web3 / DAO governance",
          desc: "Before a treasury action or governance operation, the agent must pass a safety gate.",
        },
        {
          name: "AI coding agents",
          desc: "Before merge, patch, or production change, the agent leaves a verifiable trace and passes pre-execution validation.",
        },
      ],
    },
    positioning: {
      eyebrow: "Positioning",
      title: "PythiaLabs is not another agent",
      negatives: [
        "Not a chatbot.",
        "Not another agent wrapper.",
        "Not “prompt engineering safety”.",
      ],
      claim: "PythiaLabs is the gate before the agent acts.",
      tagsLabel: "When the agent wants to execute, the gate decides:",
      tags: ["ALLOW", "BLOCK", "ESCALATE", "AUDIT"],
    },
    authority: {
      eyebrow: "Built for the next generation of agentic systems",
      title: "Autonomy without verifiable action permissions is not intelligence — it is risk",
      body: "The AI industry is moving fast toward autonomous agents. PythiaLabs is built around a simple idea:",
      pullQuote:
        "A powerful AI agent should not only reason. It should be constrained by verifiable action permissions.",
    },
    founderVideosBlock: {
      eyebrow: "From the founder",
      title: "Three short videos",
      cards: {
        longForm: {
          name: "Video 1 — The main thesis",
          headline: "Should this AI agent action execute?",
          desc: "AI agents are becoming actors, not just responders. PythiaLabs introduces a deterministic safety layer that evaluates whether an action should execute before it reaches the real world.",
          cta: "Watch full walkthrough",
        },
        short1: {
          name: "Short — the hook",
          headline: "Who decides whether the action is allowed?",
          desc: "AI agents are no longer just generating text. They are starting to take actions. PythiaLabs focuses on the question every serious AI system will need to answer.",
          cta: "Watch the short",
        },
        short2: {
          name: "Short — the new category",
          headline: "Pre-execution control",
          desc: "The next frontier of AI safety is pre-execution control. PythiaLabs is building a deterministic gate for agentic actions — before code changes, infrastructure commands, financial decisions, or governance operations are executed.",
          cta: "Watch the short",
        },
      },
    },
    faq: {
      title: "Frequently asked questions",
      items: [
        {
          q: "Is PythiaLabs another AI agent?",
          a: "No. PythiaLabs is not an agent. It is a safety and governance layer that evaluates actions before execution.",
        },
        {
          q: "Is this production-ready?",
          a: "No. PythiaLabs is an open-source MVP with deterministic local demos. We are looking for pilot partners, not unqualified production deployments.",
        },
        {
          q: "Does it replace human review?",
          a: "No. It improves human review by making risky actions visible, explainable, and traceable.",
        },
        {
          q: "Why not just use prompts?",
          a: "Prompts are not enough for high-risk actions. PythiaLabs focuses on deterministic checks, evidence, traces, and explicit action permissions.",
        },
        {
          q: "How is this different from RBAC or OPA?",
          a: "RBAC asks “is this principal allowed?”. PythiaLabs asks “should this specific action happen, given current evidence, freshness, and risk?”. It complements policy engines like OPA — you can keep them in front of or behind the gate.",
        },
        {
          q: "Does the gate call an LLM?",
          a: "No. The decision path is deterministic by design. Same input, same decision, every time. LLMs propose actions; PythiaLabs decides whether they execute.",
        },
        {
          q: "What's the license?",
          a: "Apache-2.0. Fork it, run it on your infrastructure, audit every line.",
        },
        {
          q: "What is the core idea?",
          a: "Before an AI agent acts, it must pass a gate.",
        },
      ],
    },
    founderLetter: {
      title: "Why I built this",
      body: "I spent 12 years in QA for fintech and infrastructure systems where the price of a wrong action is measured in audited regulatory filings. When I started watching AI agents do the same kind of work — modify code, call cloud APIs, prepare on-chain transactions — I kept asking the question that QA culture trained me to ask: where is the pre-execution checkpoint? PythiaLabs is my attempt to build it as deterministic, replayable, and reviewer-friendly as the systems I came from.",
      signoff: "— Aleksei Safonov, founder",
    },
    finalCta: {
      eyebrow: "For builders of high-risk AI agents",
      title: "Build AI agents that can be audited before they act",
      body: "The next generation of AI systems will not be judged only by how well they answer. They will be judged by whether their actions are safe, authorized, and explainable. PythiaLabs gives agentic AI a gate before execution.",
      primary: "Watch the demo",
      secondary: "View GitHub repo",
      tertiary: "Join early access",
      reassurance: "Apache-2.0 · Self-hostable · No vendor lock-in · No credit card",
    },
    closer: {
      title: "PythiaLabs is the pre-execution safety gate for AI agents.",
    },
    stage: {
      title: "Project stage",
      items: [
        "Open-source MVP with deterministic local demos.",
        "Not a production enforcement system, regulatory product, or certified safety framework.",
        "Looking for pilot partners, accelerators, technical collaborators, and early reviewers.",
      ],
    },
    founder: {
      title: "Founder",
      role: "Open-source maintainer · QA engineer",
      exp: "12+ years in high-reliability fintech and infrastructure QA.",
      focus:
        "Focused on deterministic oversight, evidence artifacts, and safer agentic AI workflows.",
    },
    contact: {
      title: "Contact",
      labels: {
        github: "GitHub",
        demo: "Demo",
        email: "Email",
        x: "X",
        telegram: "Telegram",
      },
    },
    stickyBar: {
      label: "Open-source · Apache-2.0 · Pre-execution safety gate for AI agents",
      cta: "Join early access",
    },
    footer: {
      tagline: "Open-source MVP · Apache-2.0",
      copyright: "© {year} PythiaLabs",
    },
  },

  ru: {
    htmlLang: "ru",
    langLabel: "RU",
    meta: {
      title: "Pre-execution safety gate для AI-агентов — PythiaLabs",
      description:
        "PythiaLabs — pre-execution safety gate для AI-агентов. Решает, должно ли действие агента быть ALLOW, BLOCK или ESCALATE до выполнения, с воспроизводимыми доказательствами.",
    },
    nav: {
      problem: "Проблема",
      idea: "Идея",
      solution: "Как работает",
      useCases: "Применение",
      videos: "Видео",
      faq: "FAQ",
      contact: "Контакты",
    },
    skipLink: "К содержимому",
    hero: {
      eyebrow: "Pre-execution safety layer · Open-source · Apache-2.0",
      headline: "Останавливайте опасные действия AI-агентов до их выполнения.",
      subtitle:
        "AI-агенты переходят от ответов к действиям. PythiaLabs решает, должны ли эти действия выполняться.",
      body: "AI-агенты уже меняют код, запускают команды, трогают инфраструктуру и участвуют в финансовых и governance-сценариях. PythiaLabs — pre-execution safety layer, проверяющий действие до того, как агент его выполнит.",
      tagline: "Не доверие. Верификация до выполнения.",
      starsAlt: "Звёзды на GitHub",
    },
    trustStrip: [
      "100% open-source",
      "Apache-2.0",
      "Детерминированно — 0 вызовов LLM в шлюзе",
      "Self-hosted",
      "Без телеметрии",
    ],
    cta: {
      primary: "Смотреть демо",
      secondary: "Открыть GitHub",
      tertiary: "Запросить ранний доступ",
      pilot: "Стать пилотным партнёром",
      contact: "Связаться",
    },
    videoBlock: {
      eyebrow: "Почему это важно",
      title: "Должно ли это действие AI-агента выполниться?",
      body: "Когда AI-агент получает возможность действовать, ошибка перестаёт быть просто плохим ответом — она становится реальным действием в реальном мире. PythiaLabs ставит проверяемые ворота перед исполнением: есть ли право на действие, достаточно ли контекста, валиден ли temporal/causal state, можно ли воспроизвести trace, и нужно ли разрешить, заблокировать или эскалировать на человека.",
      coreLabel: "Главный тезис",
      core: "Будущее agent safety — не пост-фактум дебаг. Это контроль до выполнения.",
      fallback: "Смотреть на YouTube",
    },
    problem: {
      title: "Опасный разрыв в agentic AI",
      intro: "AI-агенты уже могут:",
      items: [
        "менять production-код",
        "запускать DevOps-команды",
        "обрабатывать банковские и платёжные операции",
        "принимать workflow-решения",
        "действовать в Web3 treasury и governance",
        "выполнять действия через tools и APIs",
      ],
      punchline:
        "Но большинство систем всё ещё проверяют результат после выполнения. Это как поставить пожарную сигнализацию после того, как здание уже сгорело.",
    },
    bigIdea: {
      eyebrow: "Главная идея",
      title: "Прежде чем агент действует, он должен доказать, что действие разрешено",
      lead: "PythiaLabs задаёт один критический вопрос:",
      quote: "«Должно ли это действие AI-агента выполниться?»",
      not: [
        "Не «выглядит ли ответ умным?»",
        "Не «уверена ли модель?»",
        "Не «хорошо ли звучит reasoning?»",
      ],
      but: "Имеет ли это действие право быть выполненным прямо сейчас?",
    },
    solution: {
      title: "Как работает PythiaLabs",
      intro: "Четыре шага. Детерминированно. Воспроизводимо.",
      steps: [
        {
          name: "Агент предлагает действие",
          desc: "AI-агент предлагает действие: изменить код, выполнить команду, одобрить операцию, запустить workflow.",
        },
        {
          name: "PythiaLabs проверяет доказательства",
          desc: "Шлюз оценивает контекст, разрешения, риск, временное состояние и causal consistency.",
        },
        {
          name: "Действие решается до выполнения",
          desc: "Действие получает одно из: ALLOW · BLOCK · ESCALATE — и воспроизводимый audit trace.",
        },
        {
          name: "Каждое решение оставляет доказательства",
          desc: "PythiaLabs выдаёт прозрачный след: почему действие было разрешено, заблокировано или эскалировано.",
        },
      ],
      checksTitle: "Проверки",
      checks: [
        "авторизация",
        "актуальность доказательств",
        "контекст на момент решения",
        "границы прав",
        "учётные данные",
        "предположения о восстановлении",
        "риск действия",
      ],
      returnsTitle: "Возвращает",
    },
    artifact: {
      title: "Проверяемые артефакты решений",
      intro:
        "Каждое решение порождает JSON-артефакт: стабильные stop-причины, результаты по каждой проверке, воспроизводимый trace ID и дайджест с проверкой целостности. Это то, что реально читают ревьюеры и аудиторы.",
    },
    valueStack: {
      title: "Останавливайте опасные действия агентов до того, как они произойдут",
      intro:
        "PythiaLabs помогает командам строить AI-агентов, которым нельзя просто «доверять на слово». Вместо этого вы получаете:",
      items: [
        "Детерминированные safety gates — один и тот же вход даёт одно и то же решение",
        "Воспроизводимые трассы со стабильными stop-причинами",
        "Human-review workflow для эскалаций",
        "Audit-доказательства, которые читают ревьюеры и аудиторы",
        "Apache-2.0 — форкайте, запускайте на своей инфре, аудируйте каждую строку",
        "Никакого vendor lock-in: нет SaaS-зависимости, нет телеметрии, нет phone-home",
      ],
      footer: "Всё это · $0 · Open source",
    },
    comparison: {
      title: "До и с PythiaLabs",
      withoutTitle: "Без доказательного шлюза",
      withoutItems: [
        "Агенты действуют первыми, разбираетесь вы потом — инциденты постфактум",
        "Кастомные guard'ы расходятся по командам и тихо ломают инварианты",
        "«Почему это было разрешено?» — требует копания в логах",
        "Ревьюеры получают непоследовательные и невоспроизводимые доказательства",
      ],
      withTitle: "С PythiaLabs",
      withItems: [
        "Решения принимаются до выполнения — никаких сюрпризов",
        "Один детерминированный engine, один набор проверок везде",
        "У каждого решения есть stop-причина, трасса и проверяемый дайджест",
        "Ревьюеры каждый раз получают один и тот же артефакт, replay включён",
      ],
    },
    useCases: {
      title: "Где это становится критично",
      items: [
        {
          name: "DevOps / Инфраструктура",
          desc: "Перед тем как агент удалит volume, перезапустит сервис или изменит конфигурацию, PythiaLabs проверяет, имеет ли он право это сделать.",
        },
        {
          name: "Банки / FinTech",
          desc: "Перед одобрением рискованной операции шлюз проверяет доказательства, лимиты, контекст и временную валидность.",
        },
        {
          name: "Web3 / DAO governance",
          desc: "Перед treasury-действием или governance-операцией агент должен пройти safety gate.",
        },
        {
          name: "AI-агенты для кода",
          desc: "Перед merge, patch или production-change агент оставляет проверяемый trace и проходит pre-execution validation.",
        },
      ],
    },
    positioning: {
      eyebrow: "Позиционирование",
      title: "PythiaLabs — не очередной агент",
      negatives: [
        "Не чатбот.",
        "Не очередная обёртка над агентом.",
        "Не «prompt engineering safety».",
      ],
      claim: "PythiaLabs — это шлюз перед действием агента.",
      tagsLabel: "Когда агент хочет выполнить действие, шлюз решает:",
      tags: ["ALLOW", "BLOCK", "ESCALATE", "AUDIT"],
    },
    authority: {
      eyebrow: "Создано для следующего поколения agentic-систем",
      title:
        "Автономность без проверяемых прав на действие — это не интеллект, это риск",
      body: "AI-индустрия быстро движется к автономным агентам. PythiaLabs построен вокруг простой идеи:",
      pullQuote:
        "Сильный AI-агент должен не только рассуждать. Он должен быть ограничен проверяемыми правами на действие.",
    },
    founderVideosBlock: {
      eyebrow: "От основателя",
      title: "Три коротких видео",
      cards: {
        longForm: {
          name: "Видео 1 — главный тезис",
          headline: "Должно ли это действие AI-агента выполниться?",
          desc: "AI-агенты становятся actor'ами, а не просто responder'ами. PythiaLabs вводит детерминированный safety layer, который оценивает действие до того, как оно достигнет реального мира.",
          cta: "Смотреть полный обзор",
        },
        short1: {
          name: "Шортс — крючок",
          headline: "Кто решает, разрешено ли действие?",
          desc: "AI-агенты больше не просто генерируют текст. Они начинают совершать действия. PythiaLabs фокусируется на вопросе, на который придётся отвечать каждой серьёзной AI-системе.",
          cta: "Смотреть шортс",
        },
        short2: {
          name: "Шортс — новая категория",
          headline: "Pre-execution control",
          desc: "Следующая граница AI safety — это контроль до выполнения. PythiaLabs строит детерминированный шлюз для agentic-действий: перед изменением кода, infra-командой, финансовым решением или governance-операцией.",
          cta: "Смотреть шортс",
        },
      },
    },
    faq: {
      title: "Частые вопросы",
      items: [
        {
          q: "PythiaLabs — это очередной AI-агент?",
          a: "Нет. PythiaLabs — не агент. Это safety- и governance-слой, который оценивает действия до выполнения.",
        },
        {
          q: "Это production-ready?",
          a: "Нет. PythiaLabs — open-source MVP с детерминированными локальными демо. Мы ищем пилотных партнёров, а не бесконтрольные production-деплои.",
        },
        {
          q: "Заменяет ли это human review?",
          a: "Нет. Это улучшает human review, делая рискованные действия видимыми, объяснимыми и трассируемыми.",
        },
        {
          q: "Почему просто не использовать промпты?",
          a: "Промптов недостаточно для высокорисковых действий. PythiaLabs фокусируется на детерминированных проверках, доказательствах, трассах и явных правах на действие.",
        },
        {
          q: "Чем это отличается от RBAC или OPA?",
          a: "RBAC отвечает на «можно ли этому principal'у?». PythiaLabs отвечает на «должно ли это конкретное действие произойти с учётом текущих доказательств, их свежести и риска?». Это дополняет policy engine'ы вроде OPA.",
        },
        {
          q: "Шлюз вызывает LLM?",
          a: "Нет. Путь принятия решения детерминированный по дизайну. Один и тот же вход — одно и то же решение. LLM предлагают действия; PythiaLabs решает, выполнятся ли они.",
        },
        {
          q: "Какая лицензия?",
          a: "Apache-2.0. Форкайте, запускайте на своей инфре, аудируйте каждую строку.",
        },
        {
          q: "В чём главная идея?",
          a: "Прежде чем AI-агент действует, он должен пройти шлюз.",
        },
      ],
    },
    founderLetter: {
      title: "Почему я это сделал",
      body: "Я провёл 12 лет в QA финтеха и инфраструктуры — там, где цена неправильного действия измеряется в аудируемых отчётах для регулятора. Когда я начал смотреть, как AI-агенты делают ту же работу — меняют код, дёргают cloud API, готовят on-chain транзакции — я задавал тот же вопрос, которому меня научила QA-культура: где точка контроля перед выполнением? PythiaLabs — моя попытка сделать её такой же детерминированной, воспроизводимой и удобной для ревьюеров, как системы, из которых я пришёл.",
      signoff: "— Алексей Сафонов, основатель",
    },
    finalCta: {
      eyebrow: "Для тех, кто строит AI-агентов с высоким риском",
      title: "Стройте AI-агентов, которых можно аудировать до их действий",
      body: "Следующее поколение AI-систем будут оценивать не только по тому, насколько хорошо они отвечают. Их будут оценивать по тому, безопасны ли, авторизованы ли и объяснимы ли их действия. PythiaLabs даёт agentic AI шлюз перед выполнением.",
      primary: "Смотреть демо",
      secondary: "Открыть GitHub",
      tertiary: "Запросить ранний доступ",
      reassurance: "Apache-2.0 · Self-hosted · Без vendor lock-in · Без карточки",
    },
    closer: {
      title: "PythiaLabs — pre-execution safety gate для AI-агентов.",
    },
    stage: {
      title: "Стадия проекта",
      items: [
        "Open-source MVP с детерминированными локальными демо.",
        "Не production-система контроля, не комплаенс-продукт, не сертифицированный safety-фреймворк.",
        "Ищем пилотных партнёров, акселераторы, технических сотрудников и ранних ревьюеров.",
      ],
    },
    founder: {
      title: "Основатель",
      role: "Open-source мейнтейнер · QA-инженер",
      exp: "12+ лет в QA высоконадёжного финтеха и инфраструктуры.",
      focus:
        "Фокус — детерминированный оверсайт, доказательные артефакты и безопасные агентные AI-сценарии.",
    },
    contact: {
      title: "Контакты",
      labels: {
        github: "GitHub",
        demo: "Демо",
        email: "Email",
        x: "X",
        telegram: "Telegram",
      },
    },
    stickyBar: {
      label: "Open-source · Apache-2.0 · Pre-execution safety gate для AI-агентов",
      cta: "Запросить ранний доступ",
    },
    footer: {
      tagline: "Open-source MVP · Apache-2.0",
      copyright: "© {year} PythiaLabs",
    },
  },

  zh: {
    htmlLang: "zh-Hans",
    langLabel: "中文",
    meta: {
      title: "面向 AI Agent 的执行前安全门控 — PythiaLabs",
      description:
        "PythiaLabs 是面向 AI Agent 的执行前安全门控。在执行前判定行动应 ALLOW、BLOCK 或 ESCALATE，并产出可重放的证据。",
    },
    nav: {
      problem: "问题",
      idea: "核心理念",
      solution: "工作原理",
      useCases: "应用场景",
      videos: "视频",
      faq: "常见问题",
      contact: "联系",
    },
    skipLink: "跳到内容",
    hero: {
      eyebrow: "执行前安全层 · 开源 · Apache-2.0",
      headline: "在 AI Agent 执行前阻止危险行动。",
      subtitle:
        "AI Agent 正从“回答”走向“行动”。PythiaLabs 决定这些行动是否应当执行。",
      body: "AI Agent 已经在修改代码、运行命令、操作基础设施，并参与金融与治理流程。PythiaLabs 是一个执行前安全层，在 Agent 执行前评估它的行动。",
      tagline: "不是信任，而是执行前的验证。",
      starsAlt: "GitHub 星标",
    },
    trustStrip: [
      "100% 开源",
      "Apache-2.0",
      "确定性 — 门控路径中无 LLM 调用",
      "可自托管",
      "无遥测",
    ],
    cta: {
      primary: "观看演示",
      secondary: "查看 GitHub",
      tertiary: "申请早期访问",
      pilot: "申请试点合作",
      contact: "联系",
    },
    videoBlock: {
      eyebrow: "为什么这件事重要",
      title: "这个 AI Agent 行动应该被执行吗？",
      body: "当 AI Agent 拥有了行动能力，错误就不再只是糟糕的回答，而是真实世界中的真实行动。PythiaLabs 在执行前设置一个可校验的门：Agent 是否有权执行、上下文是否充分、时间/因果状态是否有效、轨迹是否可重放、是允许、阻止还是升级到人。",
      coreLabel: "核心信息",
      core: "Agent 安全的未来不是事后调试，而是执行前的控制。",
      fallback: "在 YouTube 观看",
    },
    problem: {
      title: "Agentic AI 中的危险缺口",
      intro: "AI Agent 已能：",
      items: [
        "修改生产代码",
        "运行 DevOps 命令",
        "处理银行与支付流程",
        "做出工作流决策",
        "在 Web3 国库与治理中行动",
        "通过 tools 与 API 执行",
      ],
      punchline:
        "但大多数系统仍在执行后才校验结果。这就像在大楼烧毁后才安装火警警报。",
    },
    bigIdea: {
      eyebrow: "核心理念",
      title: "在 Agent 行动之前，必须证明该行动是被允许的",
      lead: "PythiaLabs 提出一个关键问题：",
      quote: "“这个 AI Agent 行动应该被执行吗？”",
      not: [
        "不是“答案听起来聪明吗？”",
        "不是“模型有信心吗？”",
        "不是“推理听起来对吗？”",
      ],
      but: "这个行动现在是否有权被执行？",
    },
    solution: {
      title: "PythiaLabs 工作原理",
      intro: "四个步骤。确定性。可重放。",
      steps: [
        {
          name: "Agent 提议行动",
          desc: "AI Agent 提议行动：修改代码、运行命令、批准操作、启动工作流。",
        },
        {
          name: "PythiaLabs 校验证据",
          desc: "门控评估上下文、权限、风险、时间状态与因果一致性。",
        },
        {
          name: "在执行前作出决策",
          desc: "行动获得 ALLOW · BLOCK · ESCALATE 之一，并附可重放的审计轨迹。",
        },
        {
          name: "每个决策都留下证据",
          desc: "PythiaLabs 输出透明轨迹：行动为何被允许、阻止或升级。",
        },
      ],
      checksTitle: "检查项",
      checks: [
        "授权",
        "证据新鲜度",
        "决策时上下文",
        "权限边界",
        "凭据",
        "恢复假设",
        "行动风险",
      ],
      returnsTitle: "返回",
    },
    artifact: {
      title: "可审查的决策产物",
      intro:
        "每个决策都会生成 JSON 产物：稳定的停止原因、各项检查结果、可重放的 trace ID，以及可校验的摘要。这才是审查者和审计者真正会读的内容。",
    },
    valueStack: {
      title: "在危险的 Agent 行动发生之前阻止它",
      intro:
        "PythiaLabs 帮助团队构建不能仅凭“信任”交付的 AI Agent。你将获得：",
      items: [
        "确定性安全门控 — 同样输入永远得到同样决策",
        "带稳定停止原因的可重放轨迹",
        "升级到人审的 human-review 工作流",
        "审查者与审计者真正会读的证据",
        "Apache-2.0 — 可 fork、可自部署、可审计每一行",
        "零供应商锁定：无 SaaS 依赖、无遥测、无回连",
      ],
      footer: "全部 · $0 · 开源",
    },
    comparison: {
      title: "对比：有无 PythiaLabs",
      withoutTitle: "没有证据门控",
      withoutItems: [
        "代理先行动，事后再排查 — 事故都是事后的",
        "各团队的自定义守卫漂移，悄悄破坏不变量",
        "“为什么这被允许？”需要去翻日志",
        "审查者拿到的证据互不一致、无法重放",
      ],
      withTitle: "使用 PythiaLabs",
      withItems: [
        "决策在执行前评估 — 不会出现意外行动",
        "一个确定性引擎、一套检查、统一应用",
        "每个决策都有停止原因、轨迹与可校验摘要",
        "审查者每次拿到的是同样的产物，含重放",
      ],
    },
    useCases: {
      title: "关键场景",
      items: [
        {
          name: "DevOps / 基础设施",
          desc: "在 Agent 删除卷、重启服务或修改配置之前，PythiaLabs 校验它是否有权这样做。",
        },
        {
          name: "银行 / FinTech",
          desc: "在批准风险操作之前，门控会检查证据、限额、上下文与时间有效性。",
        },
        {
          name: "Web3 / DAO 治理",
          desc: "在国库或治理操作之前，Agent 必须通过安全门控。",
        },
        {
          name: "AI 编码代理",
          desc: "在合并、补丁或生产变更之前，Agent 留下可校验的轨迹并通过执行前验证。",
        },
      ],
    },
    positioning: {
      eyebrow: "定位",
      title: "PythiaLabs 不是又一个 Agent",
      negatives: ["不是聊天机器人。", "不是又一个 Agent 包装。", "不是“提示工程安全”。"],
      claim: "PythiaLabs 是 Agent 行动之前的门控。",
      tagsLabel: "当 Agent 想执行时，门控决定：",
      tags: ["ALLOW", "BLOCK", "ESCALATE", "AUDIT"],
    },
    authority: {
      eyebrow: "为下一代 agentic 系统而生",
      title: "没有可校验行动权限的自主性，不是智能，而是风险",
      body: "AI 行业正快速走向自主代理。PythiaLabs 构建在一个简单理念之上：",
      pullQuote: "强大的 AI Agent 不只是要会推理，更应受到可校验行动权限的约束。",
    },
    founderVideosBlock: {
      eyebrow: "来自创始人",
      title: "三个短视频",
      cards: {
        longForm: {
          name: "视频 1 — 主张",
          headline: "这个 AI Agent 行动应该被执行吗？",
          desc: "AI Agent 正在成为行动者，而非仅仅是回应者。PythiaLabs 引入一个确定性的安全层，在行动到达真实世界之前评估它是否应该执行。",
          cta: "观看完整讲解",
        },
        short1: {
          name: "短视频 — 钩子",
          headline: "谁来决定行动是否被允许？",
          desc: "AI Agent 不再只是生成文本，它们正在开始采取行动。PythiaLabs 关注每个严肃 AI 系统都需要回答的问题。",
          cta: "观看短视频",
        },
        short2: {
          name: "短视频 — 新品类",
          headline: "执行前控制",
          desc: "AI 安全的下一个前沿是执行前控制。PythiaLabs 正在为 agentic 行动构建确定性门控 — 在代码变更、基础设施命令、金融决策或治理操作执行之前。",
          cta: "观看短视频",
        },
      },
    },
    faq: {
      title: "常见问题",
      items: [
        {
          q: "PythiaLabs 是又一个 AI Agent 吗？",
          a: "不是。PythiaLabs 不是 Agent，而是在执行前评估行动的安全与治理层。",
        },
        {
          q: "是否生产可用？",
          a: "尚未。PythiaLabs 是带有确定性本地演示的开源 MVP。我们寻找的是试点伙伴，而不是无条件的生产部署。",
        },
        {
          q: "它会取代人审吗？",
          a: "不会。它通过让风险行动可见、可解释、可追踪来改进人审。",
        },
        {
          q: "为什么不直接用提示词？",
          a: "对于高风险行动，仅靠提示词是不够的。PythiaLabs 关注确定性检查、证据、轨迹与显式的行动权限。",
        },
        {
          q: "与 RBAC 或 OPA 有何不同？",
          a: "RBAC 问“这个 principal 是否被允许？”。PythiaLabs 问“在当前证据、新鲜度与风险下，这个具体行动应该发生吗？”，与 OPA 等策略引擎互补。",
        },
        {
          q: "门控会调用 LLM 吗？",
          a: "不会。决策路径设计上是确定性的：同样输入 → 同样决策。LLM 提议行动；PythiaLabs 决定是否执行。",
        },
        {
          q: "采用什么许可证？",
          a: "Apache-2.0。可 fork、可自部署、可审计每一行。",
        },
        {
          q: "核心理念是什么？",
          a: "在 AI Agent 行动之前，它必须通过门控。",
        },
      ],
    },
    founderLetter: {
      title: "我为什么做这件事",
      body: "我在金融科技与基础设施 QA 行业工作了 12 年——在那里，一次错误行动的代价以受审计的监管报告来衡量。当我开始观察 AI Agent 做同类工作——修改代码、调用云 API、准备链上交易——我总在问 QA 文化教给我的同一个问题：执行前的检查点在哪里？PythiaLabs 就是我把它做得像我来自的系统一样确定、可重放、对审查者友好的尝试。",
      signoff: "— Aleksei Safonov，创始人",
    },
    finalCta: {
      eyebrow: "为构建高风险 AI Agent 的团队",
      title: "构建可在行动前被审计的 AI Agent",
      body: "下一代 AI 系统不会只以回答得多好被评判，更会以行动是否安全、被授权、可解释来评判。PythiaLabs 为 agentic AI 提供执行前的门控。",
      primary: "观看演示",
      secondary: "查看 GitHub",
      tertiary: "申请早期访问",
      reassurance: "Apache-2.0 · 可自托管 · 无供应商锁定 · 无需信用卡",
    },
    closer: {
      title: "PythiaLabs 是面向 AI Agent 的执行前安全门控。",
    },
    stage: {
      title: "项目阶段",
      items: [
        "具有确定性本地演示的开源 MVP。",
        "并非生产级执行系统、合规产品或经认证的安全框架。",
        "正在寻找试点合作伙伴、加速器、技术合作者与早期审查者。",
      ],
    },
    founder: {
      title: "创始人",
      role: "开源维护者 · QA 工程师",
      exp: "12 年以上高可靠性金融科技与基础设施 QA 经验。",
      focus: "专注于确定性监督、证据产物以及更安全的 AI Agent 工作流。",
    },
    contact: {
      title: "联系",
      labels: {
        github: "GitHub",
        demo: "演示",
        email: "邮箱",
        x: "X",
        telegram: "Telegram",
      },
    },
    stickyBar: {
      label: "开源 · Apache-2.0 · 面向 AI Agent 的执行前安全门控",
      cta: "申请早期访问",
    },
    footer: {
      tagline: "开源 MVP · Apache-2.0",
      copyright: "© {year} PythiaLabs",
    },
  },
};

export const localeOrder = ["en", "ru", "zh"];

const optionalLocalePrefixes = ["exampleDecision."];

function isOptionalLocaleKey(key) {
  return optionalLocalePrefixes.some((prefix) => key.startsWith(prefix));
}

function collectKeys(obj, prefix = "") {
  const keys = [];
  for (const [k, v] of Object.entries(obj)) {
    const path = prefix ? `${prefix}.${k}` : k;
    if (v !== null && typeof v === "object" && !Array.isArray(v)) {
      keys.push(...collectKeys(v, path));
    } else {
      keys.push(path);
    }
  }
  return keys;
}

export function validateLocales(reference = "en") {
  const refKeys = new Set(collectKeys(locales[reference]));
  const errors = [];
  for (const id of localeOrder) {
    if (id === reference) continue;
    const keys = new Set(collectKeys(locales[id]));
    for (const k of refKeys) {
      if (isOptionalLocaleKey(k)) continue;
      if (!keys.has(k)) errors.push(`locale ${id}: missing key '${k}'`);
    }
    for (const k of keys) {
      if (!refKeys.has(k)) errors.push(`locale ${id}: extra key '${k}'`);
    }
  }
  if (errors.length) {
    throw new Error(`locale validation failed:\n  ${errors.join("\n  ")}`);
  }
}
