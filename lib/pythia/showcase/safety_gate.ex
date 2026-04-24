defmodule Pythia.Showcase.SafetyGate do
  @moduledoc """
  Deterministic constraint gate for agent actions.
  """

  alias Pythia.Showcase.AgentAction

  @spec evaluate(AgentAction.t()) :: {:ok, map()} | {:error, map()}
  def evaluate(action) do
    with :ok <- AgentAction.validate(action),
         :ok <- check_permission(action.required_permission, action.granted_permissions) do
      trace = [
        %{event: :proposed_action, action_type: action.action_type},
        %{event: :constraint_check, constraint: :permission_present, result: :pass},
        %{event: :decision, result: :proceed}
      ]

      {:ok,
       %{
         status: :accepted,
         action: action,
         confidence: 1.0,
         stop_reason: :constraints_satisfied,
         trace: trace
       }}
    else
      {:error, :invalid_action} ->
        {:error,
         %{
           status: :rejected,
           rejected_action: action,
           stop_reason: :invalid_action,
           trace: invalid_trace(action)
         }}

      {:error, :missing_authorization} ->
        {:error,
         %{
           status: :rejected,
           rejected_action: action,
           stop_reason: :missing_authorization,
           trace: [
             %{event: :proposed_action, action_type: action.action_type},
             %{event: :constraint_check, constraint: :permission_present, result: :fail},
             %{event: :decision, result: :reject}
           ]
         }}
    end
  end

  defp check_permission(required, granted_permissions)
       when is_binary(required) and is_list(granted_permissions) do
    if Enum.member?(granted_permissions, required) do
      :ok
    else
      {:error, :missing_authorization}
    end
  end

  defp check_permission(_required, _granted_permissions), do: {:error, :invalid_action}

  defp invalid_trace(action) do
    [
      %{event: :proposed_action, action_type: Map.get(action, :action_type, nil)},
      %{event: :constraint_check, constraint: :action_shape, result: :fail},
      %{event: :decision, result: :reject}
    ]
  end
end
