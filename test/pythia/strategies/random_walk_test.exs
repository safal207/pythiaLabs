defmodule Pythia.Strategies.RandomWalkTest do
  use ExUnit.Case, async: true
  alias Pythia.Strategies.RandomWalk

  describe "init/1" do
    test "returns state with default options" do
      state = RandomWalk.init([])
      assert state.temperature == 1.0
      assert state.operations == [:insert, :delete, :replace]
    end

    test "accepts custom options" do
      state = RandomWalk.init(temperature: 0.5, operations: [:insert, :delete])
      assert state.temperature == 0.5
      assert state.operations == [:insert, :delete]
    end
  end

  describe "propose/3" do
    test "returns :noop for identical strings" do
      assert RandomWalk.propose("test", "test", %{}) == {:noop}
      assert RandomWalk.propose("", "", %{}) == {:noop}
    end

    test "returns valid proposal type" do
      proposal = RandomWalk.propose("abc", "xyz", %{})

      assert elem(proposal, 0) in [:insert, :delete, :replace, :noop]
    end

    test "insert proposal has valid structure" do
      # Run multiple times due to randomness
      proposals = for _ <- 1..10 do
        RandomWalk.propose("", "target", %{})
      end

      # All should be inserts (can't delete/replace empty string)
      for proposal <- proposals do
        assert match?({:insert, _, _}, proposal)
        {:insert, char, pos} = proposal
        assert is_binary(char)
        assert is_integer(pos)
        assert pos >= 0
      end
    end

    test "delete proposal has valid structure" do
      # Configure to only do deletes
      state = RandomWalk.init(operations: [:delete])

      proposals = for _ <- 1..10 do
        RandomWalk.propose("hello", "", %{strategy_state: state})
      end

      for proposal <- proposals do
        assert match?({:delete, _}, proposal) or proposal == {:noop}

        if match?({:delete, _}, proposal) do
          {:delete, pos} = proposal
          assert is_integer(pos)
          assert pos >= 0 and pos < 5
        end
      end
    end

    test "replace proposal has valid structure" do
      state = RandomWalk.init(operations: [:replace])

      proposals = for _ <- 1..10 do
        RandomWalk.propose("test", "best", %{strategy_state: state})
      end

      for proposal <- proposals do
        assert match?({:replace, _, _}, proposal)
        {:replace, char, pos} = proposal
        assert is_binary(char)
        assert is_integer(pos)
        assert pos >= 0 and pos < 4
      end
    end

    test "generates diverse proposals" do
      # Run many times and check we get different proposals
      proposals = for _ <- 1..20 do
        RandomWalk.propose("hello", "world", %{})
      end

      unique_proposals = Enum.uniq(proposals)

      # Should have some diversity (not all identical)
      assert length(unique_proposals) > 1
    end

    test "non-deterministic (different from greedy)" do
      # Random walk should sometimes differ from greedy approach
      greedy_like_count = for _ <- 1..20 do
        proposal = RandomWalk.propose("test", "best", %{})
        # Greedy would do: {:replace, "b", 0}
        if proposal == {:replace, "b", 0}, do: 1, else: 0
      end
      |> Enum.sum()

      # Not all proposals should match greedy
      assert greedy_like_count < 20
    end
  end
end
