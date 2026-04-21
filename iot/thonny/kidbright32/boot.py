"""Device boot script.

Runs once at startup before main.py. Keep this file minimal and robust.
"""

try:
    import gc
    gc.collect()
except Exception:
    pass
