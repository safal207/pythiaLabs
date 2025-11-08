defmodule Pythia.ExecutorTest do
  use ExUnit.Case, async: true
  alias Pythia.Executor

  setup do
    {:ok, executor: Executor.new()}
  end

  describe "new/0" do
    test "creates executor struct" do
      exec = Executor.new()
      assert %Executor{} = exec
    end
  end

  describe "apply_proposal/3 - :noop" do
    test "returns unchanged string", %{executor: exec} do
      {result, meta} = Executor.apply_proposal(exec, "hello", {:noop})
      assert result == "hello"
      assert meta == %{op: :noop}
    end
  end

  describe "apply_proposal/3 - :insert" do
    test "inserts character at beginning", %{executor: exec} do
      {result, meta} = Executor.apply_proposal(exec, "ello", {:insert, "h", 0})
      assert result == "hello"
      assert meta == %{op: :insert, ch: "h", pos: 0}
    end

    test "inserts character in middle", %{executor: exec} do
      {result, meta} = Executor.apply_proposal(exec, "helo", {:insert, "l", 3})
      assert result == "hello"
      assert meta == %{op: :insert, ch: "l", pos: 3}
    end

    test "inserts character at end", %{executor: exec} do
      {result, meta} = Executor.apply_proposal(exec, "hell", {:insert, "o", 4})
      assert result == "hello"
      assert meta == %{op: :insert, ch: "o", pos: 4}
    end

    test "inserts into empty string", %{executor: exec} do
      {result, _meta} = Executor.apply_proposal(exec, "", {:insert, "x", 0})
      assert result == "x"
    end
  end

  describe "apply_proposal/3 - :delete" do
    test "deletes character at beginning", %{executor: exec} do
      {result, meta} = Executor.apply_proposal(exec, "xhello", {:delete, 0})
      assert result == "hello"
      assert meta == %{op: :delete, pos: 0}
    end

    test "deletes character in middle", %{executor: exec} do
      {result, meta} = Executor.apply_proposal(exec, "helxlo", {:delete, 3})
      assert result == "hello"
      assert meta == %{op: :delete, pos: 3}
    end

    test "deletes character at end", %{executor: exec} do
      {result, _meta} = Executor.apply_proposal(exec, "hellox", {:delete, 5})
      assert result == "hello"
    end

    test "deletes from single character string", %{executor: exec} do
      {result, _meta} = Executor.apply_proposal(exec, "x", {:delete, 0})
      assert result == ""
    end

    test "delete at end of string returns unchanged", %{executor: exec} do
      {result, _meta} = Executor.apply_proposal(exec, "hello", {:delete, 5})
      assert result == "hello"
    end
  end

  describe "apply_proposal/3 - :replace" do
    test "replaces character at beginning", %{executor: exec} do
      {result, meta} = Executor.apply_proposal(exec, "jello", {:replace, "h", 0})
      assert result == "hello"
      assert meta == %{op: :replace, ch: "h", pos: 0}
    end

    test "replaces character in middle", %{executor: exec} do
      {result, meta} = Executor.apply_proposal(exec, "hezlo", {:replace, "l", 2})
      assert result == "hello"
      assert meta == %{op: :replace, ch: "l", pos: 2}
    end

    test "replaces character at end", %{executor: exec} do
      {result, _meta} = Executor.apply_proposal(exec, "hellx", {:replace, "o", 4})
      assert result == "hello"
    end

    test "replace at end position appends character", %{executor: exec} do
      {result, _meta} = Executor.apply_proposal(exec, "hell", {:replace, "o", 4})
      assert result == "hello"
    end
  end

  describe "apply_proposal/3 - unicode handling" do
    test "handles unicode insertion", %{executor: exec} do
      {result, _meta} = Executor.apply_proposal(exec, "caf", {:insert, "é", 3})
      assert result == "café"
    end

    test "handles unicode deletion", %{executor: exec} do
      {result, _meta} = Executor.apply_proposal(exec, "café", {:delete, 3})
      assert result == "caf"
    end

    test "handles unicode replacement", %{executor: exec} do
      {result, _meta} = Executor.apply_proposal(exec, "cafe", {:replace, "é", 3})
      assert result == "café"
    end

    test "handles emoji", %{executor: exec} do
      {result, _meta} = Executor.apply_proposal(exec, "hello", {:insert, "👋", 0})
      assert result == "👋hello"
    end
  end

  describe "score/3" do
    test "returns 0 for identical strings", %{executor: exec} do
      assert Executor.score(exec, "hello", "hello") == 0
      assert Executor.score(exec, "", "") == 0
    end

    test "returns edit distance for different strings", %{executor: exec} do
      assert Executor.score(exec, "kitten", "sitting") == 3
      assert Executor.score(exec, "hello", "world") == 4
    end

    test "returns string length when comparing with empty", %{executor: exec} do
      assert Executor.score(exec, "", "hello") == 5
      assert Executor.score(exec, "world", "") == 5
    end
  end

  describe "integration - edit sequence" do
    test "can transform string through sequence of edits", %{executor: exec} do
      # kitten → sitten → sittin → sitting
      current = "kitten"

      {current, _} = Executor.apply_proposal(exec, current, {:replace, "s", 0})
      assert current == "sitten"

      {current, _} = Executor.apply_proposal(exec, current, {:replace, "i", 4})
      assert current == "sittin"

      {current, _} = Executor.apply_proposal(exec, current, {:insert, "g", 6})
      assert current == "sitting"

      assert Executor.score(exec, current, "sitting") == 0
    end
  end
end
