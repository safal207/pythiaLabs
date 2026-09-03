defmodule Mix.Tasks.Pythia.CgqaConformance do
  use Mix.Task

  @shortdoc "Run the pinned CGQA/LiminalQA interop conformance suite"

  @moduledoc """
  Runs all 14 canonical CGQA/LiminalQA conformance vectors through Pythia's
  native Elixir adapter. The embedded suite is used by default.

      mix pythia.cgqa_conformance
      mix pythia.cgqa_conformance --suite path/to/suite.json
  """

  @impl Mix.Task
  def run(argv) do
    {opts, positional, invalid} =
      OptionParser.parse(argv,
        strict: [suite: :string],
        aliases: [s: :suite]
      )

    Mix.Task.run("compile")

    case {positional, invalid} do
      {[], []} -> execute(Keyword.get(opts, :suite))
      _ -> emit_error("unsupported command arguments")
    end
  end

  defp execute(suite_path) do
    case Pythia.Interop.CgqaConformance.run(suite_path) do
      {:ok, report} ->
        IO.puts(Jason.encode!(report, maps: :strict))

        if report["status"] != "PASS" do
          System.halt(1)
        end

      {:error, reason} ->
        emit_error(reason)
    end
  end

  defp emit_error(message) do
    IO.puts(
      Jason.encode!(
        %{
          ok: false,
          status: "FAIL",
          message: message,
          mayAuthorizeAction: false,
          sideEffectExecuted: false
        },
        maps: :strict
      )
    )

    System.halt(1)
  end
end
