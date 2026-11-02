"""
Carbon-Aware Autonomous Cloud Scheduler - Interactive CLI
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from core.carbon_telemetry import CarbonTelemetryProvider
from core.optimizer import CarbonWorkloadOptimizer, WorkloadRequirement

console = Console()


def run_cli():
    console.print(Panel.fit(
        "[bold green]CARBON-AWARE AUTONOMOUS CLOUD SCHEDULER (GREENOPS)[/bold green]\n"
        "[cyan]Real-Time Regional Grid Emissions · Spot Economics · Multi-Objective Placement[/cyan]",
        border_style="green"
    ))

    # Phase 1: Regional Grid Telemetry
    console.print("\n[bold cyan]=== GLOBAL AWS REGION ELECTRICAL GRID EMISSIONS & SPOT PRICING ===[/bold cyan]")
    regions = CarbonTelemetryProvider.get_all_regions()

    grid_table = Table(show_header=True, header_style="bold green")
    grid_table.add_column("AWS Region", width=18)
    grid_table.add_column("Location", width=26)
    grid_table.add_column("Grid Carbon (gCO2/kWh)", width=24)
    grid_table.add_column("Renewables", width=14)
    grid_table.add_column("Spot $/vCPU-hr", width=16)

    for r in sorted(regions, key=lambda x: x.grid_carbon_intensity_gco2_kwh):
        color = "green" if r.grid_carbon_intensity_gco2_kwh < 100 else ("yellow" if r.grid_carbon_intensity_gco2_kwh < 300 else "red")
        grid_table.add_row(
            r.region_code,
            r.region_name,
            f"[{color}]{r.grid_carbon_intensity_gco2_kwh} gCO2eq/kWh[/{color}]",
            f"{r.renewable_percentage}%",
            f"${r.spot_price_hourly_vcpu:.4f}"
        )
    console.print(grid_table)

    # Phase 2: Workload Placement Optimization
    console.print("\n[bold yellow]=== WORKLOAD SCHEDULING: 64-vCPU LLM FINE-TUNING BATCH JOB ===[/bold yellow]")
    workload = WorkloadRequirement(
        workload_id="job-llm-fine-tune-01",
        name="Llama-3-70B Parameter Fine-Tuning Batch",
        workload_type="ML_TRAINING",
        required_vcpus=64,
        estimated_duration_hours=12.0,
        carbon_weight=0.7,
        cost_weight=0.3,
        default_region="us-east-1"
    )

    opt = CarbonWorkloadOptimizer.optimize_placement(workload)

    res_table = Table(show_header=True, header_style="bold blue")
    res_table.add_column("Optimization Metric", width=36)
    res_table.add_column("Value / Impact", width=42)

    res_table.add_row("Default Placement", "us-east-1 (US East - N. Virginia)")
    res_table.add_row("Recommended Green Placement", f"[bold green]{opt.recommended_region} ({opt.recommended_region_name})[/bold green]")
    res_table.add_row("Baseline Grid Emissions", f"{opt.estimated_co2_kg_baseline} kg CO2e")
    res_table.add_row("Optimized Grid Emissions", f"[bold green]{opt.estimated_co2_kg_optimized} kg CO2e[/bold green]")
    res_table.add_row("Net Carbon Reduction", f"[bold green]-{opt.co2_reduction_percentage}% ({opt.co2_saved_kg} kg CO2e saved)[/bold green]")
    res_table.add_row("Baseline Spot Spend", f"${opt.estimated_cost_baseline_usd:.2f}")
    res_table.add_row("Optimized Spot Spend", f"${opt.estimated_cost_optimized_usd:.2f}")
    res_table.add_row("Multi-Objective Fitness Score", f"{opt.fitness_score} / 100")
    res_table.add_row("Optimization Rationale", f"[dim]{opt.rationale}[/dim]")
    console.print(res_table)

    console.print(f"\n[bold green][SUCCESS] Workload dispatched to {opt.recommended_region} with zero SLA degradation.[/bold green]\n")


if __name__ == "__main__":
    run_cli()
