"""
Carbon-Aware Autonomous Cloud Scheduler Core Package
"""

from .carbon_telemetry import CarbonTelemetryProvider, RegionTelemetry, AWS_GLOBAL_REGION_TELEMETRY
from .optimizer import CarbonWorkloadOptimizer, WorkloadRequirement, OptimizationResult

__all__ = [
    "CarbonTelemetryProvider",
    "RegionTelemetry",
    "AWS_GLOBAL_REGION_TELEMETRY",
    "CarbonWorkloadOptimizer",
    "WorkloadRequirement",
    "OptimizationResult"
]
