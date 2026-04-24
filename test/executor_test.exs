defmodule Pythia.ExecutorTest do
  use ExUnit.Case, async: true

  alias Pythia.Executor

  setup do
    %{exec: Executor.new()}
  end

  test "insert/delete/replace proposals mutate string at position", %{exec: exec} do
    {inserted, _} = Executor.apply_proposal(exec, "abc", {:insert, "Z", 1})
    assert inserted == "aZbc"

    {deleted, _} = Executor.apply_proposal(exec, "abc", {:delete, 1})
    assert deleted == "ac"

    {replaced, _} = Executor.apply_proposal(exec, "abc", {:replace, "Z", 1})
    assert replaced == "aZc"
  end

  test "delete and replace gracefully handle out-of-range positions", %{exec: exec} do
    {deleted, _} = Executor.apply_proposal(exec, "abc", {:delete, 9})
    assert deleted == "abc"

    {replaced, _} = Executor.apply_proposal(exec, "abc", {:replace, "Z", 9})
    assert replaced == "abcZ"
  end
end
