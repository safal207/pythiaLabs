defmodule Pythia.Strategies.GreedyLCPTest do
  use ExUnit.Case, async: true
  alias Pythia.Strategies.GreedyLCP

  describe "init/1" do
    test "returns empty map" do
      assert GreedyLCP.init([]) == %{}
    end
  end

  describe "propose/3" do
    test "returns :noop for identical strings" do
      assert GreedyLCP.propose("hello", "hello", %{}) == {:noop}
      assert GreedyLCP.propose("", "", %{}) == {:noop}
    end

    test "proposes insert when target has more characters" do
      assert GreedyLCP.propose("hell", "hello", %{}) == {:insert, "o", 4}
      assert GreedyLCP.propose("", "a", %{}) == {:insert, "a", 0}
    end

    test "proposes delete when current has more characters" do
      assert GreedyLCP.propose("hello", "hell", %{}) == {:delete, 4}
      assert GreedyLCP.propose("a", "", %{}) == {:delete, 0}
    end

    test "proposes replace when characters differ" do
      assert GreedyLCP.propose("kitten", "sitting", %{}) == {:replace, "s", 0}
      assert GreedyLCP.propose("hello", "hallo", %{}) == {:replace, "a", 1}
    end

    test "handles common prefix correctly" do
      assert GreedyLCP.propose("testing", "tested", %{}) == {:replace, "e", 4}
      assert GreedyLCP.propose("prefix_ab", "prefix_cd", %{}) == {:replace, "c", 7}
    end

    test "deterministic results" do
      # Should always propose same action for same input
      proposal1 = GreedyLCP.propose("test", "best", %{})
      proposal2 = GreedyLCP.propose("test", "best", %{})
      assert proposal1 == proposal2
    end
  end
end
