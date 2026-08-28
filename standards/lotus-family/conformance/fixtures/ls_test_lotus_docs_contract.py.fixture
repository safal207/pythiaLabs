from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOTUS = ROOT / "LOTUS.md"
PR_TEMPLATE = ROOT / ".github" / "pull_request_template.md"


def test_pr_evidence_is_bound_to_exact_head() -> None:
    template = PR_TEMPLATE.read_text(encoding="utf-8")

    assert "Exact PR head SHA validated" in template
    assert "Validation command" in template
    assert "Validation was run or rerun after the most recent PR head change" in template
    assert "Evidence becomes stale" in template
    assert "apply to the exact SHA above" in template


def test_lotus_preserves_human_authority_in_both_languages() -> None:
    text = LOTUS.read_text(encoding="utf-8")
    english, russian = text.split("# Слой Лотоса", maxsplit=1)

    assert "has no ownership, approval, execution, delivery, or merge authority" in english
    assert "не имеет права собственности" in russian
    assert "одобрения" in russian
    assert "исполнения" in russian
    assert "доставки или merge" in russian


def test_english_and_russian_contracts_keep_the_seven_core_petals() -> None:
    text = LOTUS.read_text(encoding="utf-8")
    english, russian = text.split("# Слой Лотоса", maxsplit=1)

    english_petals = (
        "Clarity from complexity",
        "Evidence before confidence",
        "Causes before symptoms",
        "Memory without authority",
        "Consent before durable memory",
        "Repair before judgment",
        "Human authorship at the center",
    )
    russian_petals = (
        "Ясность из сложности",
        "Доказательства до уверенности",
        "Причины до симптомов",
        "Память без власти",
        "Согласие до долговременной памяти",
        "Исправление до осуждения",
        "Человек остаётся автором",
    )

    for phrase in english_petals:
        assert phrase in english
    for phrase in russian_petals:
        assert phrase in russian


def test_lotus_remains_guidance_not_runtime_authority() -> None:
    text = LOTUS.read_text(encoding="utf-8")

    assert "not a runtime component, a permission system, or an autonomous actor" in text
    assert "not a personality cult, hidden authority, mystical proof" in text
    assert "не runtime-компонент, не система разрешений и не автономный агент" in text
    assert "не культ личности, не скрытая власть, не мистическое доказательство" in text
