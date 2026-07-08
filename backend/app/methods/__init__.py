from .dunn import run_dunn
from .gitt import run_gitt

METHODS: dict[str, str] = {
    "dunn": "Dunn Method",
    "gitt": "GITT Method",
}

__all__ = ["METHODS", "run_dunn", "run_gitt"]

