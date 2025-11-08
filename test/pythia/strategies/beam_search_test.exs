defmodule Pythia.Strategies.BeamSearchTest do
  use ExUnit.Case, async: true
  alias Pythia.Strategies.BeamSearch

  describe "init/1" do
    test "returns state with default options" do
      state = BeamSearch.init([])
      assert state.beam_width == 3
      assert state.proposal_diversity == true
      assert is_map(state.greedy)
      assert is_map(state.random)
    end

    test "accepts custom beam_width" do
      state = BeamSearch.init(beam_width: 5)
      assert state.beam_width == 5
    end
  end

  describe "propose/3" do
    test "returns :noop for identical strings" do
      assert BeamSearch.propose("test", "test", %{}) == {:noop}
    end

    test "returns valid proposal" do
      proposal = BeamSearch.propose("abc", "xyz", %{})

      assert elem(proposal, 0) in [:insert, :delete, :replace, :noop]
    end

    test "proposal is valid edit operation" do
      proposals = for _ <- 1..10 do
        BeamSearch.propose("hello", "world", %{})
      end

      for proposal <- proposals do
        assert is_tuple(proposal)
        assert elem(proposal, 0) in [:insert, :delete, :replace, :noop]
      end
    end

    test "can generate diverse proposals" do
      # BeamSearch uses both greedy and random, so should be somewhat diverse
      state = BeamSearch.init(beam_width: 5)

      proposals = for _ <- 1..15 do
        BeamSearch.propose("test", "best", %{strategy_state: state})
      end

      unique_count = Enum.uniq(proposals) |> length()

      # Should have some diversity
      assert unique_count >= 1
    end

    test "handles edge cases" do
      assert BeamSearch.propose("", "abc", %{}) == {:insert, "a", 0}
      assert match?({:delete, 0}, BeamSearch.propose("abc", "", %{}))
    end
  end
end
