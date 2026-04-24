defmodule Pythia.GoldenRefineTest do
  use ExUnit.Case, async: true

  alias Pythia

  @cases [
    {"", "", 0},
    {"a", "", 1},
    {"", "abc", 3},
    {"abc", "abc", 0},
    {"kitten", "sitting", 3},
    {"book", "back", 2},
    {"flaw", "lawn", 2},
    {"gumbo", "gambol", 2},
    {"привет", "привёт", 1},
    {"mañana", "manana", 1}
  ]

  test "golden scenarios produce expected best score" do
    Enum.each(@cases, fn {source, target, expected_score} ->
      assert {:ok, result} =
               Pythia.refine_v1(%{
                 source: source,
                 target: target,
                 options: [max_steps: 64, threshold: 0, no_improve_limit: 8]
               })

      assert result.best.score == expected_score
      assert is_list(result.trace)
      assert result.stop_reason in [:threshold, :max_steps, :no_improve_limit]
    end)
  end

  test "invalid requests are rejected" do
    assert {:error, :invalid_request} = Pythia.refine_v1(%{source: "ok"})
    assert {:error, :invalid_request} = Pythia.refine_v1(:bad)
  end
end
