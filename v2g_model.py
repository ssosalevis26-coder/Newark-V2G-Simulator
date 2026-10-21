"""Estimate two separate V2G scenarios for a hypothetical electric bus fleet.

The peak-event calculation estimates exportable energy above a departure-charge
reserve. The annual regulation calculation applies a historical price benchmark
to available power, then subtracts modeled operating and capital costs. The two
scenarios are never added together.

Power is in kW, energy in kWh, money in USD, and percentages are fractions
(e.g., 0.90 means 90%). Defaults and evidence labels live in
config/scenario_defaults.json; source citations are recorded in SOURCES.md.
These calculations do not establish actual UD fleet capability, market
eligibility, or transmission-upgrade need or deferral value.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULTS_PATH = ROOT / "config" / "scenario_defaults.json"


def load_defaults(path: Path = DEFAULTS_PATH) -> dict[str, Any]:
    """Read the JSON defaults, including their evidence and source metadata.

    Args:
        path: Configuration file; defaults to the file beside this module.

    Returns:
        Nested configuration dictionary. Numerical inputs are stored inside
        records such as {"value": 155, "evidence": "published proxy", ...}.

    Raises:
        OSError: The file cannot be read.
        json.JSONDecodeError: The file is not valid JSON.

    Loading does not validate the scenario; from_config performs that step.
    """
    with path.open(encoding="utf-8") as source:
        return json.load(source)


@dataclass(frozen=True)
class ScenarioInputs:
    """Immutable numerical inputs for one scenario, without evidence metadata.

    Use from_config to construct and validate this record. Direct dataclass
    construction does not automatically validate values. ``frozen=True`` prevents
    accidental field reassignment after construction.

    bus_count is the purchased fleet; available_buses is the connected subset
    shared by the event and market calculations. battery_kwh and charger_kw are
    per bus; site_export_limit_kw is a fleet-wide ceiling. State of charge,
    efficiencies, throughput ratio, fee, and discount rate use fractions.

    electricity_rate is USD/kWh; battery_wear_cost is USD per modeled throughput
    kWh. maintenance_cost is a fleet-wide annual allowance. Equipment and site
    costs are upfront USD, except the AC increment expressed in USD/kW.
    transmission_upgrade_cost=None means unknown and excluded, not free.
    bus_reference_cost is per bus and is excluded from incremental V2G economics.
    """
    bus_count: int
    available_buses: int
    battery_kwh: float
    starting_soc: float
    departure_soc: float
    charger_kw: float
    site_export_limit_kw: float
    event_hours: float
    events_per_year: int
    discharge_efficiency: float
    round_trip_efficiency: float
    regulation_power_kw: float
    regulation_throughput_ratio: float
    available_hours_per_week: float
    electricity_rate: float
    aggregator_fee_fraction: float
    battery_wear_cost: float
    maintenance_cost: float
    cost_case: str
    ac_incremental_cost_per_kw: float
    dc_charger_cost_per_bus: float
    site_cost: float
    transmission_upgrade_cost: float | None
    bus_reference_cost: float
    asset_life_years: int
    discount_rate: float

    @classmethod
    def from_config(
        cls, config: dict[str, Any], overrides: dict[str, Any] | None = None
    ) -> "ScenarioInputs":
        """Resolve defaults and optional flat overrides, then validate inputs.

        Args:
            config: Nested configuration returned by load_defaults.
            overrides: Flat numerical edits, such as {"starting_soc": 0.85}.
                These take precedence over configuration values. Cost-case names
                are strings; transmission cost may be None or a blank string.

        Returns:
            A validated, frozen ScenarioInputs record. Historical price overrides
            are handled separately inside calculate, not stored in this record.

        Raises:
            ValueError: A numerical input is non-finite, boolean, out of bounds,
                or fractional where a whole count is required.
            KeyError: A required configuration section is missing.

        Overrides change this calculation only; the configuration is not edited.
        """
        overrides = overrides or {}
        fleet = config["fleet"]
        event = config["event"]
        tech = config["technical"]
        values = config["value_scenarios"]
        costs = config["capital_costs"]
        operating = config["operating_costs"]

        def get(section: dict[str, Any], key: str, override: str, default: Any) -> Any:
            """Read a numeric edit/default before conversion can truncate counts."""
            value = overrides.get(override, section.get(key, {}).get("value", default))
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError(f"{override} must be a finite number.")
            if override in {"bus_count", "available_buses", "events_per_year", "asset_life_years"} and value != int(value):
                raise ValueError(f"{override} must be a whole number.")
            return value

        raw_upgrade = overrides.get("transmission_upgrade_cost_usd", costs["transmission_upgrade_equipment_cost_usd"]["value"])
        if raw_upgrade is None or raw_upgrade == "":
            raw_upgrade = None
        elif isinstance(raw_upgrade, bool) or not isinstance(raw_upgrade, (int, float)) or not math.isfinite(raw_upgrade):
            raise ValueError("Transmission cost must be a finite number or null.")

        data = cls(
            bus_count=int(get(fleet, "bus_count", "bus_count", 14)),
            available_buses=int(get(fleet, "available_for_peak_event", "available_buses", 14)),
            battery_kwh=float(get(fleet, "battery_capacity_kwh_per_bus", "battery_kwh", 155)),
            starting_soc=float(get(fleet, "starting_soc_fraction", "starting_soc", 0.90)),
            departure_soc=float(get(fleet, "minimum_departure_soc_fraction", "departure_soc", 0.70)),
            charger_kw=float(get(event, "dispatch_power_limit_kw_per_bus", "charger_kw", 60)),
            site_export_limit_kw=float(get(event, "site_export_limit_kw", "site_export_limit_kw", 840)),
            event_hours=float(get(event, "duration_hours", "event_hours", 3)),
            events_per_year=int(get(event, "events_per_year", "events_per_year", 20)),
            discharge_efficiency=float(get(tech, "discharge_efficiency", "discharge_efficiency", 0.96)),
            round_trip_efficiency=float(get(tech, "round_trip_efficiency", "round_trip_efficiency", 0.90)),
            regulation_power_kw=float(get(tech, "regulation_dispatch_power_kw_per_vehicle", "regulation_power_kw", 29)),
            regulation_throughput_ratio=float(get(tech, "regulation_average_power_throughput_ratio", "regulation_throughput_ratio", 0.26)),
            available_hours_per_week=float(get(tech, "availability_hours_per_week", "available_hours_per_week", 128)),
            electricity_rate=float(get(values, "retail_energy_cost_usd_per_kwh", "electricity_rate", 0.0744)),
            aggregator_fee_fraction=float(get(operating, "aggregator_fee_fraction_of_gross_market_revenue", "aggregator_fee_fraction", 0.15)),
            battery_wear_cost=float(get(operating, "battery_wear_cost_usd_per_kwh_throughput", "battery_wear_cost", 0.03)),
            maintenance_cost=float(get(operating, "annual_maintenance_cost_usd", "maintenance_cost", 0)),
            cost_case=str(overrides.get("cost_case", costs.get("v2g_cost_case", "ac_incremental_plus_site_proxy"))),
            ac_incremental_cost_per_kw=float(get(costs, "ac_v2g_incremental_cost_usd_per_kw", "ac_incremental_cost_per_kw", 20)),
            dc_charger_cost_per_bus=float(get(costs, "dc_v2g_charger_reference_usd_per_unit", "dc_charger_cost_per_bus", 89930)),
            site_cost=float(get(costs, "site_make_ready_installation_proxy_usd", "site_cost", 113573)),
            transmission_upgrade_cost=float(raw_upgrade) if raw_upgrade is not None else None,
            bus_reference_cost=float(get(costs, "electric_v2g_bus_reference_usd_per_unit", "bus_reference_cost", 341957)),
            asset_life_years=int(get(costs, "asset_life_years", "asset_life_years", 10)),
            discount_rate=float(get(costs, "discount_rate_fraction", "discount_rate", 0.05)),
        )
        data.validate()
        return data

    def validate(self) -> None:
        """Check bounds and relationships on inputs normalized by from_config.

        For example, connected buses cannot exceed the fleet, departure charge
        cannot exceed starting charge, and weekly hours cannot exceed 168.
        Zero connected buses and zero power are valid inactive scenarios.

        Raises:
            ValueError: A checked bound or relationship is violated.

        This checks model consistency, not engineering or market feasibility.
        Numeric type, finiteness, and integer-count checks occur in from_config.
        """
        if self.bus_count < 0 or self.available_buses < 0:
            raise ValueError("Bus counts cannot be negative.")
        if self.available_buses > self.bus_count:
            raise ValueError("Available buses cannot exceed fleet size.")
        for label, value in (("starting state of charge", self.starting_soc), ("departure state of charge", self.departure_soc), ("discharge efficiency", self.discharge_efficiency), ("round-trip efficiency", self.round_trip_efficiency)):
            if not 0 <= value <= 1:
                raise ValueError(f"{label.title()} must be between 0 and 1.")
        if self.departure_soc > self.starting_soc:
            raise ValueError("Minimum departure charge cannot exceed starting charge.")
        if self.battery_kwh < 0 or self.charger_kw < 0 or self.site_export_limit_kw < 0:
            raise ValueError("Battery and power values cannot be negative.")
        if self.event_hours <= 0:
            raise ValueError("Peak-event duration must be greater than zero.")
        if self.events_per_year < 0 or self.available_hours_per_week < 0:
            raise ValueError("Event counts and available hours cannot be negative.")
        if not 0 <= self.aggregator_fee_fraction <= 1:
            raise ValueError("Aggregator fee must be between 0 and 1.")
        if min(self.battery_wear_cost, self.electricity_rate, self.maintenance_cost, self.site_cost, self.transmission_upgrade_cost or 0, self.ac_incremental_cost_per_kw, self.dc_charger_cost_per_bus, self.bus_reference_cost) < 0:
            raise ValueError("Cost inputs cannot be negative.")
        if self.asset_life_years <= 0 or not 0 <= self.discount_rate < 1:
            raise ValueError("Asset life must be positive and discount rate must be from 0 up to (but not including) 1.")
        if not 0 <= self.available_hours_per_week <= 168:
            raise ValueError("Market hours must be between 0 and 168 per week.")
        if self.regulation_power_kw < 0 or not 0 <= self.regulation_throughput_ratio <= 1:
            raise ValueError("Regulation power must be nonnegative and throughput ratio between 0 and 1.")
        if self.cost_case not in {"ac_incremental_plus_site_proxy", "dc_chargers_plus_site_proxy"}:
            raise ValueError("Choose the AC incremental or DC charger cost case.")


def capital_recovery_factor(rate: float, years: int) -> float:
    """Return the multiplier converting upfront cost to equal annual cost.

    Args:
        rate: Nonnegative finite annual discount rate as a fraction.
        years: Positive integer asset life in years.

    Returns:
        r * (1 + r)**n / ((1 + r)**n - 1), or 1/n when r is zero.
        Multiplying upfront USD by this factor gives equivalent USD/year.
        For example, 0.05 over 10 years gives approximately 0.1295.

    Raises:
        ValueError: Asset life is not a positive integer or rate is invalid.

    Annualization represents capital recovery at the assumed discount rate;
    it is not an additional actual loan payment or a simple-payback calculation.
    """
    if isinstance(years, bool) or not isinstance(years, int) or years <= 0:
        raise ValueError("Asset life must be greater than zero.")
    if not math.isfinite(rate) or rate < 0:
        raise ValueError("Discount rate cannot be negative.")
    if rate == 0:
        return 1 / years
    return rate * (1 + rate) ** years / ((1 + rate) ** years - 1)


def calculate(
    config: dict[str, Any], overrides: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Calculate physical event capability and separate annual value cases.

    Args:
        config: Defaults and provenance records returned by load_defaults.
        overrides: Optional flat input edits. price_low, price_central, and
            price_high override historical price cases in USD/MWh as used by
            the report benchmark. Other supported edits map to ScenarioInputs.

    Returns:
        JSON-compatible dictionary with these groups:
        - peak_event: Connected-fleet nameplate/site limits, usable DC energy,
          exported AC kWh per event, average kW, and annual event kWh.
        - regulation: Annual available hours, capped fleet bid power, per-bus
          throughput, and each price case's annual revenue/cost breakdown.
        - capital: Selected equipment, one site proxy, any entered transmission
          cost, and annualized capital. Bus acquisition is reference-only.
        - comparators: Separate TOU context, never added to regulation revenue.
        - limitations: Interpretation notes for the API and interface.

    Raises:
        ValueError: Inputs or historical price edits fail validation.
        KeyError: Required configuration data is missing.

    Calculation order:
        1. Usable DC energy = battery kWh * (starting SoC - departure SoC).
           Apply one-way efficiency to find exportable AC energy. Average
           export is capped by connected chargers, site power, and energy/time.
        2. Annual market hours = weekly hours * 52. The per-bus bid is capped
           by charger power and the site's equally shared export ceiling.
           Gross value uses price/1000 * hours * kW * connected buses.
        3. Subtract loss-energy cost, gross-revenue fee, throughput-based wear,
           and fleet maintenance once. The report-style loss approximation is
           throughput * (1 - round-trip efficiency); it is not a general
           output-energy-to-recharge equation. No event energy is charged here.
        4. Subtract annualized selected capital. Simple payback instead divides
           upfront capital by positive operating net, returning None otherwise.

    Costs purchase equipment for the full fleet, even if fewer buses connect.
    Unknown transmission cost remains None in the output and is omitted from
    the capital sum. Normal driving energy and full bus acquisition belong to
    the same-electric-bus baseline and are excluded. This annual benchmark does
    not simulate route schedules, charge trajectories, or regulation signals.
    """
    overrides = overrides or {}
    inputs = ScenarioInputs.from_config(config, overrides)
    fleet_count = inputs.bus_count
    active = min(inputs.available_buses, fleet_count)

    # Peak-event export uses battery energy above the next-route reserve and
    # the measured one-way discharge-efficiency comparator.
    available_dc_kwh_per_bus = inputs.battery_kwh * max(0.0, inputs.starting_soc - inputs.departure_soc)
    available_ac_kwh_per_bus = available_dc_kwh_per_bus * inputs.discharge_efficiency
    theoretical_kw = min(active * inputs.charger_kw, inputs.site_export_limit_kw)
    energy_limited_kw = active * available_ac_kwh_per_bus / inputs.event_hours
    event_export_kw = min(theoretical_kw, energy_limited_kw)
    event_export_kwh = min(active * available_ac_kwh_per_bus, event_export_kw * inputs.event_hours)
    annual_event_export_kwh = event_export_kwh * inputs.events_per_year

    # Regulation value follows the UD/Exelon report method: market capacity
    # revenue minus energy cost for round-trip losses, then fee and wear.
    annual_hours = inputs.available_hours_per_week * 52
    market_count = active
    # This remains an annual benchmark, not a time-series dispatch simulation.
    # Respect the same connected-fleet charger and site ceiling in both cases.
    market_power = min(inputs.regulation_power_kw, inputs.charger_kw,
                       inputs.site_export_limit_kw / market_count if market_count else 0)
    loss_power_kw_per_bus = (
        market_power
        * inputs.regulation_throughput_ratio
        * (1 - inputs.round_trip_efficiency)
    )
    throughput_kwh_per_bus = (
        market_power * inputs.regulation_throughput_ratio * annual_hours
    )
    fee_cases = config["value_scenarios"]["regulation_price_usd_per_mwh"]
    scenario_results: dict[str, Any] = {}
    for case_name, price_data in fee_cases.items():
        raw_price = overrides.get(f"price_{case_name}", price_data["value"])
        if isinstance(raw_price, bool) or not isinstance(raw_price, (int, float)) or not math.isfinite(raw_price):
            raise ValueError("Regulation prices must be finite numbers.")
        price = float(raw_price)
        if price < 0:
            raise ValueError("Regulation price inputs cannot be negative.")
        gross = (price / 1000) * annual_hours * market_power * market_count
        loss_energy_cost = inputs.electricity_rate * annual_hours * loss_power_kw_per_bus * market_count
        aggregator_fee = gross * inputs.aggregator_fee_fraction
        battery_wear = throughput_kwh_per_bus * market_count * inputs.battery_wear_cost
        operating_net = gross - loss_energy_cost - aggregator_fee - battery_wear - inputs.maintenance_cost
        scenario_results[case_name] = {
            "price_usd_per_mwh": price,
            "gross_revenue_usd": gross,
            "recharge_loss_cost_usd": loss_energy_cost,
            "aggregator_fee_usd": aggregator_fee,
            "battery_wear_cost_usd": battery_wear,
            "maintenance_cost_usd": inputs.maintenance_cost,
            "operating_net_usd": operating_net,
        }

    if inputs.cost_case == "ac_incremental_plus_site_proxy":
        equipment_capex = fleet_count * inputs.charger_kw * inputs.ac_incremental_cost_per_kw
        equipment_label = "AC V2G incremental manufacturing estimate"
    else:
        equipment_capex = fleet_count * inputs.dc_charger_cost_per_bus
        equipment_label = "V2G DC charger reference case"

    capital_cost = equipment_capex + inputs.site_cost + (inputs.transmission_upgrade_cost or 0)
    crf = capital_recovery_factor(inputs.discount_rate, inputs.asset_life_years)
    annualized_capital = capital_cost * crf
    for result in scenario_results.values():
        result["annualized_capital_cost_usd"] = annualized_capital
        result["annualized_net_after_capital_usd"] = result["operating_net_usd"] - annualized_capital
        result["simple_payback_years"] = (
            capital_cost / result["operating_net_usd"] if result["operating_net_usd"] > 0 else None
        )

    bus_reference_total = fleet_count * inputs.bus_reference_cost
    dc_reference_total = fleet_count * inputs.dc_charger_cost_per_bus
    dpl_tou_per_bus = float(config["value_scenarios"]["dpl_tou_comparator_net_savings_usd_per_33kw_ev_year"]["value"])

    return {
        "peak_event": {
            "active_buses": active,
            "nameplate_export_capacity_kw": active * inputs.charger_kw,
            "site_limited_capacity_kw": theoretical_kw,
            "available_battery_energy_dc_kwh": available_dc_kwh_per_bus * active,
            "export_energy_per_event_kwh": event_export_kwh,
            "average_export_power_kw": event_export_kw,
            "event_duration_hours": inputs.event_hours,
            "events_per_year": inputs.events_per_year,
            "annual_export_energy_kwh": annual_event_export_kwh,
        },
        "regulation": {
            "available_hours_per_year": annual_hours,
            "fleet_dispatch_equivalent_kw": market_power * market_count,
            "loss_power_kw_per_vehicle": loss_power_kw_per_bus,
            "throughput_kwh_per_vehicle": throughput_kwh_per_bus,
            "scenarios": scenario_results,
        },
        "capital": {
            "cost_case": inputs.cost_case,
            "equipment_label": equipment_label,
            "equipment_capex_usd": equipment_capex,
            "site_make_ready_proxy_usd": inputs.site_cost,
            "transmission_upgrade_cost_usd": inputs.transmission_upgrade_cost,
            "total_project_capital_usd": capital_cost,
            "annualized_capital_cost_usd": annualized_capital,
            "asset_life_years": inputs.asset_life_years,
            "discount_rate": inputs.discount_rate,
            "electric_bus_reference_total_usd": bus_reference_total,
            "dc_charger_reference_total_usd": dc_reference_total,
        },
        "comparators": {
            "dpl_tou_reference_per_bus_usd_year": dpl_tou_per_bus,
            "dpl_tou_reference_fleet_usd_year": dpl_tou_per_bus * fleet_count,
            "dpl_tou_is_newark_tariff": False,
            "newark_demand_charge_savings_calculated": False,
        },
        "limitations": [
            "UD bus count is used as a scenario size; actual UD buses are not asserted to be electric or V2G-capable.",
            "The bus battery, charger, reserve, and schedule values are proxies or scenario assumptions.",
            "Regulation uses the event available-bus count as a shared connected-fleet assumption, with separate weekly hours; it does not simulate route schedules, SoC trajectories, or market performance scoring.",
            "Unknown transmission cost is excluded from totals, not assumed free. Maintenance defaults to excluded (zero allowance); taxes, incentives, financing fees, and normal driving energy are excluded.",
            "Only incremental regulation loss energy is charged; no event savings or TOU value is added to regulation revenue.",
            "PJM Regulation results are historical sensitivities and assume aggregator participation and market eligibility.",
            "Newark citywide summer peak is not the UD campus feeder peak or an interconnection limit.",
            "The site make-ready figure is a case-derived proxy, not a Newark transmission-upgrade quote.",
            "No transmission deferral, demand-charge savings, or emissions benefit is claimed.",
        ],
    }
