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
    finalCta: {
      title: "Looking for design partners",
      text: "We are talking to early teams running agentic AI workflows in code, infra, finance, and governance.",
      primary: "Apply as pilot partner",
      secondary: "Star on GitHub",
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
    finalCta: {
      title: "Ищем design partners",
      text: "Мы общаемся с командами, которые уже запускают agentic AI в коде, инфраструктуре, финансах и governance.",
      primary: "Стать пилотным партнёром",
      secondary: "Поставить звезду на GitHub",
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
      contact: "联系",
    },
    skipLink: "跳到内容",
    hero: {
      eyebrow: "开源 · 确定性 · 执行前",
      headline: "在 AI Agent 执行风险操作之前阻止它们。",
      subtitle:
        "PythiaLabs 是一个开源策略引擎：在执行前返回 ALLOW / BLOCK / ESCALATE，并产出可被审查的证据产物。",
      audience: "面向运行 AI 编码代理、基础设施自动化、FinTech / RegTech 与 Web3 治理的团队。",
      starsAlt: "GitHub 星标",
    },
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
      checks: ["授权", "证据新鲜度", "决策时上下文", "权限边界", "凭据", "恢复假设", "行动风险"],
      returnsTitle: "返回",
    },
    artifact: {
      title: "可审查的决策产物",
      intro:
        "每个决策都会生成 JSON 产物：稳定的停止原因、各项检查结果、可重放的 trace ID，以及可校验的摘要。这才是审查者和审计者真正会读的内容。",
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
    finalCta: {
      title: "正在寻找设计伙伴",
      text: "我们正在与在代码、基础设施、金融与治理中运行 agentic AI 的早期团队交流。",
      primary: "申请试点合作",
      secondary: "在 GitHub 加星",
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
