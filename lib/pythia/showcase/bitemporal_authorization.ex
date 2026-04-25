defmodule Pythia.Showcase.BitemporalAuthorization do
  @moduledoc """
  Deterministic in-memory showcase for bitemporal authorization reasoning.
  """

  @spec evaluate(map(), map()) :: {:ok, map()} | {:error, map()}
  def evaluate(action, permission_record) when is_map(action) and is_map(permission_record) do
    required_permission = fetch(action, :required_permission)
    permission = fetch(permission_record, :permission)
    action_time = fetch(action, :action_time)
    decision_time = fetch(action, :decision_time)
    valid_from = fetch(permission_record, :valid_from)
    valid_to = fetch(permission_record, :valid_to)
    recorded_at = fetch(permission_record, :recorded_at)

    base_trace = [
      %{
        event: :proposed_action,
        action_id: fetch(action, :action_id),
        action_type: fetch(action, :action_type),
        required_permission: required_permission,
        action_time: action_time,
        decision_time: decision_time
      },
      %{event: :required_permission, value: required_permission}
    ]

    cond do
      not matching_permission?(required_permission, permission) ->
        reject(:missing_permission_record, [
          %{
            event: :permission_match_check,
            result: :fail,
            required: required_permission,
            record: permission
          },
          %{event: :decision, result: :reject}
          | base_trace
        ])

      not temporal_data_valid?(action_time, decision_time, valid_from, valid_to, recorded_at) ->
        reject(:invalid_temporal_record, [
          %{
            event: :permission_match_check,
            result: :pass,
            required: required_permission,
            record: permission
          },
          %{
            event: :valid_time_check,
            result: :invalid,
            valid_from: valid_from,
            valid_to: valid_to,
            action_time: action_time
          },
          %{
            event: :transaction_time_check,
            result: :invalid,
            recorded_at: recorded_at,
            decision_time: decision_time
          },
          %{event: :decision, result: :reject}
          | base_trace
        ])

      DateTime.compare(action_time, valid_from) == :lt ->
        reject(:authorization_not_yet_valid, [
          %{
            event: :permission_match_check,
            result: :pass,
            required: required_permission,
            record: permission
          },
          %{
            event: :valid_time_check,
            result: :fail,
            reason: :before_valid_from,
            valid_from: valid_from,
            valid_to: valid_to,
            action_time: action_time
          },
          %{
            event: :transaction_time_check,
            result: :skipped,
            reason: :valid_time_failed,
            recorded_at: recorded_at,
            decision_time: decision_time
          },
          %{event: :decision, result: :reject}
          | base_trace
        ])

      DateTime.compare(action_time, valid_to) == :gt ->
        reject(:authorization_expired, [
          %{
            event: :permission_match_check,
            result: :pass,
            required: required_permission,
            record: permission
          },
          %{
            event: :valid_time_check,
            result: :fail,
            reason: :after_valid_to,
            valid_from: valid_from,
            valid_to: valid_to,
            action_time: action_time
          },
          %{
            event: :transaction_time_check,
            result: :skipped,
            reason: :valid_time_failed,
            recorded_at: recorded_at,
            decision_time: decision_time
          },
          %{event: :decision, result: :reject}
          | base_trace
        ])

      DateTime.compare(recorded_at, decision_time) == :gt ->
        reject(:authorization_valid_but_unknown_at_decision_time, [
          %{
            event: :permission_match_check,
            result: :pass,
            required: required_permission,
            record: permission
          },
          %{
            event: :valid_time_check,
            result: :pass,
            valid_from: valid_from,
            valid_to: valid_to,
            action_time: action_time
          },
          %{
            event: :transaction_time_check,
            result: :fail,
            reason: :recorded_after_decision,
            recorded_at: recorded_at,
            decision_time: decision_time
          },
          %{event: :decision, result: :reject}
          | base_trace
        ])

      true ->
        {:ok,
         %{
           status: :accepted,
           stop_reason: :authorization_valid_and_known,
           action: action,
           permission_record: permission_record,
           trace:
             Enum.reverse([
               %{event: :decision, result: :accept},
               %{
                 event: :transaction_time_check,
                 result: :pass,
                 recorded_at: recorded_at,
                 decision_time: decision_time
               },
               %{
                 event: :valid_time_check,
                 result: :pass,
                 valid_from: valid_from,
                 valid_to: valid_to,
                 action_time: action_time
               },
               %{
                 event: :permission_match_check,
                 result: :pass,
                 required: required_permission,
                 record: permission
               }
               | base_trace
             ])
         }}
    end
  end

  def evaluate(_action, _permission_record) do
    reject(:invalid_temporal_record, [
      %{event: :proposed_action, result: :invalid_input_shape},
      %{event: :decision, result: :reject}
    ])
  end

  defp reject(stop_reason, trace) do
    {:error,
     %{
       status: :rejected,
       stop_reason: stop_reason,
       trace: Enum.reverse(trace)
     }}
  end

  defp fetch(map, key), do: Map.get(map, key) || Map.get(map, Atom.to_string(key))

  defp matching_permission?(required_permission, permission) do
    is_binary(required_permission) and required_permission != "" and
      required_permission == permission
  end

  defp temporal_data_valid?(action_time, decision_time, valid_from, valid_to, recorded_at) do
    Enum.all?(
      [action_time, decision_time, valid_from, valid_to, recorded_at],
      &is_struct(&1, DateTime)
    ) and
      DateTime.compare(valid_from, valid_to) != :gt
  end
end
