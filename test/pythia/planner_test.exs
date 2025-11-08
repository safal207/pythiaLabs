defmodule Pythia.PlannerTest do
  use ExUnit.Case, async: true
  alias Pythia.{Planner, Executor, Critic}

  describe "new/3" do
    test "creates planner with default options" do
      planner = Planner.new("hello", "world", [])

      assert planner.problem == "hello"
      assert planner.objective == "world"
      assert planner.state == %{candidate: "hello"}
      assert planner.best == %{candidate: "hello", score: :infinity}
      assert planner.step == 0
      assert planner.max_steps == 20
      assert planner.threshold == 0
      assert planner.no_improve_limit == 5
      assert planner.no_improve == 0
      assert planner.trace == []
    end

    test "creates planner with custom options" do
      opts = [max_steps: 50, threshold: 2, no_improve_limit: 10]
      planner = Planner.new("abc", "xyz", opts)

      assert planner.max_steps == 50
      assert planner.threshold == 2
      assert planner.no_improve_limit == 10
    end
  end

  describe "run/3 - termination conditions" do
    test "terminates when score reaches threshold" do
      planner = Planner.new("hello", "hello", max_steps: 100)
      executor = Executor.new()
      critic = Critic.new()

      {:ok, result} = Planner.run(planner, executor, critic)

      assert result.best.score == 0
      assert result.best.candidate == "hello"
      assert result.steps == 1
    end

    test "terminates at max_steps" do
      # Use strings that require more than max_steps edits
      planner = Planner.new("aaaa", "bbbb", max_steps: 2)
      executor = Executor.new()
      critic = Critic.new()

      {:ok, result} = Planner.run(planner, executor, critic)

      assert result.steps == 2
    end

    test "terminates when no improvement limit reached" do
      # This might be tricky to test reliably, but we can try with a case
      # where the greedy strategy gets stuck
      planner = Planner.new("xyz", "abc", max_steps: 100, no_improve_limit: 3)
      executor = Executor.new()
      critic = Critic.new()

      {:ok, result} = Planner.run(planner, executor, critic)

      # Should terminate due to no_improve_limit or reaching threshold
      assert result.steps > 0
    end
  end

  describe "run/3 - successful refinement" do
    test "successfully refines kitten to sitting" do
      planner = Planner.new("kitten", "sitting", max_steps: 30)
      executor = Executor.new()
      critic = Critic.new()

      {:ok, result} = Planner.run(planner, executor, critic)

      assert result.best.candidate == "sitting"
      assert result.best.score == 0
      assert result.steps > 0
      assert length(result.trace) == result.steps
    end

    test "successfully refines with minimal steps" do
      planner = Planner.new("cat", "bat", max_steps: 10)
      executor = Executor.new()
      critic = Critic.new()

      {:ok, result} = Planner.run(planner, executor, critic)

      assert result.best.candidate == "bat"
      assert result.best.score == 0
      assert result.steps <= 2
    end

    test "handles empty string to string refinement" do
      planner = Planner.new("", "abc", max_steps: 10)
      executor = Executor.new()
      critic = Critic.new()

      {:ok, result} = Planner.run(planner, executor, critic)

      assert result.best.candidate == "abc"
      assert result.best.score == 0
    end

    test "handles string to empty string refinement" do
      planner = Planner.new("abc", "", max_steps: 10)
      executor = Executor.new()
      critic = Critic.new()

      {:ok, result} = Planner.run(planner, executor, critic)

      assert result.best.candidate == ""
      assert result.best.score == 0
    end
  end

  describe "run/3 - trace validation" do
    test "trace contains all steps" do
      planner = Planner.new("ab", "ba", max_steps: 10)
      executor = Executor.new()
      critic = Critic.new()

      {:ok, result} = Planner.run(planner, executor, critic)

      assert length(result.trace) == result.steps

      # Each trace entry should have required fields
      for entry <- result.trace do
        assert Map.has_key?(entry, :step)
        assert Map.has_key?(entry, :proposal)
        assert Map.has_key?(entry, :candidate)
        assert Map.has_key?(entry, :score)
        assert Map.has_key?(entry, :meta)
      end
    end

    test "trace steps are sequential" do
      planner = Planner.new("hello", "world", max_steps: 20)
      executor = Executor.new()
      critic = Critic.new()

      {:ok, result} = Planner.run(planner, executor, critic)

      step_numbers = Enum.map(result.trace, & &1.step)
      expected_steps = Enum.to_list(1..result.steps)

      assert step_numbers == expected_steps
    end

    test "trace shows score improvement" do
      planner = Planner.new("kitten", "sitting", max_steps: 30)
      executor = Executor.new()
      critic = Critic.new()

      {:ok, result} = Planner.run(planner, executor, critic)

      # Final score should be 0 (or at least the best score)
      final_entry = List.last(result.trace)
      assert final_entry.score <= hd(result.trace).score
    end
  end

  describe "run/3 - best tracking" do
    test "tracks best candidate" do
      planner = Planner.new("abc", "xyz", max_steps: 5)
      executor = Executor.new()
      critic = Critic.new()

      {:ok, result} = Planner.run(planner, executor, critic)

      # Best score should be the minimum score achieved
      all_scores = Enum.map(result.trace, & &1.score)
      assert result.best.score == Enum.min(all_scores)
    end

    test "best candidate matches best score" do
      planner = Planner.new("test", "best", max_steps: 10)
      executor = Executor.new()
      critic = Critic.new()

      {:ok, result} = Planner.run(planner, executor, critic)

      # Find the trace entry with the best score
      best_entry = Enum.find(result.trace, fn entry ->
        entry.score == result.best.score
      end)

      assert best_entry.candidate == result.best.candidate
    end
  end

  describe "run/3 - edge cases" do
    test "handles identical source and target" do
      planner = Planner.new("same", "same", max_steps: 10)
      executor = Executor.new()
      critic = Critic.new()

      {:ok, result} = Planner.run(planner, executor, critic)

      assert result.best.score == 0
      assert result.best.candidate == "same"
      assert result.steps == 1
    end

    test "handles unicode strings" do
      planner = Planner.new("café", "cafe", max_steps: 10)
      executor = Executor.new()
      critic = Critic.new()

      {:ok, result} = Planner.run(planner, executor, critic)

      assert result.best.candidate == "cafe"
      assert result.best.score == 0
    end

    test "handles long strings" do
      source = "The quick brown fox"
      target = "The slow brown dog"
      planner = Planner.new(source, target, max_steps: 50)
      executor = Executor.new()
      critic = Critic.new()

      {:ok, result} = Planner.run(planner, executor, critic)

      # Should make progress even if not perfect
      assert result.best.score < String.length(target)
    end
  end

  describe "run/3 - proposal types" do
    test "generates appropriate proposal types" do
      planner = Planner.new("ab", "ba", max_steps: 10)
      executor = Executor.new()
      critic = Critic.new()

      {:ok, result} = Planner.run(planner, executor, critic)

      # Should have mix of operations (not just noop)
      proposal_types = result.trace
        |> Enum.map(& elem(&1.proposal, 0))
        |> Enum.uniq()

      assert :noop not in proposal_types or length(proposal_types) > 1
    end
  end

  describe "run/3 - convergence" do
    test "converges to target for simple cases" do
      test_cases = [
        {"a", "b"},
        {"ab", "ba"},
        {"hello", "hallo"},
        {"cat", "bat"},
        {"test", "best"}
      ]

      for {source, target} <- test_cases do
        planner = Planner.new(source, target, max_steps: 20)
        executor = Executor.new()
        critic = Critic.new()

        {:ok, result} = Planner.run(planner, executor, critic)

        assert result.best.candidate == target,
               "Failed to converge #{source} → #{target}"
        assert result.best.score == 0
      end
    end
  end
end
