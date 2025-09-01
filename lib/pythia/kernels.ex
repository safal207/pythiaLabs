defmodule Pythia.Kernels do
  @moduledoc "Rust NIF wrapper with safe fallback."
  use Rustler, otp_app: :liminal_pythia, crate: "fast_kernels"
  alias Pythia.KernelsFallback

  def levenshtein(a, b) when is_binary(a) and is_binary(b) do
    try do
      levenshtein_nif(a, b)
    rescue
      _ -> KernelsFallback.levenshtein(a, b)
    catch
      :exit, _ -> KernelsFallback.levenshtein(a, b)
    end
  end

  defp levenshtein_nif(_a, _b), do: :erlang.nif_error(:nif_not_loaded)
end
