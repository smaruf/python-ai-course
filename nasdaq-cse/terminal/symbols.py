"""
CSE / DSE stock symbol registry used for autocomplete and validation.

Symbols are drawn from the Dhaka Stock Exchange (DSE) and Chittagong Stock
Exchange (CSE) primary board.  Only a representative subset is shipped here;
a production system would populate this from a live exchange feed.
"""
from typing import List, Dict

# ──────────────────────────────────────────────────────────────────────────────
# Symbol table: symbol → display name
# ──────────────────────────────────────────────────────────────────────────────
CSE_SYMBOLS: Dict[str, str] = {
    # Banking
    "AB": "AB Bank",
    "ABBANK": "AB Bank Ltd",
    "BANKASIA": "Bank Asia Ltd",
    "BRAC": "BRAC Bank Ltd",
    "BRACBANK": "BRAC Bank Ltd",
    "CBL": "City Bank Ltd",
    "CITYBANK": "City Bank Ltd",
    "DBBL": "Dutch-Bangla Bank Ltd",
    "DUTCHBANGL": "Dutch-Bangla Bank Ltd",
    "EBL": "Eastern Bank Ltd",
    "EXIM": "Exim Bank Ltd",
    "IBBL": "Islami Bank Bangladesh Ltd",
    "ISLAMIBANK": "Islami Bank Bangladesh Ltd",
    "MBL": "Mercantile Bank Ltd",
    "MTBL": "Mutual Trust Bank Ltd",
    "NBL": "National Bank Ltd",
    "NCC": "NCC Bank Ltd",
    "NCCBANK": "NCC Bank Ltd",
    "ONEBANKLTD": "One Bank Ltd",
    "PBL": "Premier Bank Ltd",
    "PREMIERBAN": "Premier Bank Ltd",
    "PUBALIBANK": "Pubali Bank Ltd",
    "RUPALIBANK": "Rupali Bank Ltd",
    "SBAC": "SBAC Bank Ltd",
    "SEBL": "Southeast Bank Ltd",
    "SIBL": "Social Islami Bank Ltd",
    "SOUTHEASTB": "Southeast Bank Ltd",
    "STANDBANKL": "Standard Bank Ltd",
    "TRUSTBANK": "Trust Bank Ltd",
    "UCB": "United Commercial Bank",
    "UCBL": "United Commercial Bank Ltd",
    "UTTARABANK": "Uttara Bank Ltd",
    # Telecommunications
    "GP": "Grameenphone Ltd",
    "GRAMEENPHO": "Grameenphone Ltd",
    "ROBI": "Robi Axiata Ltd",
    "TELETALK": "Teletalk Bangladesh Ltd",
    # Pharmaceuticals & Chemicals
    "ACI": "ACI Ltd",
    "ACTIVEFINE": "Active Fine Chemicals Ltd",
    "BATBC": "British American Tobacco Bangladesh",
    "BEXIMCO": "Beximco Ltd",
    "BEXPHARMA": "Beximco Pharmaceuticals",
    "GBB": "Global Beverage Company Ltd",
    "IBNSINA": "Ibn Sina Pharma",
    "JETLINENST": "Jetline Industries",
    "RENATA": "Renata Ltd",
    "SQPHARMA": "Square Pharmaceuticals Ltd",
    "SQUAREPHAR": "Square Pharmaceuticals Ltd",
    # Textiles & Garments
    "ALLTEX": "All Text Industries",
    "ARGONDENIMS": "Argon Denims Ltd",
    "DBH": "Delta Brac Housing Finance",
    "DESHBANDHU": "Deshbandhu Group",
    "ENVOY": "Envoy Textiles Ltd",
    "EVINCOTEX": "Evince Textiles Ltd",
    "HAMIDFA": "Hamid Fabrics Ltd",
    "MLDYEING": "ML Dyeing Ltd",
    "RDFOOD": "RD Foods Ltd",
    "SQUARETEX": "Square Textiles Ltd",
    # Financial Services / Leasing
    "BAYLEASING": "Bay Leasing and Investment",
    "DBH1STMF": "DBH 1st Mutual Fund",
    "IDFCBANK": "IDFC Bank",
    "LANKABANGLA": "LankaBangla Finance",
    "LBFL": "LankaBangla Finance Ltd",
    "MIDAS": "Midas Financing Ltd",
    "PREMIER1MF": "Premier 1st Mutual Fund",
    "UNITEDINS": "United Insurance",
    # Energy & Utilities
    "DESCO": "Dhaka Electric Supply Company",
    "DPDC": "Dhaka Power Distribution",
    "KPCL": "Khulna Power Company",
    "PGCB": "Power Grid Company of Bangladesh",
    "POWERGRID": "Power Grid Company of Bangladesh",
    "SPCL": "Summit Power Ltd",
    "SUMMITPOW": "Summit Power Ltd",
    "TITAS": "Titas Gas Transmission",
    # Cement & Ceramics
    "CONFIDCEM": "Confidence Cement Ltd",
    "HEIDELBCEM": "HeidelbergCement Bangladesh",
    "LAFARGECM": "LafargeHolcim Bangladesh",
    "MEGHNACMT": "Meghna Cement Mills",
    "MICEMENT": "MI Cement Factory",
    "PREMIERCM": "Premier Cement Mills",
    # Food & Beverage
    "AMCL": "AMCL (Pran)",
    "DANISHFD": "Danish Foods Ltd",
    "FUNWORLD": "Fun World Ltd",
    "GEMINISL": "Gemini Sea Food",
    "GOLDENSON": "Golden Son Ltd",
    "OLYMPIC": "Olympic Industries Ltd",
    "PRAN": "PRAN-RFL Group",
    # Engineering & IT
    "AOSL": "Agni Systems Ltd",
    "BDCOM": "BDCOM Online Ltd",
    "BRACITLTD": "BRAC IT Ltd",
    "DATASOFT": "DataSoft Systems Bangladesh",
    "GENEXIL": "Genex Infosys Ltd",
    "WALTONHIL": "Walton Hi-Tech Industries",
}

# Sorted list of symbols for O(1) prefix lookup
_SYMBOL_LIST: List[str] = sorted(CSE_SYMBOLS.keys())


def autocomplete(prefix: str, max_results: int = 10) -> List[Dict[str, str]]:
    """
    Return up to *max_results* symbols whose name starts with *prefix*
    (case-insensitive).  Each result is ``{"symbol": ..., "name": ...}``.
    """
    prefix_up = prefix.upper()
    results = []
    for sym in _SYMBOL_LIST:
        if sym.startswith(prefix_up):
            results.append({"symbol": sym, "name": CSE_SYMBOLS[sym]})
            if len(results) >= max_results:
                break
    return results


def is_valid_symbol(symbol: str) -> bool:
    """Return True if *symbol* is in the known symbol table."""
    return symbol.upper() in CSE_SYMBOLS


def get_symbol_name(symbol: str) -> str:
    """Return the display name for *symbol*, or the symbol itself if unknown."""
    return CSE_SYMBOLS.get(symbol.upper(), symbol.upper())
