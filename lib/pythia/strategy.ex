defmodule Pythia.Strategy do
  @moduledoc """
  Behaviour for refinement strategies.

  A strategy determines how to generate proposals (candidate edits)
  to transform a current state toward an objective.

  Different strategies offer different exploration patterns:
  - Greedy: Always choose locally optimal move
  - Random: Explore randomly to escape local minima
  - Beam: Keep top-k candidates in parallel
  """

  @type state :: any()
  @type objective :: any()
  @type proposal :: Pythia.Executor.proposal()
  @type context :: %{
    optional(:step) => non_neg_integer(),
    optional(:score) => number(),
    optional(:trace) => list(),
    optional(atom()) => any()
  }

  @doc """
  Generate a proposal to transform current state toward objective.

  Arguments:
  - current: Current state/candidate
  - objective: Target state to reach
  - context: Additional context (step number, score, trace, etc.)

  Returns:
  - A proposal tuple (e.g., {:insert, ch, pos}, {:delete, pos}, etc.)
  """
  @callback propose(current :: state(), objective :: objective(), context :: context()) :: proposal()

  @doc """
  Initialize strategy with options.

  Returns:
  - Strategy-specific state/configuration
  """
  @callback init(opts :: keyword()) :: any()

  @doc """
  Optional: Reset strategy state (useful for stateful strategies).
  """
  @callback reset(strategy_state :: any()) :: any()

  @optional_callbacks [reset: 1]
end
