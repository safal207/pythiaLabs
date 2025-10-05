defmodule Mix.Tasks.Compile.RustlerFallback do
  @moduledoc "Compiler that delegates to Rustler when available and becomes a no-op otherwise."
  use Mix.Task.Compiler

  @impl Mix.Task.Compiler
  def run(args) do
    try do
      Mix.Task.run("compile.rustler", args)
    rescue
      Mix.NoTaskError ->
        Mix.shell().info("Rustler compiler not available, skipping.")
        {:noop, []}
    end
  end
end
