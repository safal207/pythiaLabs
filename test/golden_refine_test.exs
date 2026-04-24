defmodule Pythia.GoldenRefineTest do
  use ExUnit.Case, async: true

  alias Pythia

  @cases [
    {"", ""},
    {"a", ""},
    {"", "abc"},
    {"abc", "abc"},
    {"kitten", "sitting"},
    {"book", "back"},
    {"flaw", "lawn"},
    {"gumbo", "gambol"},
    {"привет", "привёт"},
    {"mañana", "manana"}
  ]

  test "golden scenarios converge to the target" do
    Enum.each(@cases, fn {source, target} ->
      assert {:ok, result} =
               Pythia.refine_v1(%{
                 source: source,
                 target: target,
                 options: [max_steps: 64, threshold: 0, no_improve_limit: 8]
               })

      assert result.best.candidate == target
      assert result.best.score == 0
      assert result.stop_reason == :threshold
      assert is_list(result.trace)
    end)
  end

  test "invalid requests are rejected" do
    assert {:error, :invalid_request} = Pythia.refine_v1(%{source: "ok"})
    assert {:error, :invalid_request} = Pythia.refine_v1(:bad)
  end

  test "non-keyword options are rejected" do
    assert {:error, :invalid_request} =
             Pythia.refine_v1(%{source: "a", target: "b", options: %{max_steps: 10}})

    assert {:error, :invalid_request} =
             Pythia.refine_v1(%{source: "a", target: "b", options: "nope"})
  end
end
