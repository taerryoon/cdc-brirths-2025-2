"""Configuration constants, mappings, and styling tokens for CDC Natality Dashboard."""

from pathlib import Path

# --- File Paths ---
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "Data"
DEFAULT_DATA_PATH = DATA_DIR / "Provisional_Natality_2025_CDC.xlsx"

# --- Metadata & Attributions ---
APP_TITLE = "U.S. Provisional Natality Analytics (2025)"
APP_SUBTITLE = "An interactive exploration of 2025 U.S. birth counts across states, months, and infant sex."
CDC_ATTRIBUTION = "Data Source: Centers for Disease Control and Prevention (CDC) National Center for Health Statistics (NCHS) - Provisional Natality Data (2025)."
PROVISIONAL_NOTICE = "NOTICE: These data are provisional and subject to monthly reporting delays and revisions before final official publication."
COUNT_VS_RATE_NOTICE = "CRITICAL ANALYTICAL DISTINCTION: Figures shown are raw birth counts (absolute volume), NOT birth rates. State differences strongly reflect underlying population size rather than per-capita fertility rates."

# --- Chronological Month Ordering ---
MONTH_ORDER = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

MONTH_CODE_TO_NAME = {i: month for i, month in enumerate(MONTH_ORDER, start=1)}
MONTH_NAME_TO_CODE = {month: i for i, month in enumerate(MONTH_ORDER, start=1)}

# --- State to 2-Letter Abbreviation Mapping (50 States + DC) ---
US_STATE_TO_ABBR = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "District of Columbia": "DC",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
}

ABBR_TO_US_STATE = {v: k for k, v in US_STATE_TO_ABBR.items()}

# --- Accessible Visual Palette Tokens ---
COLORS = {
    "primary": "#1E3A8A",      # Deep Navy Blue
    "secondary": "#0284C7",    # Cerulean Blue
    "accent": "#0D9488",       # Accessible Teal
    "highlight": "#D97706",    # Warm Amber
    "male": "#2563EB",         # Accessible Royal Blue
    "female": "#E11D48",       # Accessible Crimson / Rose
    "neutral_dark": "#0F172A", # Slate 900
    "neutral_light": "#F8FAFC",# Slate 50
    "border": "#E2E8F0",       # Slate 200
    "card_bg": "#FFFFFF",
    "choropleth_scale": "Blues",
    "heatmap_scale": "Viridis",
}
