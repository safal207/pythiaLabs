defmodule PythiaTest do
  use ExUnit.Case, async: true

  describe "refine/3" do
    test "successfully refines string to target" do
      {:ok, result} = Pythia.refine("kitten", "sitting")

      assert result.best.candidate == "sitting"
      assert result.best.score == 0
      assert result.steps > 0
      assert is_list(result.trace)
      assert length(result.trace) == result.steps
    end

    test "handles identical source and target" do
      {:ok, result} = Pythia.refine("same", "same")

      assert result.best.candidate == "same"
      assert result.best.score == 0
      assert result.steps == 1
    end

    test "accepts custom max_steps option" do
      {:ok, result} = Pythia.refine("abc", "xyz", max_steps: 5)

      assert result.steps <= 5
    end

    test "accepts custom threshold option" do
      {:ok, result} = Pythia.refine("hello", "hallo", threshold: 0)

      assert result.best.score <= 0
    end

    test "accepts custom no_improve_limit option" do
      {:ok, result} = Pythia.refine("test", "best", no_improve_limit: 3)

      assert is_map(result.best)
    end

    test "returns proper result structure" do
      {:ok, result} = Pythia.refine("a", "b")

      assert Map.has_key?(result, :best)
      assert Map.has_key?(result, :steps)
      assert Map.has_key?(result, :trace)

      assert Map.has_key?(result.best, :candidate)
      assert Map.has_key?(result.best, :score)
    end

    test "trace entries have correct structure" do
      {:ok, result} = Pythia.refine("cat", "bat")

      for entry <- result.trace do
        assert Map.has_key?(entry, :step)
        assert Map.has_key?(entry, :proposal)
        assert Map.has_key?(entry, :candidate)
        assert Map.has_key?(entry, :score)
        assert Map.has_key?(entry, :meta)
      end
    end
  end

  describe "refine/3 - integration scenarios" do
    test "classic Levenshtein examples" do
      test_cases = [
        {"kitten", "sitting", 3},
        {"saturday", "sunday", 3},
        {"", "hello", 5},
        {"hello", "", 5}
      ]

      for {source, target, expected_min_score} <- test_cases do
        {:ok, result} = Pythia.refine(source, target, max_steps: 50)

        assert result.best.score <= expected_min_score,
               "Expected score ≤ #{expected_min_score} for #{source} → #{target}, got #{result.best.score}"
      end
    end

    test "handles empty strings" do
      {:ok, result1} = Pythia.refine("", "")
      assert result1.best.score == 0

      {:ok, result2} = Pythia.refine("", "abc")
      assert result2.best.candidate == "abc"
      assert result2.best.score == 0

      {:ok, result3} = Pythia.refine("abc", "")
      assert result3.best.candidate == ""
      assert result3.best.score == 0
    end

    test "handles unicode correctly" do
      {:ok, result} = Pythia.refine("café", "cafe", max_steps: 10)

      assert result.best.candidate == "cafe"
      assert result.best.score == 0
    end

    test "handles emoji" do
      {:ok, result} = Pythia.refine("hello", "👋hello", max_steps: 10)

      assert result.best.candidate == "👋hello"
      assert result.best.score == 0
    end

    test "convergence for various string pairs" do
      pairs = [
        {"a", "b"},
        {"ab", "ba"},
        {"test", "best"},
        {"hello", "world"},
        {"foo", "bar"}
      ]

      for {source, target} <- pairs do
        {:ok, result} = Pythia.refine(source, target, max_steps: 30)

        # Should converge to exact target or get very close
        assert result.best.score <= 1,
               "Failed to converge #{source} → #{target}, score: #{result.best.score}"
      end
    end

    test "respects max_steps limit" do
      {:ok, result} = Pythia.refine("aaaa", "bbbb", max_steps: 2)

      assert result.steps == 2
      # May not reach target due to step limit
      assert result.best.score >= 0
    end

    test "terminates early when threshold reached" do
      # If threshold > 0, should stop before perfect match
      {:ok, result} = Pythia.refine("hello", "hallo", threshold: 1, max_steps: 100)

      # Should stop when score ≤ 1
      assert result.best.score <= 1
    end
  end

  describe "refine/3 - trace analysis" do
    test "trace shows progress toward goal" do
      {:ok, result} = Pythia.refine("kitten", "sitting", max_steps: 30)

      # Get all scores from trace
      scores = Enum.map(result.trace, & &1.score)

      # Best score should be in the trace
      assert result.best.score in scores

      # Final score should match best score or be close
      final_score = List.last(result.trace).score
      assert final_score == result.best.score
    end

    test "trace step numbers are sequential" do
      {:ok, result} = Pythia.refine("abc", "xyz", max_steps: 10)

      step_numbers = Enum.map(result.trace, & &1.step)
      expected = Enum.to_list(1..result.steps)

      assert step_numbers == expected
    end

    test "proposals are valid types" do
      {:ok, result} = Pythia.refine("hello", "world", max_steps: 20)

      valid_types = [:noop, :insert, :delete, :replace]

      for entry <- result.trace do
        proposal_type = elem(entry.proposal, 0)
        assert proposal_type in valid_types,
               "Invalid proposal type: #{inspect(proposal_type)}"
      end
    end
  end

  describe "refine/3 - performance characteristics" do
    test "completes simple refinements quickly" do
      simple_pairs = [
        {"a", "b"},
        {"cat", "bat"},
        {"test", "best"}
      ]

      for {source, target} <- simple_pairs do
        {:ok, result} = Pythia.refine(source, target, max_steps: 20)

        # Simple cases should complete in few steps
        assert result.steps < 10,
               "Too many steps for #{source} → #{target}: #{result.steps}"
      end
    end

    test "handles longer strings within step limit" do
      source = "The quick brown fox"
      target = "The slow brown dog"

      {:ok, result} = Pythia.refine(source, target, max_steps: 50)

      assert result.steps <= 50
      assert result.best.score >= 0
    end
  end

  describe "refine/3 - determinism" do
    test "produces consistent results for same input" do
      # Run same refinement multiple times
      results = for _ <- 1..3 do
        {:ok, result} = Pythia.refine("hello", "world", max_steps: 30)
        result
      end

      # All should produce same best score
      scores = Enum.map(results, & &1.best.score)
      assert Enum.uniq(scores) |> length() == 1

      # All should produce same step count (deterministic algorithm)
      steps = Enum.map(results, & &1.steps)
      assert Enum.uniq(steps) |> length() == 1
    end
  end
end
