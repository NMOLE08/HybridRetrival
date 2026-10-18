"""Repeated warm timing helper (wall clock, excluding setup)."""
from __future__ import annotations
import time
import numpy as np


def benchmark(fn, repeats=30, warmup=3):
    if repeats < 1 or warmup < 0: raise ValueError("Invalid timing repeat count")
    for _ in range(warmup): fn()
    times=[]
    for _ in range(repeats):
        start=time.perf_counter_ns();fn();times.append((time.perf_counter_ns()-start)/1e6)
    return {"unit":"ms","warmup":warmup,"repeats":repeats,"median":float(np.median(times)),"p95":float(np.percentile(times,95)),"samples_ms":times}
