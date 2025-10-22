# backend/utils/normalize.py
from dateutil import parser as dtparser
import re
from datetime import datetime
from typing import Optional, Tuple

# Bank locale preferences: True means day-first (DD/MM/YYYY), False means month-first (MM/DD/YYYY)
BANK_DATE_PREF = {
    "HDFC": False,    # often uses MM/DD/YYYY in our synthetic templates
    "ICICI": False,
    "SBI": False,
    "AXIS": False,
    "AMEX": False,
    "DEFAULT": False
}

def norm_number(s: Optional[str]) -> Optional[str]:
    """Normalize currency/number strings to a standard float string with 2 decimals."""
    if not s:
        return None
    s2 = re.sub(r"[^\d.\-]", "", str(s))
    if not s2:
        return None
    # If multiple dots, assume last is decimal separator
    if s2.count('.') > 1:
        parts = s2.split('.')
        s2 = ''.join(parts[:-1]) + '.' + parts[-1]
    try:
        f = float(s2)
        return f"{f:.2f}"
    except Exception:
        return None

def try_parse_date(s: str, dayfirst: bool) -> Optional[datetime]:
    """Attempt to parse date string with a given dayfirst hint; return datetime.date on success."""
    try:
        dt = dtparser.parse(s, dayfirst=dayfirst, fuzzy=True)
        return dt
    except Exception:
        return None

def norm_date_with_bank(s: Optional[str], bank: Optional[str] = None) -> Optional[str]:
    """
    Robust date normalization:
    - Uses bank-specific preference first.
    - Tries both dayfirst False and True if preferred parse fails.
    - If ambiguous numeric-only strings (e.g. 01/05/20) tries both heuristics and picks the one
      that gives a plausible date (not in future far beyond 2 years nor before 2000).
    Returns ISO date string YYYY-MM-DD or None.
    """
    if not s:
        return None
    bank = (bank or "DEFAULT").upper()
    pref = BANK_DATE_PREF.get(bank, BANK_DATE_PREF["DEFAULT"])

    # quick clean
    s_clean = str(s).strip()
    # Try preferred first
    dt = try_parse_date(s_clean, dayfirst=pref)
    if dt:
        return dt.date().isoformat()

    # Try the other way
    dt2 = try_parse_date(s_clean, dayfirst=(not pref))
    if dt2:
        return dt2.date().isoformat()

    # Additional heuristics: numeric ambiguous tokens — try swapping day/month manually
    m = re.findall(r"(\d{1,4})", s_clean)
    if len(m) >= 3:
        # attempt manual swaps for common separators
        parts = re.split(r"[^\d]+", s_clean)
        try:
            p = [int(x) for x in parts if x.strip() != ""]
            # assume (d,m,y) or (m,d,y) whichever forms valid date
            if len(p) >= 3:
                d1, d2, y = p[0], p[1], p[2]
                candidates = []
                # candidate A: day=d1, month=d2
                try:
                    cand = datetime(year=2000 + (y if y < 100 else y) if y < 1000 else y,
                                    month=d2, day=d1)
                    candidates.append(cand)
                except Exception:
                    pass
                # candidate B: month=d1, day=d2
                try:
                    cand = datetime(year=2000 + (y if y < 100 else y) if y < 1000 else y,
                                    month=d1, day=d2)
                    candidates.append(cand)
                except Exception:
                    pass
                if candidates:
                    # choose the candidate not in far future and within reasonable range
                    now = datetime.now()
                    candidates = [c for c in candidates if abs((c - now).days) < 3650]  # within 10 years
                    if candidates:
                        best = sorted(candidates, key=lambda c: abs((c - now).days))[0]
                        return best.date().isoformat()
        except Exception:
            pass

    return None

def norm_date(s: Optional[str]) -> Optional[str]:
    """Generic date normalization without bank preference (tries both)."""
    return norm_date_with_bank(s, bank=None)

def approx_equal_numbers(a: Optional[str], b: Optional[str], eps: float = 0.01) -> bool:
    na = norm_number(a)
    nb = norm_number(b)
    if na is None or nb is None:
        return False
    try:
        return abs(float(na) - float(nb)) <= eps
    except Exception:
        return False

def simple_str_sim(a: Optional[str], b: Optional[str]) -> float:
    if not a or not b:
        return 0.0
    a2 = str(a).strip().lower()
    b2 = str(b).strip().lower()
    if a2 == b2:
        return 1.0
    sa = set(re.findall(r'\w+', a2))
    sb = set(re.findall(r'\w+', b2))
    if not sa or not sb:
        return 0.0
    inter = sa.intersection(sb)
    return len(inter) / max(len(sa), len(sb))

# Exposed comparison helpers that accept bank hint
def compare_dates(label: Optional[str], parsed: Optional[str], bank: Optional[str] = None) -> Tuple[bool, Optional[str], Optional[str]]:
    ln = norm_date_with_bank(label, bank)
    pn = norm_date_with_bank(parsed, bank)
    ok = (ln is not None and pn is not None and ln == pn)
    return ok, ln, pn
