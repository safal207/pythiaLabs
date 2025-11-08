defmodule Pythia.StrategySelector do
  @moduledoc """
  Meta-learner that selects the best strategy based on context.

  Analyzes current situation (trace, score, progress) and chooses
  the most appropriate strategy:
  - GreedyLCP: When making steady progress
  - RandomWalk: When stuck in plateau or loop
  - BeamSearch: For complex problems or when diversity needed

  Selection Heuristics:
  1. Early stages (< 5 steps): Use GreedyLCP (fast convergence)
  2. Plateau detected: Switch to RandomWalk (escape local minimum)
  3. Loop detected: Switch to BeamSearch (explore alternatives)
  4. Slow progress: Mix RandomWalk with Greedy
  5. Good progress: Continue with current strategy

  Configuration:
  - default_strategy: Strategy to use initially (default: :greedy_lcp)
  - plateau_threshold: Steps before switching on plateau (default: 3)
  - enable_adaptive: Enable dynamic strategy switching (default: true)
  """

  alias Pythia.Strategies.{GreedyLCP, RandomWalk, BeamSearch}
  alias Pythia.Critic

  defstruct current_strategy: :greedy_lcp,
            strategy_states: %{},
            switch_count: 0,
            opts: []

  @type strategy_name :: :greedy_lcp | :random_walk | :beam_search
  @type t :: %__MODULE__{
          current_strategy: strategy_name(),
          strategy_states: map(),
          switch_count: non_neg_integer(),
          opts: keyword()
        }

  @doc """
  Initialize strategy selector with options.
  """
  def new(opts \\ []) do
    default_strategy = Keyword.get(opts, :default_strategy, :greedy_lcp)

    %__MODULE__{
      current_strategy: default_strategy,
      strategy_states: %{
        greedy_lcp: GreedyLCP.init([]),
        random_walk: RandomWalk.init([]),
        beam_search: BeamSearch.init([])
      },
      opts: opts
    }
  end

  @doc """
  Select best strategy based on current context.

  Returns: {:strategy_name, strategy_module, updated_selector}
  """
  def select_strategy(%__MODULE__{} = selector, context) do
    trace = Map.get(context, :trace, [])
    step = Map.get(context, :step, 0)
    critic_advice = Map.get(context, :critic_advice, :noop)

    enable_adaptive = Keyword.get(selector.opts, :enable_adaptive, true)

    new_strategy = if enable_adaptive do
      choose_strategy(selector.current_strategy, step, trace, critic_advice, selector.opts)
    else
      selector.current_strategy
    end

    # Update selector if strategy changed
    selector = if new_strategy != selector.current_strategy do
      %{selector |
        current_strategy: new_strategy,
        switch_count: selector.switch_count + 1
      }
    else
      selector
    end

    strategy_module = get_strategy_module(new_strategy)

    {new_strategy, strategy_module, selector}
  end

  @doc """
  Get current strategy module.
  """
  def get_current_strategy(%__MODULE__{} = selector) do
    get_strategy_module(selector.current_strategy)
  end

  @doc """
  Get strategy state for a specific strategy.
  """
  def get_strategy_state(%__MODULE__{} = selector, strategy_name) do
    Map.get(selector.strategy_states, strategy_name, %{})
  end

  # Private helpers

  defp choose_strategy(current, step, trace, critic_advice, opts) do
    cond do
      # Early stages: use greedy (fast convergence)
      step < 5 ->
        :greedy_lcp

      # Critic suggests random mutation (plateau or slow progress)
      match?({:suggest_random_mutation, _}, critic_advice) ->
        :random_walk

      # Critic suggests strategy shift (loop detected)
      match?({:suggest_strategy_shift, _}, critic_advice) ->
        if current == :beam_search, do: :random_walk, else: :beam_search

      # Check manual overrides from Critic
      match?({:suggest_early_stop, _}, critic_advice) ->
        current  # Keep current strategy

      # Default: continue with current unless making poor progress
      true ->
        if poor_recent_progress?(trace, window: 5) do
          # Rotate strategies: greedy → beam → random → greedy
          case current do
            :greedy_lcp -> :beam_search
            :beam_search -> :random_walk
            :random_walk -> :greedy_lcp
          end
        else
          current
        end
    end
  end

  defp get_strategy_module(:greedy_lcp), do: GreedyLCP
  defp get_strategy_module(:random_walk), do: RandomWalk
  defp get_strategy_module(:beam_search), do: BeamSearch

  defp poor_recent_progress?(trace, opts) do
    window = Keyword.get(opts, :window, 5)

    if length(trace) < window do
      false
    else
      recent_scores = trace
        |> Enum.take(window)
        |> Enum.map(& &1.score)
        |> Enum.filter(&is_number/1)

      if length(recent_scores) < 2 do
        false
      else
        first = List.last(recent_scores)
        last = hd(recent_scores)
        improvement = first - last

        # Poor progress if improvement < 0.5 over window
        improvement < 0.5 and improvement >= 0
      end
    end
  end
end
