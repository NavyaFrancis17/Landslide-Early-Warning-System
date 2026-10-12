"""
AI-Based Location-Adaptive Landslide Early-Warning System.

Phase 1 Core Package Initialization.
"""

import sys

# Scikit-learn unpickle compatibility patch for _loss module
try:
    if "_loss" not in sys.modules:
        import types
        import importlib.machinery
        import sklearn._loss.loss
        _loss_mod = types.ModuleType("_loss")
        _loss_mod.__spec__ = importlib.machinery.ModuleSpec("_loss", None)
        for attr in dir(sklearn._loss.loss):
            setattr(_loss_mod, attr, getattr(sklearn._loss.loss, attr))
        sys.modules["_loss"] = _loss_mod
except Exception:
    pass

__version__ = "0.1.0"
__author__ = "Academic AI Research Team"
