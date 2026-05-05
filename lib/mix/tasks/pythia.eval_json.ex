defmodule Mix.Tasks.Pythia.EvalJson do
  use Mix.Task

  @shortdoc "Run AgentInfraAction gate on JSON (stdin or --file path)"

  @moduledoc """
  Reads one JSON object and prints the evaluation result as JSON on stdout.

  ## Examples

      echo '{"gate":"agent_infra_action",...}' | mix pythia.eval_json

      mix pythia.eval_json --file proposal.json

  See `Pythia.Mcp.JsonEvaluator` for the input schema.
  """

  @impl Mix.Task
  def run(argv) do
    {opts, _, _} =
      OptionParser.parse(argv,
        strict: [file: :string],
        aliases: [f: :file]
      )

    Mix.Task.run("compile")

    input =
      case Keyword.get(opts, :file) do
        nil -> IO.read(:stdio)
        path -> File.read!(path)
      end

    input = String.trim(input)

    case input do
      "" ->
        IO.puts(Jason.encode!(%{ok: false, error: "empty_input"}))
        System.halt(2)

      body ->
        case Pythia.Mcp.JsonEvaluator.run(body) do
          {:ok, resp} ->
            IO.puts(Jason.encode!(resp))

          {:error, err} ->
            IO.puts(Jason.encode!(err))
            System.halt(1)
        end
    end
  end
end
