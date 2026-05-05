export const locales = {
  en: {
    htmlLang: "en",
    ogLocale: "en_US",
    langLabel: "EN",
    meta: {
      title: "Pre-execution safety gate for AI agents — PythiaLabs",
      description:
        "Open-source pre-execution gate for AI and agentic systems: ALLOW, BLOCK, or ESCALATE before tools run. Deterministic checks, replayable traces, audit-ready evidence — self-hosted Elixir library, Apache-2.0.",
      keywords:
        "AI agent safety, pre-execution gate, agentic AI, AI governance, ALLOW BLOCK ESCALATE, deterministic policy gate, audit trail, open source AI safety, Apache-2.0, Elixir agent guard, OPA RBAC complement, DevOps AI agents, fintech AI risk, Web3 treasury governance",
      ogImageAlt:
        "PythiaLabs — pre-execution safety gate for AI agents: verify actions before they execute",
    },
    nav: {
      problem: "Problem",
      idea: "Big idea",
      solution: "How it works",
      integration: "Integration",
      quickstart: "Quick start",
      fit: "Who it's for",
      pilot: "Pilot",
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
        "The gate returns ALLOW, BLOCK, or ESCALATE before your agent runs destructive tools — deterministic, replayable, on your infrastructure.",
      body: "Code, infra, banking, governance: when agents act, PythiaLabs evaluates the proposal and evidence first, not the chat transcript.",
      tagline: "Verify before execute. Evidence your reviewers can replay.",
      starsAlt: "GitHub stars",
    },
    trustStrip: [
      "100% open-source",
      "Apache-2.0",
      "Deterministic — 0 LLM calls in the gate",
      "Self-hostable",
      "No telemetry",
    ],
    cta: {
      primary: "Join early access",
      demo: "Watch the demo",
      secondary: "View GitHub repo",
      pilot: "Apply as pilot partner",
      contact: "Contact",
    },
    heroStats: {
      ariaLabel: "Repository at a glance",
      showcases: "deterministic local showcases",
      tests: "Elixir test files for gates and evidence",
      licenseLine: "License",
      licenseValue: "Apache-2.0",
      llmLine: "LLM calls in the gate",
    },
    ifYou: {
      title: "If this sounds like your team, PythiaLabs is built for you",
      items: [
        "You run (or are about to run) agents that can change production, money, or governance — not just chat.",
        "Post-hoc logs are not enough: you need a decision record before the tool fires.",
        "RBAC and coarse policy are necessary but do not answer “should this exact action run right now, with this evidence?”",
        "Reviewers and security want the same replayable artifact every time — not screenshots of a thread.",
      ],
    },
    quickstart: {
      title: "Get to a working gate in one sitting",
      intro:
        "No credit card. No SaaS account. Clone, test, run a showcase, then wire your orchestrator the same way.",
      steps: [
        {
          name: "Clone and install deps",
          desc: "`git clone` the repository, then `mix deps.get` (same toolchain as CI).",
        },
        {
          name: "Prove the test suite",
          desc: "Run `mix test` — this is the contract the gate is held to.",
        },
        {
          name: "Run a showcase script",
          desc: "Try `mix run examples/agent_infra_action_showcase.exs` (or banking / Web3 showcases) and compare stdout to `docs/*_expected_output.md`.",
        },
        {
          name: "Call the evaluator before tools",
          desc: "From your agent runner, pass a structured proposal plus decision-time evidence; block execution unless the outcome is ALLOW (or route ESCALATE per your policy).",
        },
      ],
    },
    midCta: {
      line: "Watch the walkthrough, run the repo locally, or start a pilot — your stack, your infrastructure.",
    },
    videoBlock: {
      eyebrow: "Watch why this matters",
      title: "Should this AI agent action execute?",
      body: "When agents can act, a bad answer becomes a real incident. PythiaLabs checks permission, evidence freshness, risk, and replayability — then allows, blocks, or escalates to a human before anything irreversible runs.",
      coreLabel: "Core message",
      core: "The future of agent safety is not after-the-fact debugging. It is pre-execution control.",
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
      technicalSummary: "For engineers: canonical encoding and digests",
      introPlain:
        "Every decision ships as structured evidence: outcome, why it stopped, per-check results, and a trace reviewers can replay. Auditors read the same artifact your CI can snapshot — not screenshots of a chat.",
      introTechnical:
        "Exports use canonical encoding (`pythia.canonical_export.v1`) and SHA-256 so the same evaluated snapshot always yields the same hex digest; re-run exports in CI to catch drift.",
    },
    pilotOutcome: {
      title: "What a pilot week actually delivers",
      intro:
        "This is an open-source MVP — not magic. A focused pilot still gives your team concrete, reviewable outputs:",
      items: [
        "One or two high-risk agent flows mapped to structured proposals and decision-time evidence.",
        "ALLOW / BLOCK / ESCALATE outcomes with stable stop reasons before tools execute.",
        "Replayable traces and optional SHA-256 digests your reviewers can diff in CI.",
        "Shared vocabulary with security and compliance: fewer arguments, clearer escalations.",
      ],
      footnote:
        "Scope and pace depend on your stack. Email with your scenario — we prioritize serious design partners.",
    },
    integration: {
      title: "How you integrate it (today)",
      intro:
        "PythiaLabs ships as an Apache-2.0 Elixir library — not a hosted control plane. You keep your agents and tools; the gate is a library boundary your orchestrator calls before anything irreversible happens.",
      items: [
        {
          name: "Call site in your stack",
          desc: "Link the library from your agent runner or a thin sidecar service. There is no required SaaS, telemetry, or phone-home — everything runs on your infra.",
        },
        {
          name: "Structured proposal → deterministic evaluation",
          desc: "Pass a typed proposed action plus decision-time evidence (approvals, policy state, freshness markers, environment context). The engine returns ALLOW / BLOCK / ESCALATE with a replayable trace; showcases also emit exportable digests for audit handoff.",
        },
        {
          name: "Complements RBAC and policy engines",
          desc: "OPA and RBAC answer “is this principal allowed in general?”. The gate answers “should this exact action run right now?” using decision-time evidence, freshness, risk, and temporal/causal checks — often in front of or behind your existing policy layer.",
        },
        {
          name: "Reproducible digest, not vibes",
          desc: "Evaluator outputs are canonicalized (see `pythia.canonical_export.v1` in the repository) and hashed with SHA-256. Tests pin expected digests for accepted snapshots and reject tampered payloads — that is the concrete meaning of “same inputs, same digest.”",
        },
      ],
      repoNote:
        "Reviewer quickstart: clone the repo, run `mix test`, then `mix run examples/agent_infra_action_showcase.exs` (and the banking / Web3 showcases). Expected reviewer-facing output lives under `docs/*_expected_output.md`.",
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
      vsTitle: "How this differs from nearby approaches",
      vsItems: [
        {
          name: "Prompt-only guardrails",
          desc: "Instructions to the model are not a boundary for high-risk tools. The gate is deterministic code with stable stop reasons and tests — not prompt text.",
        },
        {
          name: "RBAC / coarse IAM alone",
          desc: "Static roles don't encode “right now, with this evidence snapshot, under this risk.” The gate consumes decision-time context and freshness.",
        },
        {
          name: "Policy engines such as OPA",
          desc: "OPA answers authorization rules you express. PythiaLabs targets agent-action proposals plus replayable traces and digest exports for reviewers — complement, not duplicate.",
        },
        {
          name: "Post-hoc monitoring",
          desc: "Metrics after execution cannot undo a transfer, deletion, or governance vote. Pre-execution is the control point.",
        },
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
      oracleEyebrow: "Why this name fits",
      oracleQuote:
        "You didn't come here to make the choice. You're here to try to understand why you made it.",
      oracleSource: "The Oracle, The Matrix",
      oracleBridge:
        'When an agent acts, the risk is that the "why" only appears after the damage. PythiaLabs makes the why legible first: stable stop reasons and a replayable trace before the tool runs — so humans can understand the choice while it can still be stopped.',
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
          a: "RBAC asks “is this principal allowed?”. PythiaLabs asks “should this specific action happen, given current evidence, freshness, and risk?”. It complements policy engines like OPA — use them for static rules and the gate for decision-time, evidence-bound checks.",
        },
        {
          q: "How do I integrate PythiaLabs with my agents?",
          a: "Start from the Elixir library in this repository: wire your orchestrator to call the evaluator before tool execution, pass structured proposals plus decision-time snapshots, and store or forward the trace plus optional SHA-256 digest exports for reviewers. Follow README “Reviewer quickstart” (`mix test` and the `examples/*_showcase.exs` scripts) and compare stdout to the `docs/*_expected_output.md` files.",
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
      primary: "Join early access",
      demo: "Watch the demo",
      secondary: "View GitHub repo",
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
    ogLocale: "ru_RU",
    langLabel: "RU",
    meta: {
      title: "Pre-execution safety gate для AI-агентов — PythiaLabs",
      description:
        "Open-source шлюз до выполнения для AI и agentic-систем: ALLOW, BLOCK или ESCALATE до запуска tools. Детерминированные проверки, воспроизводимые трассы, артефакты для аудита — self-hosted Elixir-библиотека, Apache-2.0.",
      keywords:
        "безопасность AI-агентов, pre-execution gate, agentic AI, governance AI, ALLOW BLOCK ESCALATE, детерминированный policy gate, audit trail, open source AI safety, Apache-2.0, Elixir guard, OPA RBAC, DevOps агенты, финтех риск AI, Web3 treasury",
      ogImageAlt:
        "PythiaLabs — pre-execution safety gate для AI-агентов: проверка действий до выполнения",
    },
    nav: {
      problem: "Проблема",
      idea: "Идея",
      solution: "Как работает",
      integration: "Интеграция",
      quickstart: "Быстрый старт",
      fit: "Кому подходит",
      pilot: "Пилот",
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
        "Шлюз возвращает ALLOW, BLOCK или ESCALATE до того, как агент запустит разрушительные tools — детерминированно, воспроизводимо, на вашей инфре.",
      body: "Код, инфра, банки, governance: когда агент действует, PythiaLabs сначала оценивает предложение и доказательства, а не расшифровку чата.",
      tagline: "Проверка до исполнения. Доказательства, которые ревьюер может перепроиграть.",
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
      primary: "Запросить ранний доступ",
      demo: "Смотреть демо",
      secondary: "Открыть GitHub",
      pilot: "Стать пилотным партнёром",
      contact: "Связаться",
    },
    heroStats: {
      ariaLabel: "Сигналы репозитория",
      showcases: "детерминированных локальных showcase",
      tests: "файлов тестов для шлюзов и доказательств",
      licenseLine: "Лицензия",
      licenseValue: "Apache-2.0",
      llmLine: "вызовов LLM в шлюзе",
    },
    ifYou: {
      title: "Если это про вашу команду — PythiaLabs для вас",
      items: [
        "Вы запускаете (или собираетесь) агентов, которые трогают прод, деньги или governance — не только чат.",
        "Постфактум логов мало: нужна запись решения до вызова tool.",
        "RBAC и грубая политика нужны, но не отвечают: «должно ли выполниться именно это действие прямо сейчас с этими доказательствами?»",
        "Security и ревьюерам нужен один и тот же воспроизводимый артефакт — не скриншот треда.",
      ],
    },
    quickstart: {
      title: "Рабочий шлюз за одну сессию",
      intro:
        "Без карты. Без SaaS-аккаунта. Клонируйте, прогоните тесты и showcase, затем подключите оркестратор так же.",
      steps: [
        {
          name: "Клон и зависимости",
          desc: "Сделайте `git clone` репозитория, затем `mix deps.get` (как в CI).",
        },
        {
          name: "Прогон тестов",
          desc: "Выполните `mix test` — это контракт, которому соответствует шлюз.",
        },
        {
          name: "Showcase-скрипт",
          desc: "Запустите `mix run examples/agent_infra_action_showcase.exs` (или banking / Web3) и сверьте stdout с `docs/*_expected_output.md`.",
        },
        {
          name: "Вызов до tools",
          desc: "Из agent runner передайте структурированное предложение и evidence на момент решения; блокируйте исполнение, если исход не ALLOW (или обрабатывайте ESCALATE по своей политике).",
        },
      ],
    },
    midCta: {
      line: "Посмотрите walkthrough, прогоните репозиторий локально или начните пилот — ваш стек, ваша инфраструктура.",
    },
    videoBlock: {
      eyebrow: "Почему это важно",
      title: "Должно ли это действие AI-агента выполниться?",
      body: "Когда агент может действовать, плохой ответ превращается в инцидент. PythiaLabs проверяет право, свежесть доказательств, риск и воспроизводимость — затем разрешает, блокирует или эскалирует на человека до необратимых действий.",
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
      technicalSummary: "Для инженеров: канонизация и дайджесты",
      introPlain:
        "Каждое решение — это структурированное доказательство: исход, причина остановки, результаты проверок и trace, который ревьюер может перепроиграть. Аудитор читает тот же артефакт, что и ваш CI может зафиксировать снимком — не скриншот чата.",
      introTechnical:
        "Экспорт использует каноническое кодирование (`pythia.canonical_export.v1`) и SHA-256: одна и та же оценённая снапшот-сборка всегда даёт тот же hex-дайджест; повторный экспорт в CI ловит дрейф.",
    },
    pilotOutcome: {
      title: "Что даёт пилот за короткий срок",
      intro:
        "Это open-source MVP — не волшебство. Сфокусированный пилот всё равно даёт команде конкретные, проверяемые результаты:",
      items: [
        "Один–два высокорисковых агент-сценария в виде структурированных предложений и decision-time evidence.",
        "Исходы ALLOW / BLOCK / ESCALATE со стабильными stop-причинами до выполнения tools.",
        "Воспроизводимые trace и при необходимости SHA-256 дайджесты, которые ревью могут сравнивать в CI.",
        "Общий язык с security и комплаенсом — меньше споров, яснее эскалации.",
      ],
      footnote:
        "Объём и темп зависят от вашего стека. Напишите с описанием сценария — приоритет у серьёзных design partners.",
    },
    integration: {
      title: "Как это подключать (сегодня)",
      intro:
        "PythiaLabs поставляется как open-source Elixir-библиотека под Apache-2.0 — не как hosted control plane. Агенты и tools остаются у вас; шлюз — это граница библиотеки, которую оркестратор вызывает до необратимых действий.",
      items: [
        {
          name: "Место вызова в вашем стеке",
          desc: "Подключите библиотеку из agent runner'а или тонкого sidecar-сервиса. Ни SaaS по умолчанию, ни телеметрии, ни phone-home — всё на вашей инфре.",
        },
        {
          name: "Структурированное предложение → детерминированная оценка",
          desc: "Передайте типизированное предложение действия плюс decision-time evidence (апрувы, состояние политики, метки свежести, контекст среды). Движок возвращает ALLOW / BLOCK / ESCALATE с воспроизводимым trace; в showcase также экспортируются дайджесты для аудиторской передачи.",
        },
        {
          name: "Дополняет RBAC и policy engine",
          desc: "OPA и RBAC отвечают «разрешён ли principal в принципе?». Шлюз отвечает «должно ли выполниться именно это действие прямо сейчас?» с учётом evidence, freshness, риска и temporal/causal проверок — часто перед или после вашего слоя политик.",
        },
        {
          name: "Воспроизводимый дайджест, не «ощущения»",
          desc: "Выходы evaluators канонизируются (см. `pythia.canonical_export.v1` в репозитории) и хешируются SHA-256. Тесты закрепляют ожидаемые дайджесты для принятых снапшотов и отклоняют подменённые payload'ы — это конкретный смысл формулировки «те же входы → тот же дайджест».",
        },
      ],
      repoNote:
        "Быстрый старт для ревьюеров: клонировать репозиторий, выполнить `mix test`, затем `mix run examples/agent_infra_action_showcase.exs` (и banking / Web3 showcase). Ожидаемый вывод для ревью — в `docs/*_expected_output.md`.",
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
      vsTitle: "Чем это отличается от близких подходов",
      vsItems: [
        {
          name: "Только промпты и guardrails",
          desc: "Инструкции модели — не граница для высокорисковых tools. Шлюз — детерминированный код со стабильными stop-причинами и тестами, а не текст промпта.",
        },
        {
          name: "Только RBAC / грубый IAM",
          desc: "Статические роли не кодируют «прямо сейчас, с этим снапшотом доказательств, при этом риске». Шлюз потребляет контекст на момент решения и свежесть evidence.",
        },
        {
          name: "Policy engine вроде OPA",
          desc: "OPA отвечает на выраженные вами правила авторизации. PythiaLabs — про предложения действий агента, воспроизводимые trace и экспорт дайджестов для ревью; это дополнение, не дубль.",
        },
        {
          name: "Пост-мониторинг",
          desc: "Метрики после исполнения не отменят перевод, удаление или голосование. Контрольная точка — до выполнения.",
        },
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
      title: "Автономность без проверяемых прав на действие — это не интеллект, это риск",
      body: "AI-индустрия быстро движется к автономным агентам. PythiaLabs построен вокруг простой идеи:",
      pullQuote:
        "Сильный AI-агент должен не только рассуждать. Он должен быть ограничен проверяемыми правами на действие.",
      oracleEyebrow: "Почему это созвучно названию",
      oracleQuote:
        "Ты пришёл не затем, чтобы сделать выбор. Ты пришёл, чтобы понять, почему ты его сделал.",
      oracleSource: "Оракул, «Матрица»",
      oracleBridge:
        "Когда действует агент, опасность в том, что «почему» всплывает уже после последствий. PythiaLabs делает «почему» читаемым заранее: стабильные stop-причины и воспроизводимый trace до вызова tool — чтобы человек понимал выбор, пока его ещё можно остановить.",
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
          a: "RBAC отвечает на «можно ли этому principal'у?». PythiaLabs отвечает на «должно ли это конкретное действие произойти с учётом текущих доказательств, их свежести и риска?». Это дополняет policy engine'ы вроде OPA: статические правила — там, decision-time проверки с evidence — в шлюзе.",
        },
        {
          q: "Как интегрировать PythiaLabs с моими агентами?",
          a: "Начните с Elixir-библиотеки в этом репозитории: подключите оркестратор к evaluator'у до выполнения инструментов, передавайте структурированные предложения и снимки контекста на момент решения, сохраняйте или передайте trace и при необходимости экспорт SHA-256 для ревьюеров. Следуйте README «Reviewer quickstart» (`mix test` и скрипты `examples/*_showcase.exs`) и сверяйте stdout с файлами `docs/*_expected_output.md`.",
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
      primary: "Запросить ранний доступ",
      demo: "Смотреть демо",
      secondary: "Открыть GitHub",
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
    ogLocale: "zh_CN",
    langLabel: "中文",
    meta: {
      title: "面向 AI Agent 的执行前安全门控 — PythiaLabs",
      description:
        "面向 AI 与 agentic 系统的开源执行前门控：在工具运行前给出 ALLOW、BLOCK 或 ESCALATE。确定性检查、可重放轨迹、审计友好证据——自托管 Elixir 库，Apache-2.0。",
      keywords:
        "AI Agent 安全, 执行前门控, agentic AI, AI 治理, ALLOW BLOCK ESCALATE, 确定性策略门控, 审计轨迹, 开源 AI 安全, Apache-2.0, Elixir, OPA RBAC, DevOps Agent, 金融科技 AI 风险, Web3 金库治理",
      ogImageAlt: "PythiaLabs — AI Agent 执行前安全门控：先验证再执行",
    },
    nav: {
      problem: "问题",
      idea: "核心理念",
      solution: "工作原理",
      integration: "集成",
      quickstart: "快速上手",
      fit: "适合谁",
      pilot: "试点",
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
        "在 Agent 运行破坏性工具之前，门控先返回 ALLOW、BLOCK 或 ESCALATE——确定性、可重放，跑在你自己的基础设施上。",
      body: "代码、基础设施、银行、治理：当 Agent 要行动时，PythiaLabs 先评估提案与证据，而不是聊天记录本身。",
      tagline: "先验证再执行。审阅者可重放的证据。",
      starsAlt: "GitHub 星标",
    },
    trustStrip: ["100% 开源", "Apache-2.0", "确定性 — 门控路径中无 LLM 调用", "可自托管", "无遥测"],
    cta: {
      primary: "申请早期访问",
      demo: "观看演示",
      secondary: "查看 GitHub",
      pilot: "申请试点合作",
      contact: "联系",
    },
    heroStats: {
      ariaLabel: "仓库一览",
      showcases: "个确定性本地 showcase 脚本",
      tests: "个 Ex 测试文件覆盖门控与证据",
      licenseLine: "许可证",
      licenseValue: "Apache-2.0",
      llmLine: "门控路径中的 LLM 调用",
    },
    ifYou: {
      title: "如果这就是你的团队，PythiaLabs 为你而建",
      items: [
        "你运行（或计划运行）能改动生产、资金或治理的 Agent——不仅是聊天。",
        "事后日志不够：你需要在工具执行前就留下决策记录。",
        "仅有 RBAC 与粗粒度策略不够回答「在当前证据下，这一具体操作此刻是否应执行？」",
        "安全与审查需要每次都可重放的同一类产物——而不是线程截图。",
      ],
    },
    quickstart: {
      title: "一次上手就能跑通门控",
      intro: "无需信用卡与 SaaS。克隆、测试、运行 showcase，再按同样方式接入编排器。",
      steps: [
        {
          name: "克隆并安装依赖",
          desc: "`git clone` 仓库后执行 `mix deps.get`（与 CI 相同工具链）。",
        },
        {
          name: "跑通测试",
          desc: "运行 `mix test`——门控需遵守的契约。",
        },
        {
          name: "运行 showcase",
          desc: "执行 `mix run examples/agent_infra_action_showcase.exs`（或 banking / Web3 showcase），将标准输出与 `docs/*_expected_output.md` 对照。",
        },
        {
          name: "在工具前调用评估器",
          desc: "在 Agent runner 中传入结构化提案与决策时证据；若结果不是 ALLOW（或按策略处理 ESCALATE）则阻止执行。",
        },
      ],
    },
    midCta: {
      line: "观看讲解视频、在本地运行仓库，或启动试点对话——你的栈，你的基础设施。",
    },
    videoBlock: {
      eyebrow: "为什么这件事重要",
      title: "这个 AI Agent 行动应该被执行吗？",
      body: "Agent 能行动时，糟糕的回答就会变成事故。PythiaLabs 在不可逆动作之前检查权限、证据新鲜度、风险与可重放性——然后允许、阻止或升级到人。",
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
      punchline: "但大多数系统仍在执行后才校验结果。这就像在大楼烧毁后才安装火警警报。",
    },
    bigIdea: {
      eyebrow: "核心理念",
      title: "在 Agent 行动之前，必须证明该行动是被允许的",
      lead: "PythiaLabs 提出一个关键问题：",
      quote: "“这个 AI Agent 行动应该被执行吗？”",
      not: ["不是“答案听起来聪明吗？”", "不是“模型有信心吗？”", "不是“推理听起来对吗？”"],
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
      checks: ["授权", "证据新鲜度", "决策时上下文", "权限边界", "凭据", "恢复假设", "行动风险"],
      returnsTitle: "返回",
    },
    artifact: {
      title: "可审查的决策产物",
      technicalSummary: "工程细节：规范化编码与摘要",
      introPlain:
        "每次决策都会生成结构化证据：结果、停止原因、各检查项与一个审阅者可重放的轨迹。审计者读到的与你在 CI 里快照的是同一类产物——不是聊天截图。",
      introTechnical:
        "导出采用规范化编码（`pythia.canonical_export.v1`）与 SHA-256：同一评估快照总是得到相同的十六进制摘要；在 CI 中重复导出可发现漂移。",
    },
    pilotOutcome: {
      title: "一次试点周能交付什么",
      intro: "这是开源 MVP，不是魔法。但聚焦的试点仍能给团队具体、可审查的产出：",
      items: [
        "将一到两个高风险 Agent 流程映射为结构化提案与决策时证据。",
        "在工具执行前得到带稳定停止原因的 ALLOW / BLOCK / ESCALATE。",
        "可重放的轨迹以及可选的 SHA-256 摘要，便于审阅在 CI 中对比。",
        "与安全、合规共享同一套语言——争论更少，升级路径更清晰。",
      ],
      footnote: "范围与节奏取决于你的栈。请附场景邮件联系，我们会优先考虑认真的设计合作伙伴。",
    },
    integration: {
      title: "如何集成（当前形态）",
      intro:
        "PythiaLabs 以 Apache-2.0 授权的 Elixir 库交付——不是托管控制平面。Agent 与工具仍归你所有；门控是编排器在不可逆动作之前调用的库边界。",
      items: [
        {
          name: "在你系统中的挂载点",
          desc: "从 Agent runner 或轻量 sidecar 服务链接该库。不强制 SaaS、不强制遥测、无回连——一切跑在你的基础设施上。",
        },
        {
          name: "结构化提案 → 确定性评估",
          desc: "传入类型化的拟议行动以及决策时证据（审批、策略状态、新鲜度标记、环境上下文）。引擎返回 ALLOW / BLOCK / ESCALATE 与可重放轨迹；showcase 还可导出 SHA-256 证据供审计交接。",
        },
        {
          name: "与 RBAC 与策略引擎互补",
          desc: "OPA 与 RBAC 回答“主体在一般情况下是否被允许？”。门控回答“在当前证据、新鲜度与风险下，这一具体行动是否应当现在执行？”——通常可置于现有策略层之前或之后。",
        },
        {
          name: "可复现的摘要，而非主观感觉",
          desc: "评估器输出经规范化（见仓库中的 `pythia.canonical_export.v1`）并以 SHA-256 哈希。测试为接受态快照固定预期摘要并拒绝被篡改的 payload——这就是“相同输入 → 相同摘要”的具体含义。",
        },
      ],
      repoNote:
        "审阅者快速上手：克隆仓库，运行 `mix test`，再执行 `mix run examples/agent_infra_action_showcase.exs`（以及 banking / Web3 showcase）。面向审阅的预期输出见 `docs/*_expected_output.md`。",
    },
    valueStack: {
      title: "在危险的 Agent 行动发生之前阻止它",
      intro: "PythiaLabs 帮助团队构建不能仅凭“信任”交付的 AI Agent。你将获得：",
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
      vsTitle: "与常见方案的区别",
      vsItems: [
        {
          name: "仅靠提示词与护栏",
          desc: "对高风险工具而言，模型指令不是边界。门控是可测试的确定性代码与稳定停止原因——不是提示文本。",
        },
        {
          name: "仅有 RBAC / 粗粒度 IAM",
          desc: "静态角色无法表达「此刻、在此证据快照、在此风险下」。门控消费决策时上下文与证据新鲜度。",
        },
        {
          name: "诸如 OPA 的策略引擎",
          desc: "OPA 回答你编写的授权规则。PythiaLabs 聚焦 Agent 行动提案、可重放轨迹与审阅用摘要导出——互补而非重复。",
        },
        {
          name: "事后监控",
          desc: "执行后的指标无法撤销转账、删除或治理投票。控制点在执行之前。",
        },
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
      oracleEyebrow: "与名字的共鸣",
      oracleQuote: "你不是来这里做选择的——你是来试图理解自己为何做出这个选择。",
      oracleSource: "先知，《黑客帝国》",
      oracleBridge:
        "当 Agent 真正行动时，风险在于「为何」往往在后果之后才浮现。PythiaLabs 让「为何」在工具执行前就可读：稳定的停止原因与可重放轨迹——在人类仍能叫停时理解这次选择。",
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
          a: "RBAC 问“这个 principal 是否被允许？”。PythiaLabs 问“在当前证据、新鲜度与风险下，这一具体行动是否应当现在执行？”。它与 OPA 等策略引擎互补：静态规则留在策略引擎，带证据的决策时检查放在门控。",
        },
        {
          q: "如何把 PythiaLabs 接入我的 Agent？",
          a: "从本仓库的 Elixir 库开始：在工具执行前让编排器调用评估器，传入结构化提案与决策时快照，并保存或转发轨迹与可选的 SHA-256 导出供审阅。按 README 的“Reviewer quickstart”运行 `mix test` 与 `examples/*_showcase.exs` 脚本，将标准输出与 `docs/*_expected_output.md` 对照。",
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
      primary: "申请早期访问",
      demo: "观看演示",
      secondary: "查看 GitHub",
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
