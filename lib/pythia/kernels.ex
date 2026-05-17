defmodule Pythia.Kernels do
  @moduledoc "Rust NIF wrapper with safe fallback."
  use Rustler, otp_app: :liminal_pythia, crate: "fast_kernels"
  require Logger
  alias Pythia.KernelsFallback

  def levenshtein(a, b) when is_binary(a) and is_binary(b) do
    try do
      levenshtein_nif(a, b)
    rescue
      e in [ErlangError, UndefinedFunctionError] ->
        case e do
          %ErlangError{original: :nif_not_loaded} ->
            KernelsFallback.levenshtein(a, b)

          %UndefinedFunctionError{} ->
            KernelsFallback.levenshtein(a, b)

          other ->
            Logger.warning("levenshtein NIF raised #{inspect(other)}; falling back")
            KernelsFallback.levenshtein(a, b)
        end
    end
  end

  defp levenshtein_nif(_a, _b), do: :erlang.nif_error(:nif_not_loaded)
end
