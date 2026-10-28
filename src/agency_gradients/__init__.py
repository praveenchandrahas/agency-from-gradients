"""agency-from-gradients: ablation studies on the conditions under which agency emerges."""
from .config import FACTORS, SELECTIONS, Config
from .probes import viability_probe
from .world import World, passive_entropy_rate

__all__ = ["Config", "World", "FACTORS", "SELECTIONS", "viability_probe", "passive_entropy_rate"]
__version__ = "0.1.0"
