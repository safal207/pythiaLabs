defmodule Pythia.Strategies.GreedyLCP do
  @moduledoc """
  Greedy Longest Common Prefix strategy.

  This strategy uses a greedy approach based on the longest common prefix
  between current and target strings. It always chooses the locally optimal
  edit operation.

  Algorithm:
  1. Find longest common prefix (LCP) of current and target
  2. Look at first differing character after LCP
  3. Propose:
     - :insert if target has more characters
     - :delete if current has more characters
     - :replace if both differ at same position
     - :noop if strings are identical

  Pros:
  - Fast convergence for strings with similar prefixes
  - Deterministic and predictable
  - Minimal step count for many cases

  Cons:
  - Can get stuck in local minima
  - Not optimal for strings requiring complex rearrangements
  - No exploration of alternative paths
  """

  @behaviour Pythia.Strategy

  @impl true
  def init(_opts), do: %{}

  @impl true
  def propose(current, target, _context) when is_binary(current) and is_binary(target) do
    {prefix, c_rest, t_rest} = longest_common_prefix(current, target)

    cond do
      c_rest == "" and t_rest == "" ->
        {:noop}

      c_rest == "" ->
        {:insert, String.first(t_rest), String.length(prefix)}

      t_rest == "" ->
        {:delete, String.length(prefix)}

      true ->
        {:replace, String.first(t_rest), String.length(prefix)}
    end
  end

  # Private helpers

  defp longest_common_prefix(a, b), do: lcp(a, b, "")

  defp lcp(<<>>, rest, acc), do: {acc, "", rest}
  defp lcp(rest, <<>>, acc), do: {acc, rest, ""}

  defp lcp(<<x::utf8, xs::binary>>, <<y::utf8, ys::binary>>, acc) when x == y do
    lcp(xs, ys, acc <> <<x::utf8>>)
  end

  defp lcp(xs, ys, acc), do: {acc, xs, ys}
end
