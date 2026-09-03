defmodule Mix.Tasks.Pythia.EvalExternalEvidence do
  use Mix.Task

  @shortdoc "Evaluate CGQA/LiminalQA evidence as non-authorizing advisory context"

  @moduledoc """
  Reads a ContractGraph-QA bounded-evidence or LiminalQA candidate-export JSON
  artifact from stdin or `--file`. A valid artifact produces `ESCALATE`, never
  `ALLOW`.

      mix pythia.eval_external_evidence --file evidence.json
      cat evidence.json | mix pythia.eval_external_evidence
  """

  @impl Mix.Task
  def run(argv) do
    {opts, positional, invalid} =
      OptionParser.parse(argv,
        strict: [file: :string],
        aliases: [f: :file]
      )

    Mix.Task.run("compile")

    case {Keyword.get(opts, :file), positional, invalid} do
      {_, [_ | _], _} -> emit_error("unsupported positional arguments")
      {_, _, [_ | _]} -> emit_error("unsupported command arguments")
      {nil, [], []} -> IO.read(:stdio) |> evaluate_body()
      {path, [], []} -> evaluate_file(path)
    end
  end

  defp evaluate_file(path) do
    case File.read(path) do
      {:ok, body} ->
        evaluate_body(body)

      {:error, reason} ->
        emit_error("could not read input: #{:file.format_error(reason)}")
    end
  end

  defp evaluate_body(body) do
    case String.trim(body) do
      "" ->
        emit_error("empty input")

      _ ->
        case Pythia.Interop.ExternalEvidence.evaluate_json(body) do
          {:ok, assessment} -> IO.puts(Jason.encode!(assessment, maps: :strict))
          {:error, rejection} -> emit_rejection(rejection)
        end
    end
  end

  defp emit_error(message) do
    emit_rejection(%{
      ok: false,
      outcome: "BLOCK",
      status: "rejected",
      stopReason: "invalid_command",
      message: message,
      mayAuthorizeAction: false,
      sideEffectExecuted: false
    })
  end

  defp emit_rejection(rejection) do
    IO.puts(Jason.encode!(rejection, maps: :strict))
    System.halt(1)
  end
end
