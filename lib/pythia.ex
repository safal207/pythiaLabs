defmodule Pythia do
  @moduledoc """
  Public API for Pythia - Transparent AI Reasoning System.

  ## Multi-Strategy Support

  Pythia now supports multiple refinement strategies:
  - `:greedy_lcp` - Fast, deterministic (default)
  - `:random_walk` - Exploratory, escapes local minima
  - `:beam_search` - Balanced exploration/exploitation

  Strategies are selected automatically based on progress and Critic advice,
  or can be manually controlled via options.

  ## Examples

      # Basic usage (automatic strategy selection)
      {:ok, result} = Pythia.refine("kitten", "sitting")

      # Disable multi-strategy (always use greedy)
      {:ok, result} = Pythia.refine("kitten", "sitting",
        enable_multi_strategy: false
      )

      # Configure strategy selection
      {:ok, result} = Pythia.refine("kitten", "sitting",
        enable_multi_strategy: true,
        strategy_opts: [
          default_strategy: :greedy_lcp,
          plateau_threshold: 3
        ]
      )

  ## Options

  - `max_steps` - Maximum refinement steps (default: 20)
  - `threshold` - Stop when score ≤ threshold (default: 0)
  - `no_improve_limit` - Stop after N steps without improvement (default: 5)
  - `enable_multi_strategy` - Enable adaptive strategy switching (default: true)
  - `strategy_opts` - Options for strategy selector:
    - `default_strategy` - Initial strategy (default: :greedy_lcp)
    - `plateau_threshold` - Steps before switching on plateau (default: 3)
    - `enable_adaptive` - Allow dynamic switching (default: true)
  """

  alias Pythia.{Planner, Executor, Critic}

  @type strategy_name :: :greedy_lcp | :random_walk | :beam_search

  @type options :: [
          max_steps: pos_integer(),
          threshold: number(),
          no_improve_limit: pos_integer(),
          enable_multi_strategy: boolean(),
          strategy_opts: keyword()
        ]

  @doc """
  Refine a problem state toward an objective using transparent reasoning.

  Returns:
  - `{:ok, %{best: %{candidate: _, score: _}, steps: _, trace: _}}`
  """
  @spec refine(any(), any(), options()) :: {:ok, map()}
  def refine(problem, objective, opts \\ []) do
    planner = Planner.new(problem, objective, opts)
    exec = Executor.new()
    critic = Critic.new()
    Planner.run(planner, exec, critic)
  end
end
