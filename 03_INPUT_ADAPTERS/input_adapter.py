# ============================================================
# D³ VITAL-X SPACE INTELLIGENCE PLATFORM
# Module: input_adapter.py
#
# Purpose:
#   Unified public input layer for scientific data ingestion.
#
# Supported public input modes:
#   - CSV
#   - IMAGE
#   - TIME-SERIES / TXT / DAT
#
# Responsibilities:
#   1. Receive raw input bytes
#   2. Calculate SHA-256 integrity hash
#   3. Perform basic format parsing
#   4. Perform lightweight structural validation
#   5. Return standardized metadata
#
# IMPORTANT:
#   This module does NOT contain:
#   - UTL equations
#   - v10/v11 engine logic
#   - proprietary feature extraction
#   - anomaly-detection algorithms
#   - clinical diagnosis logic
#   - private validation algorithms
#
# Architecture:
#   Public Interface → Input Adapter → QC → Engine Interface
#   → Protected Intelligence Service
#
# ============================================================

import io
import hashlib
from typing import Any, Dict

import pandas as pd
from PIL import Image


# ============================================================
# CONSTANTS
# ============================================================

SUPPORTED_CSV_TYPES = {
    "CSV",
}

SUPPORTED_IMAGE_TYPES = {
    "IMAGE",
    "JPG",
    "JPEG",
    "PNG",
    "TIF",
    "TIFF",
    "WEBP",
    "BMP",
}

SUPPORTED_TIMESERIES_TYPES = {
    "TIME-SERIES",
    "TIMESERIES",
    "TXT",
    "DAT",
}


# ============================================================
# SHA-256 INTEGRITY
# ============================================================

def calculate_sha256(raw_bytes: bytes) -> str:
    """
    Calculate SHA-256 hash of the original input payload.

    Parameters
    ----------
    raw_bytes : bytes
        Original uploaded binary payload.

    Returns
    -------
    str
        SHA-256 hexadecimal digest.
    """

    if not isinstance(raw_bytes, (bytes, bytearray)):
        raise TypeError("raw_bytes must be bytes or bytearray.")

    return hashlib.sha256(bytes(raw_bytes)).hexdigest()


# ============================================================
# STANDARD ERROR RESULT
# ============================================================

def _failed_result(
    message: str,
    input_type: str = "UNKNOWN",
) -> Dict[str, Any]:
    """
    Create a standardized failed-result structure.
    """

    return {
        "status": "FAILED",
        "input_type": input_type,
        "error": message,
    }


# ============================================================
# CSV PROCESSOR
# ============================================================

def process_csv_bytes(raw_bytes: bytes) -> Dict[str, Any]:
    """
    Parse CSV input from raw bytes.

    This function performs only lightweight structural inspection.
    It does not perform scientific analysis.

    Returns
    -------
    dict
        Parsed dataframe and basic structural metadata.
    """

    try:
        if not raw_bytes:
            return _failed_result(
                "CSV payload is empty.",
                "CSV",
            )

        df = pd.read_csv(io.BytesIO(raw_bytes))

        if df.empty:
            return _failed_result(
                "CSV file contains no data rows.",
                "CSV",
            )

        numeric_columns = (
            df.select_dtypes(include=["number"])
            .columns
            .tolist()
        )

        return {
            "status": "SUCCESS",
            "input_type": "CSV",
            "dataframe": df,
            "num_rows": int(len(df)),
            "num_cols": int(len(df.columns)),
            "columns": [str(column) for column in df.columns],
            "numeric_columns": numeric_columns,
            "has_numeric_data": bool(numeric_columns),
            "error": None,
        }

    except pd.errors.EmptyDataError:
        return _failed_result(
            "CSV file contains no readable data.",
            "CSV",
        )

    except pd.errors.ParserError as exc:
        return _failed_result(
            f"CSV parsing error: {exc}",
            "CSV",
        )

    except Exception as exc:
        return _failed_result(
            f"CSV processing error: {exc}",
            "CSV",
        )


# ============================================================
# IMAGE PROCESSOR
# ============================================================

def process_image_bytes(raw_bytes: bytes) -> Dict[str, Any]:
    """
    Parse and validate an image payload.

    The image is opened once for validation and reopened afterward
    so that the returned PIL Image object remains usable.

    No image interpretation or scientific/medical classification
    is performed here.
    """

    try:
        if not raw_bytes:
            return _failed_result(
                "Image payload is empty.",
                "IMAGE",
            )

        image_stream = io.BytesIO(raw_bytes)

        # ----------------------------------------------------
        # First pass: structural validation
        # ----------------------------------------------------

        with Image.open(image_stream) as probe:

            image_format = probe.format
            image_mode = probe.mode
            image_width = probe.width
            image_height = probe.height

            # Force image decoding.
            probe.load()

        # ----------------------------------------------------
        # Second pass: return a usable image object
        # ----------------------------------------------------

        image = Image.open(io.BytesIO(raw_bytes))
        image.load()

        return {
            "status": "SUCCESS",
            "input_type": "IMAGE",
            "image": image,
            "format": image_format,
            "mode": image_mode,
            "width": int(image_width),
            "height": int(image_height),
            "dimensions": (
                int(image_width),
                int(image_height),
            ),
            "error": None,
        }

    except Exception as exc:
        return _failed_result(
            f"Image processing error: {exc}",
            "IMAGE",
        )


# ============================================================
# TIME-SERIES PROCESSOR
# ============================================================

def process_timeseries_bytes(raw_bytes: bytes) -> Dict[str, Any]:
    """
    Perform lightweight parsing of text-based time-series input.

    Supported examples:
        .txt
        .dat

    This public layer intentionally does NOT calculate:
        - entropy
        - variance trends
        - CSI
        - transition metrics
        - anomaly scores
        - UTL quantities

    It only inspects the incoming text structure.
    """

    try:
        if not raw_bytes:
            return _failed_result(
                "Time-series payload is empty.",
                "TIME-SERIES",
            )

        content = raw_bytes.decode(
            "utf-8",
            errors="replace",
        )

        lines = content.splitlines()

        non_empty_lines = [
            line.strip()
            for line in lines
            if line.strip()
        ]

        if not non_empty_lines:
            return _failed_result(
                "Time-series file contains no readable lines.",
                "TIME-SERIES",
            )

        # ----------------------------------------------------
        # Basic numeric-line inspection
        # ----------------------------------------------------

        numeric_line_count = 0

        for line in non_empty_lines:

            # Accept common separators.
            normalized = (
                line.replace(",", " ")
                .replace(";", " ")
                .replace("\t", " ")
            )

            tokens = normalized.split()

            if not tokens:
                continue

            numeric_tokens = 0

            for token in tokens:

                try:
                    float(token)
                    numeric_tokens += 1

                except ValueError:
                    continue

            # A line containing at least one numeric value
            # is considered potentially numeric.
            if numeric_tokens > 0:
                numeric_line_count += 1

        return {
            "status": "SUCCESS",
            "input_type": "TIME-SERIES",
            "raw_text": content,
            "preview_snippet": content[:2000],
            "total_lines": int(len(lines)),
            "non_empty_lines": int(len(non_empty_lines)),
            "numeric_lines": int(numeric_line_count),
            "has_numeric_data": bool(numeric_line_count),
            "error": None,
        }

    except UnicodeDecodeError as exc:
        return _failed_result(
            f"Time-series decoding error: {exc}",
            "TIME-SERIES",
        )

    except Exception as exc:
        return _failed_result(
            f"Time-series processing error: {exc}",
            "TIME-SERIES",
        )


# ============================================================
# INPUT TYPE NORMALIZATION
# ============================================================

def normalize_input_type(input_type: str) -> str:
    """
    Normalize user/application supplied input type.

    Examples
    --------
    'csv'        → 'CSV'
    'image'      → 'IMAGE'
    'jpg'        → 'JPG'
    'time-series'→ 'TIME-SERIES'
    """

    if not isinstance(input_type, str):
        raise TypeError(
            "input_type must be a string."
        )

    normalized = input_type.strip().upper()

    if not normalized:
        raise ValueError(
            "input_type cannot be empty."
        )

    return normalized


# ============================================================
# UNIFIED INPUT LOADER
# ============================================================

def load_input_data(
    raw_bytes: bytes,
    input_type: str,
) -> Dict[str, Any]:
    """
    Unified public entry point for incoming scientific data.

    Parameters
    ----------
    raw_bytes : bytes
        Original binary payload.

    input_type : str
        Input category.

        Supported:
            CSV
            IMAGE
            JPG
            JPEG
            PNG
            TIF
            TIFF
            WEBP
            BMP
            TIME-SERIES
            TIMESERIES
            TXT
            DAT

    Returns
    -------
    dict
        Standardized result containing:

            status
            input_type
            metadata
            parsed content
            error
    """

    # --------------------------------------------------------
    # Validate payload
    # --------------------------------------------------------

    if raw_bytes is None:
        return _failed_result(
            "Input payload is None."
        )

    if not isinstance(raw_bytes, (bytes, bytearray)):
        return _failed_result(
            "Input payload must be bytes or bytearray."
        )

    raw_bytes = bytes(raw_bytes)

    if len(raw_bytes) == 0:
        return _failed_result(
            "Empty data payload received."
        )

    # --------------------------------------------------------
    # Normalize input type
    # --------------------------------------------------------

    try:
        normalized_type = normalize_input_type(
            input_type
        )

    except (TypeError, ValueError) as exc:
        return _failed_result(
            str(exc)
        )

    # --------------------------------------------------------
    # Calculate integrity hash BEFORE parsing
    # --------------------------------------------------------

    sha256_hash = calculate_sha256(
        raw_bytes
    )

    # --------------------------------------------------------
    # Common metadata
    # --------------------------------------------------------

    metadata = {
        "sha256": sha256_hash,
        "size_bytes": int(len(raw_bytes)),
        "input_type": normalized_type,
        "processing_mode": "parse-only",
        "raw_input_modified": False,
    }

    # --------------------------------------------------------
    # Route to appropriate parser
    # --------------------------------------------------------

    if normalized_type in SUPPORTED_CSV_TYPES:

        parsed_result = process_csv_bytes(
            raw_bytes
        )

    elif normalized_type in SUPPORTED_IMAGE_TYPES:

        parsed_result = process_image_bytes(
            raw_bytes
        )

    elif normalized_type in SUPPORTED_TIMESERIES_TYPES:

        parsed_result = process_timeseries_bytes(
            raw_bytes
        )

    else:

        parsed_result = _failed_result(
            (
                f"Unsupported input mode: "
                f"{normalized_type}"
            ),
            normalized_type,
        )

    # --------------------------------------------------------
    # Attach common metadata
    # --------------------------------------------------------

    parsed_result["metadata"] = metadata

    return parsed_result


# ============================================================
# SIMPLE CAPABILITY CHECK
# ============================================================

def is_supported_input_type(
    input_type: str,
) -> bool:
    """
    Return True if the supplied input type is supported
    by the public adapter.
    """

    try:
        normalized_type = normalize_input_type(
            input_type
        )
    except (TypeError, ValueError):
        return False

    return (
        normalized_type in SUPPORTED_CSV_TYPES
        or normalized_type in SUPPORTED_IMAGE_TYPES
        or normalized_type in SUPPORTED_TIMESERIES_TYPES
    )


# ============================================================
# PUBLIC MODULE SELF-TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("D³ VITAL-X — INPUT ADAPTER SELF-TEST")
    print("=" * 60)

    # --------------------------------------------------------
    # CSV test
    # --------------------------------------------------------

    csv_data = (
        b"time,signal\n"
        b"0,1.2\n"
        b"1,1.5\n"
        b"2,1.8\n"
    )

    csv_result = load_input_data(
        csv_data,
        "csv",
    )

    print("\n[CSV]")
    print("Status:", csv_result["status"])
    print("SHA-256:",
          csv_result["metadata"]["sha256"])
    print("Rows:",
          csv_result.get("num_rows"))
    print("Columns:",
          csv_result.get("columns"))

    # --------------------------------------------------------
    # Time-series test
    # --------------------------------------------------------

    timeseries_data = (
        b"0.10\n"
        b"0.20\n"
        b"0.35\n"
        b"0.40\n"
    )

    ts_result = load_input_data(
        timeseries_data,
        "txt",
    )

    print("\n[TIME-SERIES]")
    print("Status:", ts_result["status"])
    print("Numeric lines:",
          ts_result.get("numeric_lines"))

    # --------------------------------------------------------
    # Unsupported input test
    # --------------------------------------------------------

    unsupported_result = load_input_data(
        b"example",
        "UNKNOWN",
    )

    print("\n[UNSUPPORTED]")
    print("Status:",
          unsupported_result["status"])
    print("Error:",
          unsupported_result["error"])

    print("\n" + "=" * 60)
    print("SELF-TEST COMPLETE")
    print("=" * 60)
