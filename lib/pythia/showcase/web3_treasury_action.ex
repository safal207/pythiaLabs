defmodule Pythia.Showcase.Web3TreasuryAction do
  @moduledoc """
  Deterministic in-memory showcase for Web3 DAO treasury action reasoning.
  """

  @required_governance_fields [
    :proposal_id,
    :permission,
    :quorum_met,
    :voting_closed_at,
    :timelock_until,
    :authorization_valid_from,
    :authorization_valid_to,
    :authorization_recorded_at,
    :transfer_expires_at
  ]

  @accepted_trace [
    :proposed_action,
    :proposal_match_check,
    :permission_check,
    :quorum_check,
    :voting_window_check,
    :timelock_check,
    :authorization_valid_time_check,
    :authorization_transaction_time_check,
    :transfer_expiration_check,
    :decision
  ]

  @spec evaluate(map(), map()) :: {:ok, map()} | {:error, map()}
  def evaluate(action, governance_record) when is_map(action) and is_map(governance_record) do
    with :ok <- validate_governance_record(governance_record),
         :ok <- validate_action_timestamps(action),
         :ok <- proposal_match_check(action, governance_record),
         :ok <- permission_check(action, governance_record),
         :ok <- quorum_check(governance_record),
         :ok <- voting_window_check(action, governance_record),
         :ok <- timelock_check(action, governance_record),
         :ok <- authorization_valid_time_check(action, governance_record),
         :ok <- authorization_transaction_time_check(action, governance_record),
         :ok <- transfer_expiration_check(action, governance_record) do
      {:ok,
       %{
         status: :accepted,
         stop_reason: :treasury_transfer_accepted,
         trace: @accepted_trace
       }}
    else
      {:error, reason, failed_check} ->
        reject(reason, build_rejected_trace(failed_check))
    end
  end

  def evaluate(_action, _governance_record) do
    reject(:invalid_governance_record, [:proposed_action, :decision])
  end

  defp build_rejected_trace(failed_check) do
    @accepted_trace
    |> Enum.take_while(&(&1 != failed_check))
    |> Kernel.++([failed_check, :decision])
  end

  defp validate_governance_record(governance_record) do
    with true <- Enum.all?(@required_governance_fields, &Map.has_key?(governance_record, &1)),
         true <- is_binary(fetch(governance_record, :proposal_id)),
         true <- is_binary(fetch(governance_record, :permission)),
         true <- is_boolean(fetch(governance_record, :quorum_met)),
         voting_closed_at when is_struct(voting_closed_at, DateTime) <-
           fetch(governance_record, :voting_closed_at),
         timelock_until when is_struct(timelock_until, DateTime) <-
           fetch(governance_record, :timelock_until),
         authorization_valid_from when is_struct(authorization_valid_from, DateTime) <-
           fetch(governance_record, :authorization_valid_from),
         authorization_valid_to when is_struct(authorization_valid_to, DateTime) <-
           fetch(governance_record, :authorization_valid_to),
         authorization_recorded_at when is_struct(authorization_recorded_at, DateTime) <-
           fetch(governance_record, :authorization_recorded_at),
         transfer_expires_at when is_struct(transfer_expires_at, DateTime) <-
           fetch(governance_record, :transfer_expires_at),
         true <- DateTime.compare(authorization_valid_from, authorization_valid_to) != :gt,
         true <- DateTime.compare(voting_closed_at, transfer_expires_at) != :gt,
         true <- DateTime.compare(timelock_until, transfer_expires_at) != :gt do
      :ok
    else
      _ -> {:error, :invalid_governance_record, :proposal_match_check}
    end
  end

  defp validate_action_timestamps(action) do
    action_time = fetch(action, :action_time)
    decision_time = fetch(action, :decision_time)

    if is_struct(action_time, DateTime) and is_struct(decision_time, DateTime) do
      :ok
    else
      {:error, :invalid_governance_record, :voting_window_check}
    end
  end

  defp proposal_match_check(action, governance_record) do
    case fetch(action, :proposal_id) == fetch(governance_record, :proposal_id) do
      true -> :ok
      false -> {:error, :missing_proposal_record, :proposal_match_check}
    end
  end

  defp permission_check(action, governance_record) do
    case fetch(action, :required_permission) == fetch(governance_record, :permission) do
      true -> :ok
      false -> {:error, :permission_mismatch, :permission_check}
    end
  end

  defp quorum_check(governance_record) do
    case fetch(governance_record, :quorum_met) do
      true -> :ok
      false -> {:error, :quorum_not_met, :quorum_check}
    end
  end

  defp voting_window_check(action, governance_record) do
    action_time = fetch(action, :action_time)
    voting_closed_at = fetch(governance_record, :voting_closed_at)

    if DateTime.compare(action_time, voting_closed_at) == :lt do
      {:error, :voting_window_still_open, :voting_window_check}
    else
      :ok
    end
  end

  defp timelock_check(action, governance_record) do
    action_time = fetch(action, :action_time)
    timelock_until = fetch(governance_record, :timelock_until)

    if DateTime.compare(action_time, timelock_until) == :lt do
      {:error, :timelock_not_satisfied, :timelock_check}
    else
      :ok
    end
  end

  defp authorization_valid_time_check(action, governance_record) do
    action_time = fetch(action, :action_time)
    authorization_valid_from = fetch(governance_record, :authorization_valid_from)
    authorization_valid_to = fetch(governance_record, :authorization_valid_to)

    cond do
      DateTime.compare(action_time, authorization_valid_from) == :lt ->
        {:error, :authorization_not_yet_valid, :authorization_valid_time_check}

      DateTime.compare(action_time, authorization_valid_to) == :gt ->
        {:error, :authorization_expired, :authorization_valid_time_check}

      true ->
        :ok
    end
  end

  defp authorization_transaction_time_check(action, governance_record) do
    decision_time = fetch(action, :decision_time)
    authorization_recorded_at = fetch(governance_record, :authorization_recorded_at)

    if DateTime.compare(authorization_recorded_at, decision_time) == :gt do
      {:error, :authorization_valid_but_unknown_at_decision_time,
       :authorization_transaction_time_check}
    else
      :ok
    end
  end

  defp transfer_expiration_check(action, governance_record) do
    action_time = fetch(action, :action_time)
    transfer_expires_at = fetch(governance_record, :transfer_expires_at)

    if DateTime.compare(action_time, transfer_expires_at) == :gt do
      {:error, :transfer_expired, :transfer_expiration_check}
    else
      :ok
    end
  end

  defp reject(stop_reason, trace) do
    {:error,
     %{
       status: :rejected,
       stop_reason: stop_reason,
       trace: trace
     }}
  end

  defp fetch(map, key), do: Map.get(map, key) || Map.get(map, Atom.to_string(key))
end
