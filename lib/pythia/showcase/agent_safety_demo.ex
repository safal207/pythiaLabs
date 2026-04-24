defmodule Pythia.Showcase.AgentSafetyDemo do
  @moduledoc """
  Demonstrates the controlled loop: propose -> evaluate constraints -> stop with reason.
  """

  alias Pythia.Showcase.{AgentAction, SafetyGate}

  @spec run(map()) :: {:ok, map()} | {:error, map()}
  def run(action_attrs) when is_map(action_attrs) do
    action = AgentAction.build(action_attrs)
    result = SafetyGate.evaluate(action)

    emit_telemetry(result)

    result
  end

  defp emit_telemetry({status_tag, %{stop_reason: stop_reason} = result}) do
    status =
      case status_tag do
        :ok -> :accepted
        :error -> :rejected
      end

    :telemetry.execute(
      [:pythia, :showcase, :decision],
      %{count: 1},
      %{status: status, stop_reason: stop_reason, trace_length: length(result.trace)}
    )
  end
end
