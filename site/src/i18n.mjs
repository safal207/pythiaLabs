export const locales = {
  en: {
    htmlLang: "en",
    langLabel: "EN",
    meta: {
      title: "Evidence Gates for AI-Agent Actions — PythiaLabs",
      description:
        "Open-source policy engine for AI agents. Returns ALLOW / BLOCK / ESCALATE for high-risk actions before execution, with replayable evidence artifacts.",
    },
    nav: {
      problem: "Problem",
      solution: "How it works",
      useCases: "Use cases",
      demo: "Demo",
      faq: "FAQ",
      contact: "Contact",
    },
    skipLink: "Skip to content",
    hero: {
      eyebrow: "Open-source · Deterministic · Pre-execution",
      headline: "Stop AI agents from running risky actions — before they happen.",
      subtitle:
        "PythiaLabs is an open-source policy engine that returns ALLOW / BLOCK / ESCALATE for high-risk agent actions, with replayable evidence artifacts your reviewers can audit.",
      audience:
        "For teams running AI coding agents, infrastructure automation, FinTech / RegTech, and Web3 governance.",
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
      primary: "Watch 2-min demo",
      secondary: "View on GitHub",
      pilot: "Apply as pilot partner",
      contact: "Contact",
    },
    problem: {
      title: "AI agents are moving from text to action",
      p1: "Coding agents merge PRs. Infra agents call cloud APIs. Treasury agents prepare on-chain transactions. Compliance agents draft regulatory filings.",
      p2: "Most teams still lack a clear pre-execution checkpoint that can answer one question:",
      quote: "“Should this action be allowed to happen?”",
    },
    solution: {
      title: "How PythiaLabs works",
      intro:
        "PythiaLabs evaluates a proposed action before execution and returns a decision plus an inspectable evidence artifact.",
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
      title: "What you get with PythiaLabs",
      items: [
        "Deterministic policy engine — same input, same decision, every time",
        "7 pre-execution checks covering auth, evidence, context, permissions, credentials, recovery, and risk",
        "JSON evidence artifacts your reviewers and auditors actually read",
        "Replayable traces with stable stop reasons and tamper-checkable digests",
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
    demo: {
      title: "See it in action",
      caption: "2-minute walkthrough of a deterministic local demo.",
      fallback: "Watch the demo on YouTube",
    },
    useCases: {
      title: "Where PythiaLabs fits",
      items: [
        {
          name: "AI coding agents",
          desc: "Block PRs that touch prod secrets or skip evidence-freshness checks.",
        },
        {
          name: "Infrastructure automation",
          desc: "Gate `terraform apply`, IAM changes, and production deploys.",
        },
        {
          name: "FinTech / RegTech",
          desc: "Pre-execution checks on payment, KYC, and compliance flows.",
        },
        {
          name: "Web3 treasury governance",
          desc: "Verify multi-sig proposals and decision-time context before broadcast.",
        },
        {
          name: "Public-sector AI",
          desc: "Auditable decisions with replay traces for transparency reviews.",
        },
        {
          name: "Enterprise AI assurance",
          desc: "Evidence artifacts your reviewers and auditors can read end-to-end.",
        },
      ],
    },
    faq: {
      title: "Frequently asked questions",
      items: [
        {
          q: "Is this production-ready?",
          a: "No. PythiaLabs is an open-source MVP with deterministic local demos. We are looking for pilot partners, not unqualified production deployments.",
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
          q: "Do you collect telemetry?",
          a: "No. There is no phone-home in the gate. Your decisions stay on your infrastructure.",
        },
        {
          q: "How do I integrate it?",
          a: "The MVP runs locally with deterministic demos. Apply as a pilot partner and we'll work the integration with you.",
        },
      ],
    },
    founderLetter: {
      title: "Why I built this",
      body: "I spent 12 years in QA for fintech and infrastructure systems where the price of a wrong action is measured in audited regulatory filings. When I started watching AI agents do the same kind of work — modify code, call cloud APIs, prepare on-chain transactions — I kept asking the question that QA culture trained me to ask: where is the pre-execution checkpoint? PythiaLabs is my attempt to build it as deterministic, replayable, and reviewer-friendly as the systems I came from.",
      signoff: "— Aleksei Safonov, founder",
      videosTitle: "Hear it from the founder",
      videoLabels: {
        longForm: "▶ Long-form walkthrough",
        short1: "▶ Short — why this matters",
        short2: "▶ Short — how it works",
      },
    },
    finalCta: {
      eyebrow: "Limited pilot cohort",
      title: "We're picking a small number of design partners",
      text: "Working closely with early teams running agentic AI in code, infrastructure, finance, or governance. If that's you, we want to talk.",
      primary: "Apply as pilot partner",
      secondary: "Star on GitHub",
      reassurance: "Apache-2.0 · Self-hostable · No vendor lock-in · No credit card",
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
      label: "Open-source · Apache-2.0 · Pre-execution evidence gates",
      cta: "Apply as pilot partner",
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
      title: "Доказательные шлюзы для AI-агентов — PythiaLabs",
      description:
        "Open-source policy engine для AI-агентов. Возвращает ALLOW / BLOCK / ESCALATE для рискованных действий до выполнения, с воспроизводимыми артефактами доказательств.",
    },
    nav: {
      problem: "Проблема",
      solution: "Как работает",
      useCases: "Применение",
      demo: "Демо",
      faq: "FAQ",
      contact: "Контакты",
    },
    skipLink: "К содержимому",
    hero: {
      eyebrow: "Open-source · Детерминированно · До выполнения",
      headline: "Останавливайте рискованные действия AI-агентов — до того, как они произойдут.",
      subtitle:
        "PythiaLabs — open-source policy engine, возвращающий ALLOW / BLOCK / ESCALATE для рискованных действий агентов, с воспроизводимыми артефактами доказательств для аудита.",
      audience:
        "Для команд с AI-агентами в коде, инфраструктуре, FinTech / RegTech и Web3-governance.",
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
      primary: "Посмотреть демо (2 мин)",
      secondary: "Открыть на GitHub",
      pilot: "Стать пилотным партнёром",
      contact: "Связаться",
    },
    problem: {
      title: "AI-агенты переходят от текста к действиям",
      p1: "Coding-агенты мерджат PR. Infra-агенты вызывают cloud API. Treasury-агенты готовят on-chain транзакции. Compliance-агенты составляют отчёты для регуляторов.",
      p2: "У большинства команд до сих пор нет чёткой точки контроля перед выполнением, которая отвечает на один вопрос:",
      quote: "«Должно ли это действие вообще произойти?»",
    },
    solution: {
      title: "Как работает PythiaLabs",
      intro:
        "PythiaLabs оценивает предлагаемое действие до выполнения и возвращает решение плюс проверяемый артефакт доказательств.",
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
      title: "Что вы получаете с PythiaLabs",
      items: [
        "Детерминированный policy engine — один и тот же вход даёт одно и то же решение",
        "7 проверок до выполнения: авторизация, свежесть доказательств, контекст, границы прав, учётные данные, восстановление, риск",
        "JSON-артефакты доказательств, которые реально читают ревьюеры и аудиторы",
        "Воспроизводимые трассы со стабильными stop-причинами и проверяемыми дайджестами",
        "Apache-2.0 — форкайте, запускайте на своей инфре, аудируйте каждую строку",
        "Никакой vendor lock-in: нет SaaS-зависимости, нет телеметрии, нет phone-home",
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
    demo: {
      title: "Посмотреть в действии",
      caption: "Двухминутный обзор детерминированного локального демо.",
      fallback: "Смотреть демо на YouTube",
    },
    useCases: {
      title: "Где применяется PythiaLabs",
      items: [
        {
          name: "AI-агенты для кода",
          desc: "Блокируйте PR, которые трогают prod-секреты или пропускают проверку свежести доказательств.",
        },
        {
          name: "Автоматизация инфраструктуры",
          desc: "Шлюзование `terraform apply`, изменений IAM и production-деплоев.",
        },
        {
          name: "FinTech / RegTech",
          desc: "Проверки до выполнения для платежей, KYC и комплаенс-сценариев.",
        },
        {
          name: "Web3-казначейство",
          desc: "Проверка multi-sig предложений и контекста на момент решения до broadcast.",
        },
        {
          name: "AI в госсекторе",
          desc: "Аудируемые решения с воспроизводимыми трассами для проверок прозрачности.",
        },
        {
          name: "Корпоративная AI-надёжность",
          desc: "Артефакты доказательств, которые ваши ревьюеры и аудиторы читают целиком.",
        },
      ],
    },
    faq: {
      title: "Частые вопросы",
      items: [
        {
          q: "Это production-ready?",
          a: "Нет. PythiaLabs — open-source MVP с детерминированными локальными демо. Мы ищем пилотных партнёров, а не бесконтрольные production-деплои.",
        },
        {
          q: "Чем это отличается от RBAC или OPA?",
          a: "RBAC отвечает на «можно ли этому principal'у?». PythiaLabs отвечает на «должно ли это конкретное действие произойти с учётом текущих доказательств, их свежести и риска?». Это дополняет policy engine'ы вроде OPA — их можно ставить до или после шлюза.",
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
          q: "Собираете ли вы телеметрию?",
          a: "Нет. В шлюзе нет phone-home. Ваши решения остаются у вас.",
        },
        {
          q: "Как интегрировать?",
          a: "MVP запускается локально с детерминированными демо. Подайтесь как пилотный партнёр — пройдём интеграцию вместе.",
        },
      ],
    },
    founderLetter: {
      title: "Почему я это сделал",
      body: "Я провёл 12 лет в QA финтеха и инфраструктуры — там, где цена неправильного действия измеряется в аудируемых отчётах для регулятора. Когда я начал смотреть, как AI-агенты делают ту же работу — меняют код, дёргают cloud API, готовят on-chain транзакции — я задавал тот же вопрос, которому меня научила QA-культура: где точка контроля перед выполнением? PythiaLabs — моя попытка сделать её такой же детерминированной, воспроизводимой и удобной для ревьюеров, как системы, из которых я пришёл.",
      signoff: "— Алексей Сафонов, основатель",
      videosTitle: "Послушать основателя",
      videoLabels: {
        longForm: "▶ Полный обзор",
        short1: "▶ Шортс — зачем это нужно",
        short2: "▶ Шортс — как это работает",
      },
    },
    finalCta: {
      eyebrow: "Ограниченная пилотная когорта",
      title: "Мы берём несколько design partners",
      text: "Работаем вплотную с ранними командами, запускающими agentic AI в коде, инфраструктуре, финансах или governance. Если это вы — давайте поговорим.",
      primary: "Стать пилотным партнёром",
      secondary: "Поставить звезду на GitHub",
      reassurance: "Apache-2.0 · Self-hosted · Без vendor lock-in · Без карточки",
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
      label: "Open-source · Apache-2.0 · Доказательные шлюзы до выполнения",
      cta: "Стать пилотным партнёром",
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
      title: "面向 AI Agent 行动的证据门控 — PythiaLabs",
      description:
        "面向 AI Agent 的开源策略引擎。在执行前返回 ALLOW / BLOCK / ESCALATE，并产出可重放的证据产物。",
    },
    nav: {
      problem: "问题",
      solution: "工作原理",
      useCases: "应用场景",
      demo: "演示",
      faq: "常见问题",
      contact: "联系",
    },
    skipLink: "跳到内容",
    hero: {
      eyebrow: "开源 · 确定性 · 执行前",
      headline: "在 AI Agent 执行风险操作之前阻止它们。",
      subtitle:
        "PythiaLabs 是一个开源策略引擎：在执行前返回 ALLOW / BLOCK / ESCALATE，并产出可被审查的证据产物。",
      audience:
        "面向运行 AI 编码代理、基础设施自动化、FinTech / RegTech 与 Web3 治理的团队。",
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
      primary: "观看 2 分钟演示",
      secondary: "查看 GitHub",
      pilot: "申请试点合作",
      contact: "联系",
    },
    problem: {
      title: "AI Agent 正从文本走向行动",
      p1: "编码代理合并 PR；基础设施代理调用云 API；金库代理准备链上交易；合规代理起草监管报告。",
      p2: "但大多数团队仍缺少一个能回答以下问题的执行前检查点：",
      quote: "“这个行动应该被允许发生吗？”",
    },
    solution: {
      title: "PythiaLabs 的工作原理",
      intro: "PythiaLabs 在执行前评估拟议行动，并返回一个决策与可审查的证据产物。",
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
      title: "PythiaLabs 为你提供的能力",
      items: [
        "确定性策略引擎 — 同样的输入永远得到同样的决策",
        "7 项执行前检查：授权、证据新鲜度、上下文、权限边界、凭据、恢复、风险",
        "审查者与审计者真正会读的 JSON 证据产物",
        "带稳定停止原因与可校验摘要的可重放轨迹",
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
    demo: {
      title: "实际效果演示",
      caption: "2 分钟的确定性本地演示。",
      fallback: "在 YouTube 观看演示",
    },
    useCases: {
      title: "PythiaLabs 的适用场景",
      items: [
        {
          name: "AI 编码代理",
          desc: "阻止触及生产密钥或跳过证据新鲜度检查的 PR。",
        },
        {
          name: "基础设施自动化",
          desc: "对 `terraform apply`、IAM 变更与生产部署做门控。",
        },
        {
          name: "FinTech / RegTech",
          desc: "对支付、KYC 与合规流程做执行前检查。",
        },
        {
          name: "Web3 国库治理",
          desc: "在广播前验证多签提案与决策时上下文。",
        },
        {
          name: "公共部门 AI",
          desc: "用可重放轨迹支撑透明度审查的可审计决策。",
        },
        {
          name: "企业 AI 保障",
          desc: "可被审查者与审计者完整阅读的证据产物。",
        },
      ],
    },
    faq: {
      title: "常见问题",
      items: [
        {
          q: "是否生产可用？",
          a: "尚未。PythiaLabs 是带有确定性本地演示的开源 MVP。我们寻找的是试点伙伴，而不是无条件的生产部署。",
        },
        {
          q: "与 RBAC 或 OPA 有何不同？",
          a: "RBAC 问“这个 principal 是否被允许？”。PythiaLabs 问“在当前证据、新鲜度与风险下，这个具体行动应该发生吗？”。它与 OPA 等策略引擎互补，可放在门控前或后。",
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
          q: "你们会收集遥测吗？",
          a: "不会。门控里没有任何回连。你的决策留在你的基础设施中。",
        },
        {
          q: "如何集成？",
          a: "MVP 可在本地以确定性演示方式运行。申请试点合作，我们与你一起完成集成。",
        },
      ],
    },
    founderLetter: {
      title: "我为什么做这件事",
      body: "我在金融科技与基础设施 QA 行业工作了 12 年——在那里，一次错误行动的代价以受审计的监管报告来衡量。当我开始观察 AI Agent 做同类工作——修改代码、调用云 API、准备链上交易——我总在问 QA 文化教给我的同一个问题：执行前的检查点在哪里？PythiaLabs 就是我把它做得像我来自的系统一样确定、可重放、对审查者友好的尝试。",
      signoff: "— Aleksei Safonov，创始人",
      videosTitle: "听创始人说",
      videoLabels: {
        longForm: "▶ 长视频讲解",
        short1: "▶ 短视频 — 为什么重要",
        short2: "▶ 短视频 — 工作原理",
      },
    },
    finalCta: {
      eyebrow: "试点名额有限",
      title: "我们正在挑选少量设计伙伴",
      text: "与在代码、基础设施、金融或治理中运行 agentic AI 的早期团队紧密合作。如果这是你 — 我们想聊聊。",
      primary: "申请试点合作",
      secondary: "在 GitHub 加星",
      reassurance: "Apache-2.0 · 可自托管 · 无供应商锁定 · 无需信用卡",
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
      label: "开源 · Apache-2.0 · 执行前证据门控",
      cta: "申请试点合作",
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
