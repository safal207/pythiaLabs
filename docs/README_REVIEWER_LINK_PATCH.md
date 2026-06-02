# README Reviewer Link Patch

Status: safe patch note for the next README cleanup.

This note exists so the reviewer-first navigation can be added to the root `README.md` without changing product, demo, site, or workflow logic.

## Recommended insertion point

Insert this block immediately after the opening project description and before `## Positioning`.

## Block to add

```md
## Reviewer-first path

If you are reviewing PythiaLabs for a grant, fellowship, or collaboration:

1. Start here: [`docs/REVIEWER_FIRST_SCREEN.md`](docs/REVIEWER_FIRST_SCREEN.md)
2. Read the portfolio map: [`AI_SAFETY_PORTFOLIO.md`](AI_SAFETY_PORTFOLIO.md)
3. Run: `mix deps.get && mix test && make demo`
4. Read limitations: [`docs/NON_CLAIMS.md`](docs/NON_CLAIMS.md)

PythiaLabs is not a Web3 transaction simulator, wallet tool, or generic memory product. It is a pre-execution evidence gate for high-risk AI-agent actions.
```

## Why this helps

The current README already contains the right materials, but reviewers have to scan for them. This block makes the reviewer journey visible in the first screen.

## Scope

Docs-only.

Do not change:

- demo/product logic;
- site/build files;
- workflows;
- generated artifacts;
- pricing or pilot text.
