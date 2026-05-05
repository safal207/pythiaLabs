defmodule Mix.Tasks.Pythia.EvalJson do
  use Mix.Task

  @shortdoc "Run deterministic showcase gate on JSON (stdin or --file)"

  @moduledoc """
  Reads one JSON object and prints the evaluation result as JSON on stdout.

  **`gate`** selects the showcase: `"agent_infra_action"`, `"banking_risk_action"`, or
  `"web3_treasury_action"`. See `Pythia.Mcp.JsonEvaluator` for field layout per gate.

  ## Examples

      echo '{"gate":"agent_infra_action",...}' | mix pythia.eval_json
      echo '{"gate":"banking_risk_action","action":{...},"governance":{...}}' | mix pythia.eval_json

      mix pythia.eval_json --file proposal.json
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
