defmodule Pythia.KernelsFallback do
  @moduledoc """
  Pure Elixir fallback for `Pythia.Kernels.levenshtein/2`.

  Operates on Unicode codepoints (`String.to_charlist/1`) so behaviour
  matches the Rust NIF, which iterates via `str::chars()`. Uses a tuple
  for the previous DP row to keep indexed reads O(1), giving overall
  O(m·n) time.
  """

  def levenshtein(a, b) when is_binary(a) and is_binary(b) do
    do_lev(String.to_charlist(a), String.to_charlist(b))
  end

  defp do_lev([], ys), do: length(ys)
  defp do_lev(xs, []), do: length(xs)

  defp do_lev(xs, ys) do
    n = length(ys)
    initial_prev = List.to_tuple(Enum.to_list(0..n))
    indexed_ys = Enum.with_index(ys, 1)

    xs
    |> Enum.with_index(1)
    |> Enum.reduce(initial_prev, fn {xi, i}, prev_row ->
      {curr_rev, _last} =
        Enum.reduce(indexed_ys, {[i], i}, fn {yj, j}, {acc, prev_in_row} ->
          cost = if xi == yj, do: 0, else: 1
          insert = prev_in_row + 1
          delete = elem(prev_row, j) + 1
          replace = elem(prev_row, j - 1) + cost
          new_val = min(insert, min(delete, replace))
          {[new_val | acc], new_val}
        end)

      curr_rev |> Enum.reverse() |> List.to_tuple()
    end)
    |> elem(n)
  end
end
