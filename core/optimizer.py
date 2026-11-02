"""
Multi-Objective Carbon & Cost Workload Optimization Engine
Evaluates global AWS regions against carbon emission limits and Spot market cost targets.
"""

from typing import List, Dict, Any, Tuple
from pydantic import BaseModel
from .carbon_telemetry import CarbonTelemetryProvider, RegionTelemetry


class WorkloadRequirement(BaseModel):
    workload_id: str
    name: str
    workload_type: str  # ML_TRAINING, BATCH_ETL, VIDEO_TRANSCODE, CI_BUILD
    required_vcpus: int
    estimated_duration_hours: float
    carbon_weight: float = 0.6  # Importance of green energy (0.0 to 1.0)
    cost_weight: float = 0.4    # Importance of lowest cost (0.0 to 1.0)
    default_region: str = "us-east-1"


class OptimizationResult(BaseModel):
    recommended_region: str
    recommended_region_name: str
    estimated_co2_kg_baseline: float
    estimated_co2_kg_optimized: float
    co2_reduction_percentage: float
    co2_saved_kg: float
    estimated_cost_baseline_usd: float
    estimated_cost_optimized_usd: float
    cost_savings_usd: float
    fitness_score: float
    rationale: str


class CarbonWorkloadOptimizer:
    """Calculates optimal deployment regions to minimize greenhouse gas emissions and cloud spend."""

    @staticmethod
    def optimize_placement(workload: WorkloadRequirement) -> OptimizationResult:
        all_regions = CarbonTelemetryProvider.get_all_regions()
        baseline_reg = CarbonTelemetryProvider.get_region_telemetry(workload.default_region) or all_regions[0]

        # Power consumption heuristic: 1 vCPU running under load consumes ~0.025 kW (25W)
        total_kwh = workload.required_vcpus * workload.estimated_duration_hours * 0.025

        # Baseline metrics
        baseline_co2_kg = round((total_kwh * baseline_reg.grid_carbon_intensity_gco2_kwh) / 1000.0, 2)
        baseline_cost = round(workload.required_vcpus * workload.estimated_duration_hours * baseline_reg.spot_price_hourly_vcpu, 2)

        best_region = None
        best_score = -1.0
        best_co2 = 0.0
        best_cost = 0.0

        max_carbon = max(r.grid_carbon_intensity_gco2_kwh for r in all_regions)
        max_price = max(r.spot_price_hourly_vcpu for r in all_regions)

        for reg in all_regions:
            # Normalized scores (higher is better)
            carbon_score = 1.0 - (reg.grid_carbon_intensity_gco2_kwh / max_carbon)
            cost_score = 1.0 - (reg.spot_price_hourly_vcpu / max_price)

            combined_fitness = (workload.carbon_weight * carbon_score) + (workload.cost_weight * cost_score)

            if combined_fitness > best_score:
                best_score = combined_fitness
                best_region = reg
                best_co2 = round((total_kwh * reg.grid_carbon_intensity_gco2_kwh) / 1000.0, 2)
                best_cost = round(workload.required_vcpus * workload.estimated_duration_hours * reg.spot_price_hourly_vcpu, 2)

        co2_saved = round(max(0.0, baseline_co2_kg - best_co2), 2)
        pct_reduced = round((co2_saved / max(0.001, baseline_co2_kg)) * 100.0, 1) if baseline_co2_kg > 0 else 0.0
        cost_saved = round(baseline_cost - best_cost, 2)

        return OptimizationResult(
            recommended_region=best_region.region_code,
            recommended_region_name=best_region.region_name,
            estimated_co2_kg_baseline=baseline_co2_kg,
            estimated_co2_kg_optimized=best_co2,
            co2_reduction_percentage=pct_reduced,
            co2_saved_kg=co2_saved,
            estimated_cost_baseline_usd=baseline_cost,
            estimated_cost_optimized_usd=best_cost,
            cost_savings_usd=cost_saved,
            fitness_score=round(best_score * 100, 1),
            rationale=f"Selected {best_region.region_name} for high {best_region.primary_energy_source} grid mix ({best_region.renewable_percentage}% renewable)."
        )
