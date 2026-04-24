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
      action_id: fetch(attrs, :action_id, "act_default"),
      action_type: fetch(attrs, :action_type, ""),
      actor: fetch(attrs, :actor, ""),
      target: fetch(attrs, :target, ""),
      required_permission: fetch(attrs, :required_permission, ""),
      granted_permissions: fetch(attrs, :granted_permissions, []),
      metadata: fetch(attrs, :metadata, %{})
    }
  end

  @spec validate(t()) :: :ok | {:error, atom()}
  def validate(action) when is_map(action) do
    permissions = Map.get(action, :granted_permissions)

    valid_permissions =
      is_list(permissions) and Enum.all?(permissions, fn permission -> is_binary(permission) end)

    if Enum.all?(@required_fields, &present?(Map.get(action, &1))) and valid_permissions do
      :ok
    else
      {:error, :invalid_action}
    end
  end

  defp fetch(attrs, key, default) do
    Map.get(attrs, key, Map.get(attrs, Atom.to_string(key), default))
  end

  defp present?(value) when is_binary(value), do: String.trim(value) != ""
  defp present?(_), do: false
end
