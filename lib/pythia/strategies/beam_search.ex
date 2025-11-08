defmodule Pythia.Strategies.BeamSearch do
  @moduledoc """
  Beam Search strategy with top-k candidates.

  Maintains a beam of top-k candidates and explores them in parallel.
  At each step, generates proposals for all candidates in the beam,
  evaluates them, and keeps only the top-k.

  Algorithm:
  1. Maintain beam of top-k candidates
  2. For each candidate, generate multiple proposals
  3. Evaluate all proposals
  4. Keep top-k candidates for next iteration

  Note: This strategy requires special handling in Planner to support
  parallel candidate tracking. For MVP, we use a simplified version
  that generates k different proposals and picks the best one.

  Pros:
  - Explores multiple paths simultaneously
  - Less likely to get stuck in local minima
  - Good balance between exploration and exploitation

  Cons:
  - Higher computational cost (k× evaluations)
  - More complex state management
  - Memory overhead for tracking candidates

  Configuration:
  - beam_width: Number of candidates to keep (default: 3)
  - proposal_diversity: Generate diverse proposals (default: true)
  """

  @behaviour Pythia.Strategy

  alias Pythia.Strategies.{GreedyLCP, RandomWalk}

  @impl true
  def init(opts) do
    %{
      beam_width: Keyword.get(opts, :beam_width, 3),
      proposal_diversity: Keyword.get(opts, :proposal_diversity, true),
      greedy: GreedyLCP.init([]),
      random: RandomWalk.init([])
    }
  end

  @impl true
  def propose(current, target, context) do
    state = Map.get(context, :strategy_state, init([]))
    beam_width = state.beam_width

    if current == target do
      {:noop}
    else
      # Generate diverse proposals
      proposals = generate_diverse_proposals(current, target, beam_width, state)

      # For MVP: return first proposal (greedy)
      # TODO: In future, Planner should evaluate all and pick best
      hd(proposals)
    end
  end

  # Private helpers

  defp generate_diverse_proposals(current, target, k, state) do
    proposals = []

    # 1. Always include greedy proposal
    greedy_proposal = GreedyLCP.propose(current, target, %{strategy_state: state.greedy})
    proposals = [greedy_proposal | proposals]

    # 2. Add random proposals for diversity
    random_proposals = for _ <- 1..(k - 1) do
      RandomWalk.propose(current, target, %{strategy_state: state.random})
    end

    proposals = proposals ++ random_proposals

    # 3. Remove duplicates and take top-k
    proposals
    |> Enum.uniq()
    |> Enum.take(k)
  end
end
