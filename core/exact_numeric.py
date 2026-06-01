from typing import Optional, Tuple, Any, List, Dict

class DualValue:
    def __init__(
        self,
        exact: Optional[str] = None,
        exact_latex: Optional[str] = None,
        numeric: Optional[str] = None,
        interval: Optional[Tuple[str, str]] = None,
        status: str = "unknown",
        method: Optional[str] = None,
        precision_digits: int = 50,
        notes: Optional[List[str]] = None,
    ):
        self.exact = exact
        self.exact_latex = exact_latex
        self.numeric = numeric
        self.interval = interval
        self.status = status
        self.method = method
        self.precision_digits = precision_digits
        self.notes = notes or []
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "exact": self.exact,
            "exact_latex": self.exact_latex,
            "numeric": self.numeric,
            "interval": self.interval,
            "status": self.status,
            "method": self.method,
            "precision_digits": self.precision_digits,
            "notes": self.notes,
        }
