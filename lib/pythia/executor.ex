defmodule Pythia.Executor do
  @moduledoc "Executor + metrics (string edits + Levenshtein)."
  alias Pythia.Kernels
  defstruct []
  def new, do: %__MODULE__{}

  @type proposal :: {:noop} | {:insert, String.t(), non_neg_integer()} | {:delete, non_neg_integer()} | {:replace, String.t(), non_neg_integer()}

  def apply_proposal(_exec, current, {:noop}), do: {current, %{op: :noop}}
  def apply_proposal(_exec, current, {:insert, ch, pos}), do: {insert_at(current, ch, pos), %{op: :insert, ch: ch, pos: pos}}
  def apply_proposal(_exec, current, {:delete, pos}), do: {delete_at(current, pos), %{op: :delete, pos: pos}}
  def apply_proposal(_exec, current, {:replace, ch, pos}), do: {replace_at(current, ch, pos), %{op: :replace, ch: ch, pos: pos}}

  def score(_exec, a, b), do: Kernels.levenshtein(a, b)

  defp insert_at(str, ch, pos) do
    {left, right} = String.split_at(str, pos)
    left <> ch <> right
  end

  defp delete_at(str, pos) do
    {left, right} = String.split_at(str, pos)
    case String.graphemes(right) do
      [] -> left
      [_h | t] -> left <> Enum.join(t)
    end
  end

  defp replace_at(str, ch, pos) do
    {left, right} = String.split_at(str, pos)
    case String.graphemes(right) do
      [] -> left <> ch
      [_h | t] -> left <> ch <> Enum.join(t)
    end
  end
end
