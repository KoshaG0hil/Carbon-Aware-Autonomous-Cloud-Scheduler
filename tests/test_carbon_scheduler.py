"""
Unit Tests for Carbon-Aware Autonomous Cloud Scheduler
"""

import pytest
from core.carbon_telemetry import CarbonTelemetryProvider
from core.optimizer import CarbonWorkloadOptimizer, WorkloadRequirement


def test_carbon_telemetry_provider():
    reg = CarbonTelemetryProvider.get_region_telemetry("eu-north-1")
    assert reg is not None
    assert reg.grid_carbon_intensity_gco2_kwh == 18.0
    assert reg.renewable_percentage > 90.0

    all_regions = CarbonTelemetryProvider.get_all_regions()
    assert len(all_regions) >= 6


def test_carbon_workload_optimization():
    workload = WorkloadRequirement(
        workload_id="test-job",
        name="Test ETL Pipeline",
        workload_type="BATCH_ETL",
        required_vcpus=32,
        estimated_duration_hours=4.0,
        carbon_weight=0.8,
        cost_weight=0.2,
        default_region="us-east-1"
    )

    opt = CarbonWorkloadOptimizer.optimize_placement(workload)

    # Cleanest region should be recommended over fossil-heavy us-east-1
    assert opt.recommended_region in ["eu-north-1", "ca-central-1"]
    assert opt.co2_saved_kg > 0.0
    assert opt.co2_reduction_percentage > 70.0
    assert opt.estimated_co2_kg_optimized < opt.estimated_co2_kg_baseline


def test_cost_heavy_weighting():
    # When cost is weighted 100%, the cheapest spot region should be selected
    workload = WorkloadRequirement(
        workload_id="cheap-job",
        name="Cost Priority Workload",
        workload_type="CI_BUILD",
        required_vcpus=16,
        estimated_duration_hours=2.0,
        carbon_weight=0.0,
        cost_weight=1.0,
        default_region="ap-southeast-2"
    )

    opt = CarbonWorkloadOptimizer.optimize_placement(workload)
    # us-east-1 has the lowest spot price (0.0110 $/vcpu-hr)
    assert opt.recommended_region == "us-east-1"
    assert opt.cost_savings_usd > 0.0
