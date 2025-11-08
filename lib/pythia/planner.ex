defmodule Pythia.Planner do
  @moduledoc """
  HRM-like outer loop: propose → run → measure → refine.

  Enhanced with multi-strategy support:
  - Adaptive strategy selection based on context
  - Integration with Critic for intelligent strategy switching
  - Support for GreedyLCP, RandomWalk, and BeamSearch strategies

  The planner now dynamically selects the best strategy at each step
  based on trace analysis and Critic advice.
  """

  alias Pythia.{Executor, StrategySelector}

  defstruct problem: nil,
            objective: nil,
            state: nil,
            best: nil,
            step: 0,
            max_steps: 20,
            threshold: 0,
            no_improve_limit: 5,
            no_improve: 0,
            trace: [],
            strategy_selector: nil,
            current_strategy: nil

  def new(problem, objective, opts) do
    # Extract strategy options
    strategy_opts = Keyword.get(opts, :strategy_opts, [])
    enable_multi_strategy = Keyword.get(opts, :enable_multi_strategy, true)

    strategy_selector = if enable_multi_strategy do
      StrategySelector.new(strategy_opts)
    else
      # Disable adaptive selection, always use greedy
      StrategySelector.new(Keyword.put(strategy_opts, :enable_adaptive, false))
    end

    %__MODULE__{
      problem: problem,
      objective: objective,
      state: %{candidate: problem},
      best: %{candidate: problem, score: :infinity},
      max_steps: Keyword.get(opts, :max_steps, 20),
      threshold: Keyword.get(opts, :threshold, 0),
      no_improve_limit: Keyword.get(opts, :no_improve_limit, 5),
      strategy_selector: strategy_selector,
      current_strategy: :greedy_lcp
    }
  end

  def run(%__MODULE__{} = p, %Executor{} = exec, critic) do
    do_run(p, exec, critic)
  end

  defp do_run(%__MODULE__{step: s, max_steps: m} = p, _e, _c) when s >= m, do: finalize(p)

  defp do_run(p, exec, critic) do
    # Get advice from Critic
    critic_advice = Pythia.Critic.advise(p.state, p.trace)

    # Select strategy based on context and critic advice
    context = %{
      trace: p.trace,
      step: p.step,
      score: (if p.best.score == :infinity, do: 0, else: p.best.score),
      critic_advice: critic_advice
    }

    {strategy_name, strategy_module, updated_selector} =
      StrategySelector.select_strategy(p.strategy_selector, context)

    # Get strategy state
    strategy_state = StrategySelector.get_strategy_state(updated_selector, strategy_name)

    # Generate proposal using selected strategy
    strategy_context = %{
      step: p.step,
      score: (if p.best.score == :infinity, do: 0, else: p.best.score),
      trace: p.trace,
      strategy_state: strategy_state
    }

    proposal = strategy_module.propose(p.state.candidate, p.objective, strategy_context)

    # Apply proposal and measure
    {new_candidate, meta} = Executor.apply_proposal(exec, p.state.candidate, proposal)
    score = Executor.score(exec, new_candidate, p.objective)

    {best, no_improve} =
      case p.best do
        %{score: s} when is_number(s) and score < s -> {%{candidate: new_candidate, score: score}, 0}
        %{score: :infinity} -> {%{candidate: new_candidate, score: score}, 0}
        _ -> {p.best, p.no_improve + 1}
      end

    step = p.step + 1

    # Enhanced trace entry with strategy info
    trace_entry = %{
      step: step,
      proposal: proposal,
      candidate: new_candidate,
      score: score,
      meta: Map.merge(meta, %{
        strategy: strategy_name,
        critic_advice: critic_advice
      })
    }

    p = %{p |
      state: %{candidate: new_candidate},
      best: best,
      step: step,
      no_improve: no_improve,
      trace: [trace_entry | p.trace],
      strategy_selector: updated_selector,
      current_strategy: strategy_name
    }

    cond do
      score <= p.threshold -> finalize(p)
      no_improve >= p.no_improve_limit ->
        _ = critic
        finalize(p)
      true -> do_run(p, exec, critic)
    end
  end

  defp finalize(p) do
    {:ok, %{best: p.best, steps: p.step, trace: Enum.reverse(p.trace)}}
  end
end
