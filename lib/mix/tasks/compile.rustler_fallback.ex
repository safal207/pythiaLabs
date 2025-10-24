defmodule Mix.Tasks.Compile.RustlerFallback do
  @moduledoc """
  Compiles Rustler NIFs with fallback to Elixir implementation.

  This compiler attempts to compile Rustler NIFs but gracefully falls back
  to pure Elixir implementations if Rustler compilation fails (e.g., when
  Rust is not available in the environment).
  """
  use Mix.Task.Compiler

  @recursive true

  @impl Mix.Task.Compiler
  def run(_args) do
    if rustler_available?() do
      try do
        # Attempt to compile Rustler NIFs
        case Mix.Task.run("compile.rustler", []) do
          {:ok, _} ->
            Mix.shell().info("Rustler NIFs compiled successfully")
            {:ok, []}

          {:error, _} = error ->
            Mix.shell().info("Rustler compilation failed, using fallback implementation")
            {:ok, []}

          _ ->
            {:ok, []}
        end
      rescue
        e ->
          Mix.shell().info("Rustler compilation error: #{inspect(e)}, using fallback")
          {:ok, []}
      end
    else
      Mix.shell().info("Rustler not available, using fallback implementation")
      {:ok, []}
    end
  end

  @impl Mix.Task.Compiler
  def clean do
    # Clean Rustler artifacts if the task exists
    if rustler_available?() do
      try do
        Mix.Task.run("clean.rustler", [])
      rescue
        _ -> :ok
      end
    end

    :ok
  end

  defp rustler_available? do
    # Check if Rustler is available as a dependency
    Code.ensure_loaded?(Rustler) and function_exported?(Mix.Task, :run, 2)
  end
end
