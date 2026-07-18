defmodule Pythia.LotusDocsContractTest do
  use ExUnit.Case, async: true

  @root Path.expand("..", __DIR__)
  @lotus Path.join(@root, "LOTUS.md")
  @template Path.join(@root, ".github/pull_request_template.md")
  @limitations Path.join(@root, "docs/LIMITATIONS.md")

  test "PR evidence is bound to exact head and changed context" do
    template = File.read!(@template)

    assert template =~ "Exact PR head SHA validated"
    assert template =~ "Validation command"
    assert template =~ "Validation was run or rerun after the most recent PR head change"
    assert template =~ "Evidence becomes stale"
    assert template =~ "evaluated inputs, policy, environment, authorization, credential, or recovery context changes"
  end

  test "ALLOW requires positive authorization and does not imply execution" do
    lotus = File.read!(@lotus)
    limitations = File.read!(@limitations)

    assert lotus =~ "Authorization before `ALLOW`"
    assert lotus =~ "absence of a blocking signal is not enough"
    assert lotus =~ "`ALLOW` is not execution"
    assert limitations =~ "`ALLOW` does not execute the proposed action"
    assert limitations =~ "does not create missing authorization"
  end

  test "uncertainty stays explicit and may escalate" do
    lotus = File.read!(@lotus)
    template = File.read!(@template)

    assert lotus =~ "Uncertainty stays explicit"
    assert lotus =~ "Pythia should produce `ESCALATE` rather than invent certainty"
    assert template =~ "Missing, stale, conflicting, or unavailable evidence remains visible"
    assert template =~ "not converted into confidence"
  end

  test "English and Russian contracts preserve the same core boundaries" do
    lotus = File.read!(@lotus)
    [english, russian] = String.split(lotus, "# Слой Лотоса Pythia", parts: 2)

    for phrase <- [
          "Evidence before verdict",
          "Exact state before evidence reuse",
          "Authorization before `ALLOW`",
          "Uncertainty stays explicit",
          "Judgment without execution",
          "Replayable reasons",
          "Human challengeability"
        ] do
      assert english =~ phrase
    end

    for phrase <- [
          "Доказательства до вердикта",
          "Точное состояние до повторного использования evidence",
          "Разрешение до `ALLOW`",
          "Неопределённость остаётся явной",
          "Суждение без исполнения",
          "Воспроизводимые причины",
          "Право человека оспорить"
        ] do
      assert russian =~ phrase
    end
  end

  test "Lotus remains a limitation contract rather than a safety overclaim" do
    limitations = File.read!(@limitations)

    assert limitations =~ "human-readable judgment contract, not a new enforcement claim"
    assert limitations =~ "do not upgrade the MVP into a certified safety system"
    assert limitations =~ "do not replace domain-specific authorization and execution controls"
  end
end
