defmodule Pythia.StrategySelectorTest do
  use ExUnit.Case, async: true
  alias Pythia.StrategySelector
  alias Pythia.Strategies.{GreedyLCP, RandomWalk, BeamSearch}

  describe "new/1" do
    test "creates selector with default strategy" do
      selector = StrategySelector.new()

      assert selector.current_strategy == :greedy_lcp
      assert selector.switch_count == 0
      assert is_map(selector.strategy_states)
    end

    test "accepts custom default strategy" do
      selector = StrategySelector.new(default_strategy: :random_walk)

      assert selector.current_strategy == :random_walk
    end
  end

  describe "select_strategy/2" do
    test "returns greedy for early steps" do
      selector = StrategySelector.new()
      context = %{step: 2, trace: [], critic_advice: :noop}

      {strategy, module, _} = StrategySelector.select_strategy(selector, context)

      assert strategy == :greedy_lcp
      assert module == GreedyLCP
    end

    test "switches to random_walk on plateau advice" do
      selector = StrategySelector.new()

      context = %{
        step: 10,
        trace: [%{score: 5}, %{score: 5}, %{score: 5}],
        critic_advice: {:suggest_random_mutation, reason: "plateau"}
      }

      {strategy, module, updated} = StrategySelector.select_strategy(selector, context)

      assert strategy == :random_walk
      assert module == RandomWalk
      assert updated.current_strategy == :random_walk
      assert updated.switch_count == 1
    end

    test "switches strategy on loop advice" do
      selector = StrategySelector.new()

      context = %{
        step: 10,
        trace: [],
        critic_advice: {:suggest_strategy_shift, reason: "loop"}
      }

      {strategy, module, updated} = StrategySelector.select_strategy(selector, context)

      # Should switch to beam or random (depends on implementation)
      assert strategy in [:beam_search, :random_walk]
      assert updated.switch_count == 1
    end

    test "maintains current strategy with :noop advice" do
      selector = StrategySelector.new()

      context = %{
        step: 10,
        trace: [%{score: 5}, %{score: 4}, %{score: 3}],  # Good progress
        critic_advice: :noop
      }

      {strategy, _, updated} = StrategySelector.select_strategy(selector, context)

      assert strategy == :greedy_lcp
      assert updated.switch_count == 0
    end

    test "increments switch_count on strategy change" do
      selector = StrategySelector.new()

      context1 = %{
        step: 10,
        trace: [],
        critic_advice: {:suggest_random_mutation, reason: "test"}
      }

      {_, _, selector} = StrategySelector.select_strategy(selector, context1)
      assert selector.switch_count == 1

      context2 = %{
        step: 15,
        trace: [],
        critic_advice: {:suggest_strategy_shift, reason: "test"}
      }

      {_, _, selector} = StrategySelector.select_strategy(selector, context2)
      assert selector.switch_count == 2
    end

    test "respects enable_adaptive option" do
      # Disable adaptive selection
      selector = StrategySelector.new(enable_adaptive: false)

      context = %{
        step: 10,
        trace: [],
        critic_advice: {:suggest_random_mutation, reason: "should be ignored"}
      }

      {strategy, _, updated} = StrategySelector.select_strategy(selector, context)

      # Should stay on default strategy
      assert strategy == :greedy_lcp
      assert updated.switch_count == 0
    end
  end

  describe "get_current_strategy/1" do
    test "returns current strategy module" do
      selector = StrategySelector.new()

      assert StrategySelector.get_current_strategy(selector) == GreedyLCP
    end

    test "reflects strategy changes" do
      selector = %{StrategySelector.new() | current_strategy: :random_walk}

      assert StrategySelector.get_current_strategy(selector) == RandomWalk
    end
  end

  describe "get_strategy_state/2" do
    test "returns strategy state for given strategy" do
      selector = StrategySelector.new()

      state = StrategySelector.get_strategy_state(selector, :greedy_lcp)
      assert is_map(state)
    end

    test "returns empty map for unknown strategy" do
      selector = StrategySelector.new()

      state = StrategySelector.get_strategy_state(selector, :unknown)
      assert state == %{}
    end
  end
end
