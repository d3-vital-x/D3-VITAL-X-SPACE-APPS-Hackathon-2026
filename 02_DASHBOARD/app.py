# ============================================================
# D³ VITAL-X SPACE INTELLIGENCE PLATFORM
# Module 57 — app.py
# Functional Streamlit Dashboard Entry Point
#
# Public framework only.
# Proprietary intelligence core is NOT included.
# ============================================================

from pathlib import Path
import sys
import io
import hashlib
import json
import importlib.util
from datetime import datetime, timezone

import streamlit as st


# ============================================================
# PROJECT PATH (DYNAMIC RESOLUTION)
# ============================================================

# Dynamically resolve project root based on app.py location
# app.py resides in 02_DASHBOARD, so parent of 02_DASHBOARD is PROJECT_ROOT
PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))



# ============================================================
# ANALYTICS MODULE CONNECTION — MODULES 18–22
# ============================================================

ANALYTICS_AVAILABLE = False
IMPORT_ERROR_REASON = ""

ANALYTICS_MODULES = {
    "metrics": "metrics.py",
    "transition_analysis": "transition_analysis.py",
    "anomaly_scoring": "anomaly_scoring.py",
    "uncertainty": "uncertainty.py",
    "explainability": "explainability.py",
}

ANALYTICS_IMPORTS = {}


def find_public_module(filename):
    """
    Locate a public analytics module inside the project.

    Private intelligence-core directories are intentionally
    excluded from discovery.
    """

    excluded_parts = {
        "15_PRIVATE_CORE",
        "__pycache__",
        ".git",
        ".venv",
        "venv",
    }

    # --------------------------------------------------------
    # First check project root directly.
    # --------------------------------------------------------

    direct_path = PROJECT_ROOT / filename

    if direct_path.exists() and direct_path.is_file():
        return direct_path

    # --------------------------------------------------------
    # Then search public project directories.
    # --------------------------------------------------------

    for path in PROJECT_ROOT.rglob(filename):

        if not path.is_file():
            continue

        if any(
            part in excluded_parts
            for part in path.parts
        ):
            continue

        return path

    return None


def load_public_module(module_name, filename):
    """
    Dynamically load one public analytics module.

    This loader exposes only public framework modules.
    No proprietary intelligence-core source is imported.
    """

    module_path = find_public_module(filename)

    if module_path is None:
        raise FileNotFoundError(
            f"{filename} was not found inside project root."
        )

    spec = importlib.util.spec_from_file_location(
        module_name,
        module_path,
    )

    if spec is None or spec.loader is None:
        raise ImportError(
            f"Could not create import specification "
            f"for {filename}."
        )

    module = importlib.util.module_from_spec(spec)

    # --------------------------------------------------------
    # Register module before execution.
    # This supports dataclasses and module-level introspection.
    # --------------------------------------------------------

    sys.modules[module_name] = module

    spec.loader.exec_module(module)

    return module


# ------------------------------------------------------------
# LOAD MODULES 18–22
# ------------------------------------------------------------

try:

    for module_name, filename in ANALYTICS_MODULES.items():

        ANALYTICS_IMPORTS[module_name] = load_public_module(
            module_name,
            filename,
        )

    # --------------------------------------------------------
    # Public module handles
    # --------------------------------------------------------

    metrics = ANALYTICS_IMPORTS["metrics"]

    transition_analysis = ANALYTICS_IMPORTS[
        "transition_analysis"
    ]

    anomaly_scoring = ANALYTICS_IMPORTS[
        "anomaly_scoring"
    ]

    uncertainty = ANALYTICS_IMPORTS[
        "uncertainty"
    ]

    explainability = ANALYTICS_IMPORTS[
        "explainability"
    ]

    ANALYTICS_AVAILABLE = True
    IMPORT_ERROR_REASON = ""


except Exception as exc:

    ANALYTICS_AVAILABLE = False

    IMPORT_ERROR_REASON = (
        f"{type(exc).__name__}: {exc}"
    )

# ============================================================
# VISUALIZATION MODULE CONNECTION — MODULES 23–29
# ============================================================

VISUALIZATION_AVAILABLE = False
VISUALIZATION_IMPORT_ERROR = ""

VISUALIZATION_MODULES = {
    "entropy_map": "entropy_map.py",
    "variance_map": "variance_map.py",
    "gradient_map": "gradient_map.py",
    "csi_map": "csi_map.py",
    "anomaly_overlay": "anomaly_overlay.py",
    "timeseries_plot": "timeseries_plot.py",
    "dashboard_metrics": "dashboard_metrics.py",
}

VISUALIZATION_IMPORTS = {}


# ------------------------------------------------------------
# LOAD PUBLIC VISUALIZATION MODULES
# ------------------------------------------------------------

try:

    for module_name, filename in VISUALIZATION_MODULES.items():

        VISUALIZATION_IMPORTS[module_name] = load_public_module(
            module_name,
            filename,
        )

    # --------------------------------------------------------
    # Public visualization module handles
    # --------------------------------------------------------

    entropy_map = VISUALIZATION_IMPORTS[
        "entropy_map"
    ]

    variance_map = VISUALIZATION_IMPORTS[
        "variance_map"
    ]

    gradient_map = VISUALIZATION_IMPORTS[
        "gradient_map"
    ]

    csi_map = VISUALIZATION_IMPORTS[
        "csi_map"
    ]

    anomaly_overlay = VISUALIZATION_IMPORTS[
        "anomaly_overlay"
    ]

    timeseries_plot = VISUALIZATION_IMPORTS[
        "timeseries_plot"
    ]

    dashboard_metrics = VISUALIZATION_IMPORTS[
        "dashboard_metrics"
    ]

    VISUALIZATION_AVAILABLE = True
    VISUALIZATION_IMPORT_ERROR = ""


except Exception as exc:

    VISUALIZATION_AVAILABLE = False

    VISUALIZATION_IMPORT_ERROR = (
        f"{type(exc).__name__}: {exc}"
    )

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="D³ VITAL-X Space Intelligence Platform",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CONSTANTS
# ============================================================

APP_VERSION = "0.1.0-development"

SUPPORTED_PUBLIC_INPUTS = [
    "CSV",
    "Image",
    "Time-Series",
]

PROJECT_STATUS = "ACTIVE DEVELOPMENT"


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def utc_timestamp():
    """Return current UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


def calculate_sha256(data: bytes) -> str:
    """Calculate SHA-256 hash of raw uploaded bytes."""
    return hashlib.sha256(data).hexdigest()


def format_bytes(size):
    """Human-readable file size."""

    if size < 1024:
        return f"{size} B"

    if size < 1024 ** 2:
        return f"{size / 1024:.2f} KB"

    if size < 1024 ** 3:
        return f"{size / 1024 ** 2:.2f} MB"

    return f"{size / 1024 ** 3:.2f} GB"


def detect_input_type(filename):
    """Detect supported public input type from filename."""

    suffix = Path(filename).suffix.lower()

    if suffix == ".csv":
        return "CSV"

    if suffix in [
        ".png",
        ".jpg",
        ".jpeg",
        ".bmp",
        ".tif",
        ".tiff",
        ".webp",
    ]:
        return "IMAGE"

    if suffix in [
        ".txt",
        ".dat",
    ]:
        return "TIME-SERIES"

    return "UNKNOWN"


# ============================================================
# HEADER
# ============================================================

st.title(
    "🛰️ D³ VITAL-X Space Intelligence Platform"
)

st.markdown(
    """
    ### One AI Engine. Multiple Worlds. One Signal Language.
    **Independent research prototype — D³ VITAL-X BANGLADESH**

    This dashboard provides a public interface for scientific
    data ingestion, technical quality assessment, exploratory
    analysis, and visualization.

    > **Development Status: ACTIVE DEVELOPMENT**
    """
)


# ============================================================
# PROJECT STATUS BANNER
# ============================================================

st.info(
    "🔬 This is a work-in-progress research prototype. "
    "Some analytics, NASA integration, biomedical workflows, "
    "live mode, and advanced visualization modules are under development."
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("🛰️ D³ VITAL-X")

    st.caption(
        f"Version: {APP_VERSION}"
    )

    st.divider()

    st.subheader("Navigation")

    page = st.radio(
        "Select Mode",
        [
            "🏠 Home",
            "📥 Data Upload",
            "🔬 Data Quality",
            "📊 Visualization",
            "🛰️ Space Mode",
            "🩻 Biomedical Mode",
            "🎥 Live Mode",
            "ℹ️ About",
        ],
    )

    st.divider()

    st.subheader("System Status")

    st.success(
        "Public Framework: Available"
    )

    st.success(
        "Input Layer: Available"
    )

    st.success(
        "Unified Data Layer: Available"
    )

    # ========================================================
    # MODULES 18–22 STATUS
    # ========================================================

    if ANALYTICS_AVAILABLE:

        st.success(
            "Advanced Analytics (18–22): Connected"
        )

    else:

        st.warning(
            "Advanced Analytics: Disconnected"
        )

        if IMPORT_ERROR_REASON:

            st.caption(
                f"Error: {IMPORT_ERROR_REASON}"
            )

        # ========================================================
    # MODULES 23–29 STATUS
    # ========================================================

    if VISUALIZATION_AVAILABLE:

        st.success(
            "Visualization (23–29): Connected"
        )

    else:

        st.warning(
            "Visualization (23–29): Disconnected"
        )

        if VISUALIZATION_IMPORT_ERROR:

            st.caption(
                f"Error: {VISUALIZATION_IMPORT_ERROR}"
            )
    
    # ========================================================
    # OTHER DEVELOPMENT STATUS
    # ========================================================

    st.warning(
        "NASA Integration: Under Development"
    )

    st.warning(
        "Live Mode: Under Development"
    )

    st.divider()

    st.caption(
        "D³ VITAL-X BANGLADESH"
    )


# ============================================================
# SESSION STATE
# ============================================================

if "uploaded_data" not in st.session_state:

    st.session_state.uploaded_data = None


if "uploaded_name" not in st.session_state:

    st.session_state.uploaded_name = None


if "uploaded_type" not in st.session_state:

    st.session_state.uploaded_type = None


if "uploaded_hash" not in st.session_state:

    st.session_state.uploaded_hash = None


if "uploaded_size" not in st.session_state:

    st.session_state.uploaded_size = None


# ============================================================
# HOME
# ============================================================

if page == "🏠 Home":

    st.header(
        "Welcome to D³ VITAL-X"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Input Modes",
            "3",
        )

    with col2:

        st.metric(
            "Data Layer",
            "Active",
        )

    with col3:

        st.metric(
            "QC Framework",
            "Active",
        )

    with col4:

        st.metric(
            "Development",
            "Ongoing",
        )

    st.divider()

    st.subheader(
        "Current Public Architecture"
    )

    architecture = [
        "Input Adapters",
        "Unified Data Layer",
        "Data Validation",
        "Quality Control",
        "Feature Engine Interface",
        "Analytics",
        "Visualization",
        "Dashboard",
    ]

    for i, item in enumerate(
        architecture,
        start=1,
    ):

        st.write(
            f"**{i}.** {item}"
        )

    st.divider()

    st.subheader(
        "Supported Public Inputs"
    )

    input_col1, input_col2, input_col3 = st.columns(3)

    with input_col1:

        st.info(
            "📄 CSV\n\nStructured scientific data"
        )

    with input_col2:

        st.info(
            "🖼️ Image\n\nScientific image data"
        )

    with input_col3:

        st.info(
            "📈 Time-Series\n\nSignal-based data"
        )

    st.divider()

    st.subheader(
        "Responsible Research"
    )

    st.markdown(
        """
        - Raw input preservation
        - Data provenance
        - Technical validation
        - Quality-control checks
        - Human review
        - Research-oriented anomaly prioritization
        """
    )

    st.warning(
        "This platform is not a clinical diagnostic system, "
        "medical decision tool, or flight-certified spacecraft system."
    )


# ============================================================
# DATA UPLOAD
# ============================================================

elif page == "📥 Data Upload":

    st.header(
        "📥 Data Upload"
    )

    st.write(
        "Upload a supported public input file for technical "
        "inspection and exploratory processing."
    )

    uploaded_file = st.file_uploader(
        "Choose a file",
        type=[
            "csv",
            "png",
            "jpg",
            "jpeg",
            "bmp",
            "tif",
            "tiff",
            "webp",
            "txt",
            "dat",
        ],
    )

    if uploaded_file is not None:

        raw_bytes = uploaded_file.getvalue()

        filename = uploaded_file.name

        input_type = detect_input_type(
            filename
        )

        raw_hash = calculate_sha256(
            raw_bytes
        )

        st.session_state.uploaded_data = raw_bytes

        st.session_state.uploaded_name = filename

        st.session_state.uploaded_type = input_type

        st.session_state.uploaded_hash = raw_hash

        st.session_state.uploaded_size = len(
            raw_bytes
        )

        st.success(
            f"Loaded: {filename}"
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Input Type",
                input_type,
            )

        with col2:

            st.metric(
                "File Size",
                format_bytes(
                    len(raw_bytes)
                ),
            )

        with col3:

            st.metric(
                "Integrity Hash",
                raw_hash[:12] + "...",
            )

        st.divider()

        st.subheader(
            "Raw Input Information"
        )

        metadata = {
            "filename": filename,
            "input_type": input_type,
            "file_size_bytes": len(raw_bytes),
            "sha256": raw_hash,
            "received_at_utc": utc_timestamp(),
            "raw_data_immutable": True,
        }

        st.json(
            metadata
        )

        # ----------------------------------------------------
        # CSV PREVIEW
        # ----------------------------------------------------

        if input_type == "CSV":

            try:

                import pandas as pd

                dataframe = pd.read_csv(
                    io.BytesIO(raw_bytes)
                )

                st.subheader(
                    "CSV Preview"
                )

                st.dataframe(
                    dataframe.head(100),
                    use_container_width=True,
                )

                st.caption(
                    f"Rows: {len(dataframe):,} | "
                    f"Columns: {len(dataframe.columns):,}"
                )

            except Exception as exc:

                st.error(
                    f"CSV preview could not be generated: {exc}"
                )

        # ----------------------------------------------------
        # IMAGE PREVIEW
        # ----------------------------------------------------

        elif input_type == "IMAGE":

            try:

                from PIL import Image

                image = Image.open(
                    io.BytesIO(raw_bytes)
                )

                st.subheader(
                    "Image Preview"
                )

                st.image(
                    image,
                    caption=filename,
                    use_container_width=True,
                )

                st.write(
                    {
                        "format": image.format,
                        "mode": image.mode,
                        "width": image.width,
                        "height": image.height,
                    }
                )

            except Exception as exc:

                st.error(
                    f"Image preview could not be generated: {exc}"
                )

        # ----------------------------------------------------
        # TIME-SERIES PREVIEW
        # ----------------------------------------------------

        elif input_type == "TIME-SERIES":

            st.subheader(
                "Time-Series Input"
            )

            try:

                text_preview = raw_bytes.decode(
                    "utf-8",
                    errors="replace",
                )

                st.code(
                    text_preview[:5000],
                    language="text",
                )

            except Exception as exc:

                st.error(
                    f"Time-series preview failed: {exc}"
                )

    else:

        st.info(
            "Upload a CSV, image, or supported time-series "
            "file to begin."
        )


# ============================================================
# DATA QUALITY
# ============================================================

elif page == "🔬 Data Quality":

    st.header(
        "🔬 Data Quality & Integrity"
    )

    if st.session_state.uploaded_data is None:

        st.info(
            "Please upload a dataset from the Data Upload page first."
        )

    else:

        raw_bytes = (
            st.session_state.uploaded_data
        )

        st.success(
            "Raw input received."
        )

        checks = {
            "File received": True,
            "Raw data preserved": True,
            "SHA-256 generated": True,
            "Input type detected": (
                st.session_state.uploaded_type
                != "UNKNOWN"
            ),
            "Human review available": True,
        }

        for check_name, result in checks.items():

            if result:

                st.success(
                    f"✓ {check_name}"
                )

            else:

                st.error(
                    f"✗ {check_name}"
                )

        st.divider()

        st.subheader(
            "Provenance"
        )

        st.json(
            {
                "source_name": (
                    st.session_state.uploaded_name
                ),
                "input_type": (
                    st.session_state.uploaded_type
                ),
                "size_bytes": (
                    st.session_state.uploaded_size
                ),
                "sha256": (
                    st.session_state.uploaded_hash
                ),
                "received_at_utc": utc_timestamp(),
                "raw_data_immutable": True,
            }
        )

        st.divider()

        st.caption(
            "Quality-control results shown here are technical "
            "checks and should not be interpreted as scientific "
            "or medical conclusions."
        )


# ============================================================
# VISUALIZATION
# ============================================================

elif page == "📊 Visualization":

    st.header(
        "📊 Visualization"
    )

    if st.session_state.uploaded_data is None:

        st.info(
            "Upload a dataset first to generate exploratory visualization."
        )

    else:

        input_type = (
            st.session_state.uploaded_type
        )

        raw_bytes = (
            st.session_state.uploaded_data
        )

        if input_type == "CSV":

            try:

                import pandas as pd
                import matplotlib.pyplot as plt

                dataframe = pd.read_csv(
                    io.BytesIO(raw_bytes)
                )

                numeric_columns = (
                    dataframe
                    .select_dtypes(
                        include="number"
                    )
                    .columns
                    .tolist()
                )

                if numeric_columns:

                    selected_column = st.selectbox(
                        "Select numeric signal",
                        numeric_columns,
                    )

                    fig = plt.figure()

                    plt.plot(
                        dataframe[
                            selected_column
                        ].values
                    )

                    plt.title(
                        f"Exploratory Signal: "
                        f"{selected_column}"
                    )

                    plt.xlabel(
                        "Sample"
                    )

                    plt.ylabel(
                        selected_column
                    )

                    st.pyplot(
                        fig
                    )

                    st.caption(
                        "Exploratory visualization only."
                    )

                else:

                    st.warning(
                        "No numeric columns were detected."
                    )

            except Exception as exc:

                st.error(
                    f"Visualization failed: {exc}"
                )

        elif input_type == "IMAGE":

            try:

                from PIL import Image

                image = Image.open(
                    io.BytesIO(raw_bytes)
                )

                st.image(
                    image,
                    caption="Input Image",
                    use_container_width=True,
                )

            except Exception as exc:

                st.error(
                    f"Image visualization failed: {exc}"
                )

        else:

            st.info(
                "Advanced time-series visualization "
                "is under development."
            )

                # ====================================================
        # MODULE 29 — DASHBOARD METRICS
        # ====================================================

        st.divider()

        st.subheader(
            "📊 Dashboard Metrics"
        )

        if VISUALIZATION_AVAILABLE:

            try:

                # ------------------------------------------------
                # Build public dashboard summary
                # ------------------------------------------------

                dashboard = dashboard_metrics.build_dashboard_metrics(
                    dataset_id=(
                        st.session_state.uploaded_hash
                        or "uploaded-dataset"
                    ),
                    title=(
                        "D³ VITAL-X "
                        "Exploratory Dashboard"
                    ),
                    provenance={
                        "source_name": (
                            st.session_state.uploaded_name
                        ),
                        "input_type": (
                            st.session_state.uploaded_type
                        ),
                        "sha256": (
                            st.session_state.uploaded_hash
                        ),
                        "presentation_only": True,
                    },
                )

                # ------------------------------------------------
                # Dashboard state
                # ------------------------------------------------

                status_col1, status_col2, status_col3 = (
                    st.columns(3)
                )

                with status_col1:

                    st.metric(
                        "Dashboard Status",
                        dashboard.overall_status.value.upper(),
                    )

                with status_col2:

                    st.metric(
                        "Data Quality",
                        dashboard.data_quality.value.upper(),
                    )

                with status_col3:

                    st.metric(
                        "Review Required",
                        "YES"
                        if dashboard.review_required
                        else "NO",
                    )

                # ------------------------------------------------
                # Metric cards
                # ------------------------------------------------

                if dashboard.cards:

                    st.markdown(
                        "#### Public Metric Summary"
                    )

                    # Display cards in rows of 4
                    cards = dashboard.cards

                    for start in range(
                        0,
                        len(cards),
                        4,
                    ):

                        row = cards[
                            start:start + 4
                        ]

                        columns = st.columns(
                            len(row)
                        )

                        for column, card in zip(
                            columns,
                            row,
                        ):

                            with column:

                                display_value = (
                                    dashboard_metrics
                                    .format_metric_value(
                                        card
                                    )
                                )

                                st.metric(
                                    card.label,
                                    display_value,
                                )

                                if (
                                    card.status.value
                                    == "review"
                                ):

                                    st.caption(
                                        "🔎 Human review"
                                    )

                                elif (
                                    card.status.value
                                    == "warning"
                                ):

                                    st.caption(
                                        "⚠️ Review indicator"
                                    )

                                else:

                                    st.caption(
                                        "ℹ️ "
                                        "Computational indicator"
                                    )

                else:

                    st.info(
                        "No public dashboard metrics are "
                        "available for the current input yet."
                    )

                # ------------------------------------------------
                # Responsible interpretation
                # ------------------------------------------------

                st.info(
                    "ℹ️ Dashboard metrics are computational "
                    "indicators supplied by the public analytics "
                    "layer. They do not establish physical "
                    "causality, medical diagnosis, or operational "
                    "failure."
                )

            except Exception as exc:

                st.warning(
                    "Dashboard Metrics could not be generated "
                    "for this input."
                )

                st.caption(
                    f"{type(exc).__name__}: {exc}"
                )

        else:

            st.warning(
                "Visualization modules are currently disconnected."
            )


# ============================================================
# SPACE MODE
# ============================================================

elif page == "🛰️ Space Mode":

    st.header(
        "🛰️ NASA / Space Mode"
    )

    st.info(
        "Space Mode is an active development area."
    )

    st.subheader(
        "Planned Public Workflow"
    )

    st.write(
        """
        NASA dataset → Input Adapter → Unified Data Layer → Technical QC → Feature Interface → Analytics → Visualization
        """
    )

    st.divider()

    st.subheader(
        "NASA Data Integration"
    )

    st.warning(
        "NASA dataset loaders and space-specific processing "
        "modules are currently under development."
    )

    st.markdown(
        """
        Planned sources include compatible NASA open datasets
        and NASA API-accessible data products.
        """
    )


# ============================================================
# BIOMEDICAL MODE
# ============================================================

elif page == "🩻 Biomedical Mode":

    st.header(
        "🩻 Biomedical Research Mode"
    )

    st.info(
        "Biomedical functionality is intended for research "
        "validation and technical data exploration."
    )

    st.subheader(
        "Current Scope"
    )

    st.markdown(
        """
        - Image and structured-data exploration
        - Technical quality assessment
        - Research visualization
        - Human review
        """
    )

    st.warning(
        "This platform does not provide clinical diagnosis, "
        "medical advice, or automated disease detection."
    )

    st.caption(
        "DICOM adapter and biomedical validation modules are under development."
    )


# ============================================================
# LIVE MODE
# ============================================================

elif page == "🎥 Live Mode":

    st.header(
        "🎥 Live / Demonstration Mode"
    )

    st.info(
        "Live imaging is planned as an optional demonstration mode."
    )

    st.subheader(
        "Development Status"
    )

    st.warning(
        "Video adapter, stream controller, frame processor, "
        "live metrics, and live heatmap modules are under development."
    )

    st.caption(
        "Live mode is a research demonstration and is not a "
        "clinical or operational diagnostic system."
    )


# ============================================================
# ABOUT
# ============================================================

elif page == "ℹ️ About":

    st.header(
        "ℹ️ About D³ VITAL-X"
    )

    st.markdown(
        """
        ### D³ VITAL-X Space Intelligence Platform
        **D³ VITAL-X BANGLADESH**

        An independent research-oriented prototype designed to
        support scientific data exploration through a unified,
        lightweight framework.

        ### Current Focus

        - Scientific data ingestion
        - Unified data representation
        - Technical validation
        - Quality control
        - Exploratory visualization
        - Human-centered anomaly prioritization

        ### Development Status

        **ACTIVE DEVELOPMENT**

        The public repository contains framework components and
        interfaces. Proprietary intelligence-core implementation
        is not publicly exposed.
        """
    )

    st.divider()

    st.subheader(
        "Responsible Use"
    )

    st.warning(
        "Research prototype only. Not a clinical diagnostic system, "
        "medical decision tool, or flight-certified spacecraft system."
    )

    st.divider()

    st.caption(
        "D³ VITAL-X BANGLADESH • NASA Space Apps Challenge 2026"
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "D³ VITAL-X Space Intelligence Platform | "
    "Independent Research Prototype | "
    f"{PROJECT_STATUS}"
)
