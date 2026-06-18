import json
import os
from datetime import datetime


def parse_and_normalize_record(raw_payload, index):
    """
    PHASE 1 HELPER: Key Mapping, Normalization & Data Ingestion
    """
    if not isinstance(raw_payload, dict):
        raise ValueError("Payload must be a dictionary object.")

    raw_time = (
        raw_payload.get("time")
        if raw_payload.get("time") is not None
        else raw_payload.get("t")
    )
    raw_status = raw_payload.get("status") or raw_payload.get("state")

    if raw_time is None or not raw_status:
        raise KeyError(
            "Missing critical time or status fields ('time'/'t' or 'status'/'state')."
        )

    status_str = str(raw_status).upper().strip()
    status_mapping = {"D": "DRIVING", "OFF": "OFF_DUTY", "ON": "ON_DUTY"}
    normalized_status = status_mapping.get(status_str, status_str)

    parsed_datetime = None
    if isinstance(raw_time, (int, float)):
        parsed_datetime = datetime.fromtimestamp(raw_time)
    elif isinstance(raw_time, str):
        raw_time = raw_time.strip()
        if raw_time.isdigit():
            parsed_datetime = datetime.fromtimestamp(int(raw_time))
        else:
            try:
                if raw_time.endswith("Z"):
                    parsed_datetime = datetime.fromisoformat(
                        raw_time.replace("Z", "+00:00")
                    )
                else:
                    parsed_datetime = datetime.fromisoformat(raw_time)
            except ValueError:
                pass

            if not parsed_datetime:
                try:
                    parsed_datetime = datetime.strptime(raw_time, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    pass

    if not parsed_datetime:
        raise ValueError(f"Unrecognized timestamp format or type: '{raw_time}'")

    # Convert offset-aware datetimes to offset-naive by stripping tzinfo
    # This guarantees smooth sorting and delta calculations across differing vendors
    if parsed_datetime.tzinfo is not None:
        parsed_datetime = parsed_datetime.replace(tzinfo=None)
    return {
        "original_index": index,
        "timestamp": parsed_datetime,
        "status": normalized_status,
    }


def process_and_analyze_truck_logs(raw_events):
    """
    MAIN PIPELINE ORCHESTRATOR
    """
    valid_parsed_events = []
    erroneous_records = []

    for index, raw_payload in enumerate(raw_events):
        try:
            normalized_event = parse_and_normalize_record(raw_payload, index)
            valid_parsed_events.append(normalized_event)
        except (ValueError, KeyError, TypeError) as error:
            erroneous_records.append(
                {"index": index, "raw_payload": raw_payload, "error_reason": str(error)}
            )

    valid_parsed_events.sort(key=lambda x: x["timestamp"])

    total_driving_minutes = 0.0
    continuous_driving_minutes = 0.0
    violations = []

    for i in range(len(valid_parsed_events)):
        current_event = valid_parsed_events[i]
        if i + 1 >= len(valid_parsed_events):
            break

        next_event = valid_parsed_events[i + 1]
        interval_minutes = (
            next_event["timestamp"] - current_event["timestamp"]
        ).total_seconds() / 60.0

        if interval_minutes <= 0:
            continue

        if current_event["status"] == "DRIVING":
            total_driving_minutes += interval_minutes
            continuous_driving_minutes += interval_minutes

            if continuous_driving_minutes > 300.0:
                violations.append(
                    f"Violation: Exceeded 300-min driving limit at {next_event['timestamp']} "
                    f"({int(continuous_driving_minutes)} minutes consecutive)"
                )
        elif current_event["status"] == "OFF_DUTY" and interval_minutes >= 30.0:
            continuous_driving_minutes = 0.0

    return {
        "total_driving_time_minutes": round(total_driving_minutes, 2),
        "violations_detected": violations,
        "valid_records_count": len(valid_parsed_events),
        "failed_records_count": len(erroneous_records),
        "erroneous_records": erroneous_records,
    }


if __name__ == "__main__":
    file_path = "mock_stream.json"

    if not os.path.exists(file_path):
        print(f"Error: Run script in the directory containing '{file_path}'")
        exit(1)

    with open(file_path, "r", encoding="utf-8") as f:
        loaded_records = json.load(f)

    analysis = process_and_analyze_truck_logs(loaded_records)

    print(f"Valid Records Parsed : {analysis['valid_records_count']}")
    print(f"Invalid Records Dropped: {analysis['failed_records_count']}")
    print(f"Total Driving Accounted: {analysis['total_driving_time_minutes']} Minutes")

    print("\n--- Compliance Flag Logs ---")
    for violation in analysis["violations_detected"]:
        print(f"[⚠️] {violation}")

    print("\n--- Pipeline Anomaly Drops ---")
    for failure in analysis["erroneous_records"]:
        print(
            f"[❌] Index {failure['index']} dropped. Error: {failure['error_reason']}"
        )
