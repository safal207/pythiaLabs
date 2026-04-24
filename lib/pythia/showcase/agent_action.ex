defmodule Pythia.Showcase.AgentAction do
  @moduledoc """
  Data model and validation helpers for deterministic agent action evaluation.
  """

  @type t :: %{
          action_id: String.t(),
          action_type: String.t(),
          actor: String.t(),
          target: String.t(),
          required_permission: String.t(),
          granted_permissions: [String.t()],
          metadata: map()
        }

  @required_fields [:action_type, :actor, :target, :required_permission]

  @spec build(map()) :: t()
  def build(attrs) when is_map(attrs) do
    %{
      action_id: Map.get(attrs, :action_id, "act_default"),
      action_type: Map.get(attrs, :action_type, ""),
      actor: Map.get(attrs, :actor, ""),
      target: Map.get(attrs, :target, ""),
      required_permission: Map.get(attrs, :required_permission, ""),
      granted_permissions: Map.get(attrs, :granted_permissions, []),
      metadata: Map.get(attrs, :metadata, %{})
    }
  end

  @spec validate(t()) :: :ok | {:error, atom()}
  def validate(action) when is_map(action) do
    if Enum.all?(@required_fields, &present?(Map.get(action, &1))) do
      :ok
    else
      {:error, :invalid_action}
    end
  end

  defp present?(value) when is_binary(value), do: String.trim(value) != ""
  defp present?(_), do: false
end
