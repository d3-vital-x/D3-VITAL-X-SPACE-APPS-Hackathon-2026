# ============================================================
# D³ VITAL-X SPACE INTELLIGENCE PLATFORM
# Module: qc_engine.py
#
# Public Quality-Control Layer
#
# Purpose:
#   Perform lightweight, transparent input-quality checks
#   before data is passed to the intelligence interface.
#
# This module performs:
#   - basic structure checks
#   - missing-value checks
#   - NaN checks
#   - infinite-value checks
#   - negative-value flagging
#   - duplicate-value flagging
#   - basic time-series consistency checks
#   - input integrity metadata handling
#
# This module does NOT perform:
#   - UTL calculations
#   - v10/v11 engine execution
#   - anomaly classification
#   - scientific interpretation
#   - clinical diagnosis
#   - proprietary feature extraction
#
# Architecture:
#
#   Input Adapter
#        │
#        ▼
#   QC Engine
#        │
#        ▼
#   Engine Interface
#        │
#        ▼
#   Protected Intelligence Service
#
# ============================================================

from datetime import datetime, timezone
import math
from typing import Any, Dict


# ============================================================
# VERSION
# ============================================================

QC_VERSION = "0.1.0"


# ============================================================
# BASIC TYPE HELPERS
# ============================================================

def is_numeric_value(value: Any) -> bool:
    """
    Return True when value is a numeric scalar.

    Boolean values are intentionally excluded because Python
    treats bool as a subclass of int.
    """

    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
    )


def is_nan_value(value: Any) -> bool:
    """
    Safely detect NaN values.
    """

    try:
        return bool(math.isnan(value))
    except (TypeError, ValueError):
        return False


def is_infinite_value(value: Any) -> bool:
    """
    Safely detect positive or negative infinity.
    """

    try:
        return bool(math.isinf(value))
    except (TypeError, ValueError):
        return False


# ============================================================
# QC REPORT CREATION
# ============================================================

def create_qc_report(
    dataset_id: Any = None,
) -> Dict[str, Any]:
    """
    Create a standardized public QC report.
    """

    return {
        "qc_version": QC_VERSION,

        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),

        "dataset_id": dataset_id,

        "overall_status": "NOT_EVALUATED",

        "summary": {
            "total_checks": 0,
            "passed_checks": 0,
            "warning_count": 0,
            "error_count": 0,
        },

        "checks": [],

        "flags": [],

        # Public integrity statement.
        "raw_data_modified": False,

        # Explicit boundary declarations.
        "scientific_validation_performed": False,
        "clinical_diagnosis_performed": False,
    }


# ============================================================
# ADD QC CHECK
# ============================================================

def add_qc_check(
    report: Dict[str, Any],
    check_name: str,
    passed: bool,
    severity: str = "INFO",
    message: str = "",
    details: Dict[str, Any] | None = None,
) -> None:
    """
    Add one check to the QC report.
    """

    severity = str(severity).upper()

    if severity not in {
        "INFO",
        "WARNING",
        "ERROR",
    }:
        raise ValueError(
            f"Unsupported severity: {severity}"
        )

    details = details or {}

    check = {
        "check_name": check_name,
        "passed": bool(passed),
        "severity": severity,
        "message": message,
        "details": details,
    }

    report["checks"].append(check)

    report["summary"]["total_checks"] += 1

    if passed:
        report["summary"]["passed_checks"] += 1

    if severity == "WARNING":
        report["summary"]["warning_count"] += 1

    if severity == "ERROR":
        report["summary"]["error_count"] += 1

    # A warning/error or failed check is surfaced as a flag.
    if (
        not passed
        or severity in {"WARNING", "ERROR"}
    ):
        report["flags"].append({
            "check_name": check_name,
            "severity": severity,
            "message": message,
            "details": details,
        })


# ============================================================
# VALUE INSPECTION
# ============================================================

def inspect_values(
    data: Any,
    path: str = "root",
) -> Dict[str, Any]:
    """
    Recursively inspect a basic Python data structure.

    This is intentionally lightweight and transparent.

    It does not calculate scientific metrics.
    """

    result = {
        "total_values": 0,
        "missing_values": 0,
        "nan_values": 0,
        "infinite_values": 0,
        "negative_values": 0,
        "non_numeric_values": 0,

        "negative_value_paths": [],
        "nan_value_paths": [],
        "infinite_value_paths": [],
    }

    def visit(
        value: Any,
        current_path: str,
    ) -> None:

        # ----------------------------------------------------
        # Dictionary
        # ----------------------------------------------------

        if isinstance(value, dict):

            for key, item in value.items():

                visit(
                    item,
                    f"{current_path}.{key}",
                )

            return

        # ----------------------------------------------------
        # List / tuple
        # ----------------------------------------------------

        if isinstance(value, (list, tuple)):

            for index, item in enumerate(value):

                visit(
                    item,
                    f"{current_path}[{index}]",
                )

            return

        # ----------------------------------------------------
        # Scalar
        # ----------------------------------------------------

        result["total_values"] += 1

        # Missing
        if value is None:

            result["missing_values"] += 1
            return

        # NaN
        if is_nan_value(value):

            result["nan_values"] += 1

            if len(
                result["nan_value_paths"]
            ) < 20:

                result[
                    "nan_value_paths"
                ].append(current_path)

            return

        # Infinite
        if is_infinite_value(value):

            result["infinite_values"] += 1

            if len(
                result["infinite_value_paths"]
            ) < 20:

                result[
                    "infinite_value_paths"
                ].append(current_path)

            return

        # Numeric
        if is_numeric_value(value):

            if value < 0:

                result["negative_values"] += 1

                if len(
                    result["negative_value_paths"]
                ) < 20:

                    result[
                        "negative_value_paths"
                    ].append(current_path)

        else:

            result["non_numeric_values"] += 1

    visit(data, path)

    return result


# ============================================================
# MISSING VALUE CHECK
# ============================================================

def run_missing_value_check(
    report: Dict[str, Any],
    inspection: Dict[str, Any],
) -> None:

    count = inspection["missing_values"]

    add_qc_check(
        report=report,
        check_name="missing_values",
        passed=(count == 0),
        severity=(
            "ERROR"
            if count > 0
            else "INFO"
        ),
        message=(
            "Missing values detected."
            if count > 0
            else "No missing values detected."
        ),
        details={
            "count": count,
        },
    )


# ============================================================
# NaN CHECK
# ============================================================

def run_nan_check(
    report: Dict[str, Any],
    inspection: Dict[str, Any],
) -> None:

    count = inspection["nan_values"]

    add_qc_check(
        report=report,
        check_name="nan_values",
        passed=(count == 0),
        severity=(
            "ERROR"
            if count > 0
            else "INFO"
        ),
        message=(
            "NaN values detected."
            if count > 0
            else "No NaN values detected."
        ),
        details={
            "count": count,
            "paths": inspection[
                "nan_value_paths"
            ],
        },
    )


# ============================================================
# INFINITE VALUE CHECK
# ============================================================

def run_infinite_check(
    report: Dict[str, Any],
    inspection: Dict[str, Any],
) -> None:

    count = inspection["infinite_values"]

    add_qc_check(
        report=report,
        check_name="infinite_values",
        passed=(count == 0),
        severity=(
            "ERROR"
            if count > 0
            else "INFO"
        ),
        message=(
            "Infinite values detected."
            if count > 0
            else "No infinite values detected."
        ),
        details={
            "count": count,
            "paths": inspection[
                "infinite_value_paths"
            ],
        },
    )


# ============================================================
# NEGATIVE VALUE CHECK
# ============================================================

def run_negative_value_check(
    report: Dict[str, Any],
    inspection: Dict[str, Any],
) -> None:

    count = inspection["negative_values"]

    # Negative values are NOT automatically invalid.
    # They are flagged for contextual review only.

    add_qc_check(
        report=report,
        check_name="negative_values",
        passed=True,
        severity=(
            "WARNING"
            if count > 0
            else "INFO"
        ),
        message=(
            "Negative numeric values detected; "
            "contextual review recommended."
            if count > 0
            else "No negative numeric values detected."
        ),
        details={
            "count": count,
            "policy": "FLAG_ONLY",
            "paths": inspection[
                "negative_value_paths"
            ],
        },
    )


# ============================================================
# DUPLICATE CHECK
# ============================================================

def run_duplicate_check(
    report: Dict[str, Any],
    data: Any,
) -> None:

    duplicate_count = 0
    sequence_length = 0

    if isinstance(data, (list, tuple)):

        sequence_length = len(data)

        comparable_values = []

        for value in data:

            if isinstance(
                value,
                (str, int, float, bool),
            ):

                comparable_values.append(
                    repr(value)
                )

        duplicate_count = (
            len(comparable_values)
            - len(set(comparable_values))
        )

    has_duplicates = (
        duplicate_count > 0
    )

    add_qc_check(
        report=report,
        check_name="duplicate_values",
        passed=True,
        severity=(
            "WARNING"
            if has_duplicates
            else "INFO"
        ),
        message=(
            "Repeated scalar values detected; "
            "contextual review recommended."
            if has_duplicates
            else "No duplicate scalar values detected."
        ),
        details={
            "sequence_length": sequence_length,
            "duplicate_count": duplicate_count,
            "policy": "FLAG_ONLY",
        },
    )


# ============================================================
# TIME-SERIES STRUCTURE CHECK
# ============================================================

def run_time_series_check(
    report: Dict[str, Any],
    data: Any,
) -> None:
    """
    Perform basic checks when data contains
    conventional 'time' and 'signal' fields.
    """

    if not isinstance(data, dict):

        add_qc_check(
            report=report,
            check_name="time_series_structure",
            passed=True,
            severity="INFO",
            message=(
                "Input is not a dictionary-based "
                "time-series structure."
            ),
        )

        return

    time_values = data.get("time")
    signal_values = data.get("signal")

    # --------------------------------------------------------
    # Fields absent
    # --------------------------------------------------------

    if (
        time_values is None
        or signal_values is None
    ):

        add_qc_check(
            report=report,
            check_name="time_series_structure",
            passed=True,
            severity="INFO",
            message=(
                "Conventional time/signal fields "
                "were not both present."
            ),
        )

        return

    # --------------------------------------------------------
    # Type check
    # --------------------------------------------------------

    valid_sequences = (
        isinstance(
            time_values,
            (list, tuple),
        )
        and isinstance(
            signal_values,
            (list, tuple),
        )
    )

    if not valid_sequences:

        add_qc_check(
            report=report,
            check_name="time_series_sequence_type",
            passed=False,
            severity="ERROR",
            message=(
                "Time and signal values must "
                "be list or tuple sequences."
            ),
        )

        return

    # --------------------------------------------------------
    # Length check
    # --------------------------------------------------------

    lengths_match = (
        len(time_values)
        == len(signal_values)
    )

    add_qc_check(
        report=report,
        check_name="time_signal_length_match",
        passed=lengths_match,
        severity=(
            "INFO"
            if lengths_match
            else "ERROR"
        ),
        message=(
            "Time and signal lengths match."
            if lengths_match
            else "Time and signal lengths do not match."
        ),
        details={
            "time_length": len(time_values),
            "signal_length": len(signal_values),
        },
    )

    # --------------------------------------------------------
    # Numeric time check
    # --------------------------------------------------------

    numeric_time = all(
        is_numeric_value(value)
        for value in time_values
    )

    if not numeric_time:

        add_qc_check(
            report=report,
            check_name="time_numeric",
            passed=False,
            severity="WARNING",
            message=(
                "Time sequence contains "
                "non-numeric values."
            ),
        )

        return

    # --------------------------------------------------------
    # Monotonicity check
    # --------------------------------------------------------

    if len(time_values) > 1:

        non_monotonic_count = sum(
            1
            for previous, current in zip(
                time_values,
                time_values[1:],
            )
            if current <= previous
        )

        strictly_increasing = (
            non_monotonic_count == 0
        )

        add_qc_check(
            report=report,
            check_name="time_monotonicity",
            passed=strictly_increasing,
            severity=(
                "INFO"
                if strictly_increasing
                else "WARNING"
            ),
            message=(
                "Time values are strictly increasing."
                if strictly_increasing
                else "Time values are not strictly increasing."
            ),
            details={
                "non_monotonic_count":
                    non_monotonic_count,
            },
        )


# ============================================================
# METADATA CHECK
# ============================================================

def run_metadata_check(
    report: Dict[str, Any],
    metadata: Any,
) -> None:
    """
    Basic metadata presence check.

    No private schema is required.
    """

    if metadata is None:

        add_qc_check(
            report=report,
            check_name="metadata_presence",
            passed=True,
            severity="WARNING",
            message=(
                "No metadata supplied; "
                "traceability may be limited."
            ),
        )

        return

    if isinstance(metadata, dict):

        add_qc_check(
            report=report,
            check_name="metadata_structure",
            passed=True,
            severity="INFO",
            message="Metadata structure is readable.",
            details={
                "field_count": len(metadata),
                "fields": list(
                    metadata.keys()
                )[:20],
            },
        )

    else:

        add_qc_check(
            report=report,
            check_name="metadata_structure",
            passed=False,
            severity="WARNING",
            message=(
                "Metadata is present but is not "
                "a dictionary structure."
            ),
        )


# ============================================================
# OVERALL STATUS
# ============================================================

def finalize_qc_report(
    report: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Determine final public QC status.
    """

    if report["summary"]["error_count"] > 0:

        report["overall_status"] = "REJECTED"

    elif report["summary"]["warning_count"] > 0:

        report["overall_status"] = (
            "PASSED_WITH_WARNINGS"
        )

    else:

        report["overall_status"] = "PASSED"

    return report


# ============================================================
# MAIN QC ENTRY POINT
# ============================================================

def run_qc(
    data: Any,
    metadata: Dict[str, Any] | None = None,
    dataset_id: Any = None,
) -> Dict[str, Any]:
    """
    Run public input-quality checks.

    Parameters
    ----------
    data :
        Parsed input data.

    metadata :
        Optional public metadata dictionary.

    dataset_id :
        Optional dataset identifier.

    Returns
    -------
    dict
        Standardized QC report.

    IMPORTANT:
        This function performs input-quality checks only.
        It does not perform scientific interpretation.
    """

    report = create_qc_report(
        dataset_id=dataset_id
    )

    # --------------------------------------------------------
    # Basic payload presence
    # --------------------------------------------------------

    if data is None:

        add_qc_check(
            report=report,
            check_name="data_presence",
            passed=False,
            severity="ERROR",
            message="No data payload supplied.",
        )

        report[
            "raw_data_modified"
        ] = False

        return finalize_qc_report(
            report
        )

    add_qc_check(
        report=report,
        check_name="data_presence",
        passed=True,
        severity="INFO",
        message="Data payload received.",
    )

    # --------------------------------------------------------
    # Recursive value inspection
    # --------------------------------------------------------

    inspection = inspect_values(data)

    run_missing_value_check(
        report,
        inspection,
    )

    run_nan_check(
        report,
        inspection,
    )

    run_infinite_check(
        report,
        inspection,
    )

    run_negative_value_check(
        report,
        inspection,
    )

    run_duplicate_check(
        report,
        data,
    )

    run_time_series_check(
        report,
        data,
    )

    # --------------------------------------------------------
    # Metadata
    # --------------------------------------------------------

    run_metadata_check(
        report,
        metadata,
    )

    # --------------------------------------------------------
    # Public boundary declarations
    # --------------------------------------------------------

    report[
        "raw_data_modified"
    ] = False

    report[
        "scientific_validation_performed"
    ] = False

    report[
        "clinical_diagnosis_performed"
    ] = False

    # --------------------------------------------------------
    # Final status
    # --------------------------------------------------------

    return finalize_qc_report(
        report
    )


# ============================================================
# SIMPLE SELF-TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print(
        "D³ VITAL-X — PUBLIC QC ENGINE SELF-TEST"
    )
    print("=" * 60)

    # --------------------------------------------------------
    # Test 1: Clean time-series
    # --------------------------------------------------------

    clean_data = {
        "time": [0, 1, 2, 3, 4],
        "signal": [
            1.0,
            1.2,
            1.4,
            1.3,
            1.5,
        ],
    }

    clean_report = run_qc(
        data=clean_data,
        metadata={
            "source": "demo",
            "mode": "time-series",
        },
        dataset_id="DEMO-001",
    )

    print("\n[TEST 1 — CLEAN DATA]")
    print(
        "Status:",
        clean_report["overall_status"],
    )

    # --------------------------------------------------------
    # Test 2: Problematic data
    # --------------------------------------------------------

    problematic_data = {
        "time": [0, 2, 1, 3],
        "signal": [
            1.0,
            float("nan"),
            float("inf"),
            -2.0,
        ],
    }

    problematic_report = run_qc(
        data=problematic_data,
        metadata={
            "source": "demo",
            "mode": "time-series",
        },
        dataset_id="DEMO-002",
    )

    print("\n[TEST 2 — QC FLAGS]")
    print(
        "Status:",
        problematic_report["overall_status"],
    )

    print(
        "Warnings:",
        problematic_report[
            "summary"
        ]["warning_count"],
    )

    print(
        "Errors:",
        problematic_report[
            "summary"
        ]["error_count"],
    )

    # --------------------------------------------------------
    # Test 3: Empty input
    # --------------------------------------------------------

    empty_report = run_qc(
        data=None,
        dataset_id="DEMO-003",
    )

    print("\n[TEST 3 — EMPTY INPUT]")
    print(
        "Status:",
        empty_report["overall_status"],
    )

    # --------------------------------------------------------
    # Final
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("PUBLIC QC ENGINE SELF-TEST COMPLETE")
    print("=" * 60)
