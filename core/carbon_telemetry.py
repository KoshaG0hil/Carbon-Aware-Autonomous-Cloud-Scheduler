"""
Carbon Intensity & Spot Pricing Telemetry Engine
Monitors real-time electrical grid emissions (gCO2eq/kWh) and Spot instance economics across AWS global regions.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel


class RegionTelemetry(BaseModel):
    region_code: str
    region_name: str
    grid_carbon_intensity_gco2_kwh: float  # Grams of CO2 equivalent per kilowatt-hour
    primary_energy_source: str  # Hydro, Nuclear, Wind, Gas, Coal
    spot_price_hourly_vcpu: float  # Approximate Spot price per vCPU-hour ($)
    renewable_percentage: float  # Percentage of green energy on the grid


# Real-world baseline telemetry across AWS global regions
AWS_GLOBAL_REGION_TELEMETRY: Dict[str, RegionTelemetry] = {
    "eu-north-1": RegionTelemetry(
        region_code="eu-north-1",
        region_name="Europe (Stockholm)",
        grid_carbon_intensity_gco2_kwh=18.0,
        primary_energy_source="Hydro & Nuclear",
        spot_price_hourly_vcpu=0.0125,
        renewable_percentage=98.0
    ),
    "ca-central-1": RegionTelemetry(
        region_code="ca-central-1",
        region_name="Canada (Central - Montreal)",
        grid_carbon_intensity_gco2_kwh=28.0,
        primary_energy_source="Hydroelectric",
        spot_price_hourly_vcpu=0.0135,
        renewable_percentage=92.0
    ),
    "us-west-2": RegionTelemetry(
        region_code="us-west-2",
        region_name="US West (Oregon)",
        grid_carbon_intensity_gco2_kwh=115.0,
        primary_energy_source="Hydro & Wind",
        spot_price_hourly_vcpu=0.0118,
        renewable_percentage=75.0
    ),
    "eu-west-1": RegionTelemetry(
        region_code="eu-west-1",
        region_name="Europe (Ireland)",
        grid_carbon_intensity_gco2_kwh=245.0,
        primary_energy_source="Wind & Natural Gas",
        spot_price_hourly_vcpu=0.0142,
        renewable_percentage=48.0
    ),
    "us-east-1": RegionTelemetry(
        region_code="us-east-1",
        region_name="US East (N. Virginia)",
        grid_carbon_intensity_gco2_kwh=375.0,
        primary_energy_source="Natural Gas & Nuclear",
        spot_price_hourly_vcpu=0.0110,
        renewable_percentage=22.0
    ),
    "ap-southeast-2": RegionTelemetry(
        region_code="ap-southeast-2",
        region_name="Asia Pacific (Sydney)",
        grid_carbon_intensity_gco2_kwh=485.0,
        primary_energy_source="Coal & Gas",
        spot_price_hourly_vcpu=0.0160,
        renewable_percentage=15.0
    )
}


class CarbonTelemetryProvider:
    """Provides regional carbon intensity and spot telemetry feeds."""

    @staticmethod
    def get_region_telemetry(region_code: str) -> Optional[RegionTelemetry]:
        return AWS_GLOBAL_REGION_TELEMETRY.get(region_code)

    @staticmethod
    def get_all_regions() -> List[RegionTelemetry]:
        return list(AWS_GLOBAL_REGION_TELEMETRY.values())
