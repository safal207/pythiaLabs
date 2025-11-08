defmodule Pythia.CriticTest do
  use ExUnit.Case, async: true
  alias Pythia.Critic

  describe "new/0" do
    test "creates critic struct" do
      critic = Critic.new()
      assert %Critic{} = critic
    end
  end

  describe "advise/2 - insufficient data" do
    test "returns :noop when trace is empty" do
      state = %{candidate: "test"}
      assert Critic.advise(state, []) == :noop
    end

    test "returns :noop when trace has < 3 steps" do
      state = %{candidate: "test"}
      trace = [
        %{step: 1, score: 5, candidate: "a"},
        %{step: 2, score: 4, candidate: "b"}
      ]

      assert Critic.advise(state, trace) == :noop
    end
  end

  describe "advise/2 - plateau detection" do
    test "detects score plateau in last 3 steps" do
      state = %{candidate: "test"}
      trace = [
        %{step: 3, score: 5, candidate: "c"},
        %{step: 2, score: 5, candidate: "b"},
        %{step: 1, score: 5, candidate: "a"}
      ]

      assert Critic.advise(state, trace) == {:suggest_random_mutation, reason: "Score plateau detected"}
    end

    test "no plateau when scores differ" do
      state = %{candidate: "test"}
      trace = [
        %{step: 3, score: 3, candidate: "c"},
        %{step: 2, score: 4, candidate: "b"},
        %{step: 1, score: 5, candidate: "a"}
      ]

      # Should return :noop or other advice, not plateau
      advice = Critic.advise(state, trace)
      assert advice == :noop or (elem(advice, 0) != :suggest_random_mutation)
    end
  end

  describe "advise/2 - loop detection" do
    test "detects candidate loops" do
      state = %{candidate: "test"}
      trace = [
        %{step: 5, score: 5, candidate: "a"},
        %{step: 4, score: 5, candidate: "b"},
        %{step: 3, score: 5, candidate: "a"},
        %{step: 2, score: 5, candidate: "b"},
        %{step: 1, score: 5, candidate: "a"}
      ]

      advice = Critic.advise(state, trace)
      assert {:suggest_strategy_shift, reason: "Candidate loop detected"} == advice
    end

    test "no loop when candidates are unique" do
      state = %{candidate: "test"}
      trace = [
        %{step: 5, score: 1, candidate: "e"},
        %{step: 4, score: 2, candidate: "d"},
        %{step: 3, score: 3, candidate: "c"},
        %{step: 2, score: 4, candidate: "b"},
        %{step: 1, score: 5, candidate: "a"}
      ]

      # Should not detect loop
      advice = Critic.advise(state, trace)
      assert advice != {:suggest_strategy_shift, reason: "Candidate loop detected"}
    end
  end

  describe "advise/2 - slow progress detection" do
    test "detects slow progress when improvement is minimal" do
      state = %{candidate: "test"}
      trace = [
        %{step: 5, score: 10.00, candidate: "e"},
        %{step: 4, score: 10.01, candidate: "d"},
        %{step: 3, score: 10.02, candidate: "c"},
        %{step: 2, score: 10.03, candidate: "b"},
        %{step: 1, score: 10.04, candidate: "a"}
      ]

      advice = Critic.advise(state, trace)
      assert advice == {:suggest_random_mutation, reason: "Slow progress detected"}
    end

    test "no slow progress warning when making good progress" do
      state = %{candidate: "test"}
      trace = [
        %{step: 5, score: 1, candidate: "e"},
        %{step: 4, score: 3, candidate: "d"},
        %{step: 3, score: 5, candidate: "c"},
        %{step: 2, score: 7, candidate: "b"},
        %{step: 1, score: 10, candidate: "a"}
      ]

      advice = Critic.advise(state, trace)
      # Should not suggest random mutation for slow progress
      if match?({:suggest_random_mutation, _}, advice) do
        {_, reason_kw} = advice
        reason = Keyword.get(reason_kw, :reason)
        assert reason != "Slow progress detected"
      end
    end
  end

  describe "should_intervene?/1" do
    test "returns false for :noop" do
      refute Critic.should_intervene?(:noop)
    end

    test "returns true for suggest_random_mutation" do
      assert Critic.should_intervene?({:suggest_random_mutation, reason: "test"})
    end

    test "returns true for suggest_strategy_shift" do
      assert Critic.should_intervene?({:suggest_strategy_shift, reason: "test"})
    end

    test "returns true for suggest_early_stop" do
      assert Critic.should_intervene?({:suggest_early_stop, reason: "test"})
    end

    test "returns false for unknown advice" do
      refute Critic.should_intervene?(:unknown)
      refute Critic.should_intervene?({:unknown_action, []})
    end
  end

  describe "advise/2 - priority of detection" do
    test "plateau detection takes priority" do
      state = %{candidate: "test"}
      # Same score (plateau) + could be slow progress
      trace = [
        %{step: 3, score: 5, candidate: "c"},
        %{step: 2, score: 5, candidate: "b"},
        %{step: 1, score: 5, candidate: "a"}
      ]

      assert Critic.advise(state, trace) == {:suggest_random_mutation, reason: "Score plateau detected"}
    end
  end
end
