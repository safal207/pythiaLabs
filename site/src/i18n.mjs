export const locales = {
  en: {
    htmlLang: "en",
    langLabel: "EN",
    meta: {
      title: "PythiaLabs — Evidence Gates for High-Risk AI-Agent Actions",
      description:
        "Open-source deterministic evidence gates for deciding whether high-risk AI-agent actions should be allowed, blocked, or escalated before execution.",
    },
    nav: {
      problem: "Problem",
      solution: "Solution",
      useCases: "Use cases",
      stage: "Stage",
      contact: "Contact",
    },
    hero: {
      eyebrow: "Open-source · Deterministic · Pre-execution",
      subtitle: "Evidence Gates for High-Risk AI-Agent Actions",
      text: "PythiaLabs helps teams decide whether AI-agent actions should be allowed, blocked, or escalated before execution.",
      support:
        "Built for agentic AI workflows involving code, infrastructure, credentials, finance, governance, and other high-risk operations.",
    },
    cta: {
      github: "View GitHub",
      demo: "Watch Demo",
      contact: "Contact Founder",
    },
    problem: {
      title: "AI Agents Are Moving From Text to Action",
      p1: "AI agents can now modify code, call tools, touch infrastructure, handle credentials, prepare financial workflows, and support governance decisions.",
      p2: "But most teams still lack a clear pre-execution checkpoint:",
      quote: "“Should this action be allowed to happen?”",
    },
    solution: {
      title: "Deterministic Evidence Gates Before Execution",
      intro:
        "PythiaLabs evaluates proposed high-risk actions before execution.",
      checksTitle: "It checks",
      checks: [
        "authorization",
        "evidence freshness",
        "decision-time context",
        "permission boundaries",
        "credentials",
        "recovery assumptions",
        "action risk",
      ],
      returnsTitle: "Then returns",
    },
    output: {
      title: "Inspectable Decision Artifacts",
      intro: "Every decision can produce reviewer-friendly artifacts:",
      items: [
        "Replayable traces",
        "Stable stop reasons",
        "JSON evidence artifacts",
        "Tamper-checkable digests",
        "Reviewer-facing reports",
      ],
    },
    useCases: {
      title: "Where PythiaLabs Can Help",
      items: [
        "AI coding agents",
        "Infrastructure automation",
        "FinTech / RegTech workflows",
        "Web3 treasury governance",
        "Public-sector AI workflows",
        "Enterprise AI assurance",
      ],
    },
    stage: {
      title: "Current Stage",
      p1: "PythiaLabs is an open-source MVP with deterministic local demos.",
      p2: "It is not currently a production enforcement system, regulatory compliance product, or certified safety framework.",
      p3: "We are looking for pilot partners, ecosystem support, accelerators, technical collaborators, and early reviewers.",
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
    footer: "© {year} PythiaLabs · Open-source MVP",
  },

  ru: {
    htmlLang: "ru",
    langLabel: "RU",
    meta: {
      title:
        "PythiaLabs — доказательные шлюзы для рискованных действий AI-агентов",
      description:
        "Открытые детерминированные доказательные шлюзы: решают, должно ли рискованное действие AI-агента быть разрешено, заблокировано или эскалировано до выполнения.",
    },
    nav: {
      problem: "Проблема",
      solution: "Решение",
      useCases: "Применение",
      stage: "Стадия",
      contact: "Контакты",
    },
    hero: {
      eyebrow: "Open-source · Детерминированно · До выполнения",
      subtitle:
        "Доказательные шлюзы для рискованных действий AI-агентов",
      text: "PythiaLabs помогает командам решать, должно ли действие AI-агента быть разрешено, заблокировано или эскалировано до выполнения.",
      support:
        "Создано для агентных AI-сценариев с кодом, инфраструктурой, учётными данными, финансами, governance и другими высокорисковыми операциями.",
    },
    cta: {
      github: "Открыть GitHub",
      demo: "Смотреть демо",
      contact: "Связаться с автором",
    },
    problem: {
      title: "AI-агенты переходят от текста к действиям",
      p1: "AI-агенты уже могут менять код, вызывать инструменты, влиять на инфраструктуру, работать с учётными данными, готовить финансовые операции и поддерживать governance-решения.",
      p2: "Но у большинства команд до сих пор нет чёткой точки контроля перед выполнением:",
      quote: "«Должно ли это действие вообще произойти?»",
    },
    solution: {
      title: "Детерминированные доказательные шлюзы перед выполнением",
      intro:
        "PythiaLabs оценивает предлагаемые рискованные действия до их выполнения.",
      checksTitle: "Что проверяется",
      checks: [
        "авторизация",
        "актуальность доказательств",
        "контекст на момент решения",
        "границы прав",
        "учётные данные",
        "предположения о восстановлении",
        "риск действия",
      ],
      returnsTitle: "Что возвращается",
    },
    output: {
      title: "Проверяемые артефакты решений",
      intro:
        "Каждое решение может выдавать удобные для аудита артефакты:",
      items: [
        "Воспроизводимые трассы",
        "Стабильные stop-причины",
        "JSON-артефакты доказательств",
        "Дайджесты с проверкой целостности",
        "Отчёты для ревьюеров",
      ],
    },
    useCases: {
      title: "Где PythiaLabs может помочь",
      items: [
        "AI-агенты для кода",
        "Автоматизация инфраструктуры",
        "FinTech / RegTech сценарии",
        "Web3-казначейство и governance",
        "AI в госсекторе",
        "Корпоративная AI-надёжность",
      ],
    },
    stage: {
      title: "Текущая стадия",
      p1: "PythiaLabs — open-source MVP с детерминированными локальными демо.",
      p2: "Это не production-система контроля действий, не комплаенс-продукт и не сертифицированный safety-фреймворк.",
      p3: "Ищем пилотных партнёров, поддержку экосистемы, акселераторы, технических сотрудников и ранних ревьюеров.",
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
    footer: "© {year} PythiaLabs · Open-source MVP",
  },

  zh: {
    htmlLang: "zh-Hans",
    langLabel: "中文",
    meta: {
      title: "PythiaLabs — 高风险 AI Agent 行动的证据门控",
      description:
        "开源、确定性的证据门控：在执行前判断高风险 AI Agent 行动应被允许、阻止或升级处理。",
    },
    nav: {
      problem: "问题",
      solution: "解决方案",
      useCases: "应用场景",
      stage: "阶段",
      contact: "联系",
    },
    hero: {
      eyebrow: "开源 · 确定性 · 执行前",
      subtitle: "高风险 AI Agent 行动的证据门控",
      text: "PythiaLabs 帮助团队在执行前决定 AI Agent 的行动应被允许、阻止还是升级处理。",
      support:
        "面向涉及代码、基础设施、凭据、金融、治理及其他高风险操作的 AI Agent 工作流。",
    },
    cta: {
      github: "访问 GitHub",
      demo: "观看演示",
      contact: "联系创始人",
    },
    problem: {
      title: "AI Agent 正从文本走向行动",
      p1: "AI Agent 现在能修改代码、调用工具、操作基础设施、处理凭据、准备金融流程并支持治理决策。",
      p2: "但大多数团队仍缺少清晰的执行前检查点：",
      quote: "“这个行动应该被允许发生吗？”",
    },
    solution: {
      title: "执行前的确定性证据门控",
      intro: "PythiaLabs 在执行前评估拟议的高风险行动。",
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
      returnsTitle: "返回结果",
    },
    output: {
      title: "可审查的决策产物",
      intro: "每次决策都可生成便于审查的产物：",
      items: [
        "可重放的轨迹",
        "稳定的停止原因",
        "JSON 证据产物",
        "可校验的摘要",
        "面向审查者的报告",
      ],
    },
    useCases: {
      title: "PythiaLabs 的应用场景",
      items: [
        "AI 编码代理",
        "基础设施自动化",
        "FinTech / RegTech 工作流",
        "Web3 国库治理",
        "公共部门 AI 工作流",
        "企业 AI 保障",
      ],
    },
    stage: {
      title: "当前阶段",
      p1: "PythiaLabs 是一个具有确定性本地演示的开源 MVP。",
      p2: "目前并非生产级执行系统、合规产品或经认证的安全框架。",
      p3: "我们正在寻找试点合作伙伴、生态支持、加速器、技术合作者与早期审查者。",
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
    footer: "© {year} PythiaLabs · 开源 MVP",
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
