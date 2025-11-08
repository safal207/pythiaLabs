defmodule Pythia.Strategies.RandomWalk do
  @moduledoc """
  Random Walk exploration strategy.

  This strategy randomly chooses edit operations to explore the solution space.
  Useful for escaping local minima and discovering unexpected paths.

  Algorithm:
  1. Randomly choose operation type (insert/delete/replace)
  2. Randomly choose position in string
  3. For insert/replace: randomly choose character from target

  Pros:
  - Can escape local minima
  - Explores diverse solution paths
  - No bias toward particular patterns

  Cons:
  - Slow convergence
  - Many wasted steps
  - Non-deterministic results

  Best used:
  - When greedy strategy gets stuck
  - For small perturbations to break plateaus
  - Combined with other strategies (hybrid approach)
  """

  @behaviour Pythia.Strategy

  @impl true
  def init(opts) do
    %{
      temperature: Keyword.get(opts, :temperature, 1.0),
      operations: Keyword.get(opts, :operations, [:insert, :delete, :replace])
    }
  end

  @impl true
  def propose(current, target, context) when is_binary(current) and is_binary(target) do
    state = Map.get(context, :strategy_state, init([]))
    operations = state.operations

    # If strings are identical, return noop
    if current == target do
      {:noop}
    else
      # Randomly choose operation type
      op_type = Enum.random(operations)

      case op_type do
        :insert -> propose_insert(current, target)
        :delete -> propose_delete(current, target)
        :replace -> propose_replace(current, target)
      end
    end
  end

  # Private helpers

  defp propose_insert(current, target) do
    # Choose random position to insert
    pos = :rand.uniform(String.length(current) + 1) - 1

    # Choose random character from target (or from diff)
    char = if String.length(target) > 0 do
      target_chars = String.graphemes(target)
      Enum.random(target_chars)
    else
      # Fallback: random lowercase letter
      <<:rand.uniform(26) + 96>>
    end

    {:insert, char, pos}
  end

  defp propose_delete(current, _target) do
    if String.length(current) == 0 do
      {:noop}
    else
      # Choose random position to delete
      pos = :rand.uniform(String.length(current)) - 1
      {:delete, pos}
    end
  end

  defp propose_replace(current, target) do
    if String.length(current) == 0 do
      # Can't replace in empty string, do insert instead
      propose_insert(current, target)
    else
      # Choose random position to replace
      pos = :rand.uniform(String.length(current)) - 1

      # Choose random character from target
      char = if String.length(target) > 0 do
        target_chars = String.graphemes(target)
        Enum.random(target_chars)
      else
        <<:rand.uniform(26) + 96>>
      end

      {:replace, char, pos}
    end
  end
end
