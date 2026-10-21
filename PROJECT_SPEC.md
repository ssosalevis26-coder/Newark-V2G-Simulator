# Project Specification: Newark V2G Fleet Value Simulator

## Project folder

Use this workspace as the project root. It currently contains `SOURCES.md`; the MVP inputs are in `config/scenario_defaults.json`. Do not wait for proprietary UD or Kempton data to build the first version.

## Project question

For a modeled 14-bus University of Delaware fleet in Newark, what V2G power and energy could be available during a summer peak event, and what annual operating value might the same fleet earn under a PJM Regulation benchmark? Show cost, uncertainty, and the conditions that would need to be true.

## Chosen baseline and scope

- Fleet size: 14 buses, using the UD published fleet count as the scenario size. The model does **not** assert the actual UD buses are electric or V2G-capable.
- Financial comparison: the same electric buses operated without V2G versus those buses participating in V2G. This isolates the incremental V2G business case. The full bus acquisition reference cost is shown separately and excluded from incremental payback.
- Geography: Newark, Delaware. Newark annual summer peak is context only, not a feeder limit or UD campus load.
- No emissions comparison in the MVP.
- No claim of a verified transmission upgrade deferral, actual PJM enrollment, or utility-approved export capacity.

## Default technical scenario

| Input | MVP default | Evidence and treatment |
|---|---:|---|
| Number of buses | 14 | Published UD fleet count used only as a scenario size |
| Battery per bus | 155 kWh | WRI Portland example proxy; not a UD specification |
| Charger nameplate | 60 kW per bus | WRI Portland example / product benchmark |
| Starting charge | 90% | Scenario assumption |
| Minimum charge before next route | 70% | Editable scenario placeholder; no UD route energy data |
| Buses available during each peak event | 14 of 14 | User-selected scenario assumption |
| Event duration | 3 hours | Published WRI demonstration comparator |
| Events per year | 20 | Scenario assumption for physical energy throughput only |
| Round-trip efficiency | 90% | Measured UD/Exelon pilot comparator; not a UD bus measurement |
| Event discharge efficiency | 96% | Measured maximum in the UD/Exelon pilot; editable proxy, not a UD bus measurement |
| Dispatch power for market-value comparison | 29 kW per bus | Pilot achieved 29 kW from 33 kW-rated vehicles; proxy, not a bus test |

At the chosen reserve, each bus has 31 kWh of battery energy available before conversion losses (155 kWh × (90% − 70%)). At 96% discharge efficiency this is about 29.76 kWh exported per bus, or about 416.64 kWh across 14 buses per event. Over a three-hour event, this is energy-limited to about 138.88 kW average aggregate export, below the 840 kW nameplate sum. At 20 events/year, the scenario exports about 8.333 MWh/year. If users change event duration, reserve charge, or charger count, recompute this limit.

The event energy estimate and annual PJM Regulation value are separate analyses. Do not multiply the market-value benchmark by the 20 peak events or add TOU and Regulation revenue together.

## Chosen value cases

### Primary: PJM Regulation historical sensitivity

Use the 2026 UD/Exelon technical report’s formula, with a local UD large-light-and-power energy-rate proxy from Newark’s 2024 cost-of-service study. This gives an explainable, source-backed scenario while keeping assumptions visible.

For each market price case:

- Available hours: 128 hours/week × 52 = 6,656 hours/year, matching the technical report’s 40 hours/week unavailable case. The user’s assumption that all 14 buses are available during a peak event remains in force for the separate event calculation.
- Market price: low $21.15/MWh (2023 annual average), central $36.26/MWh (2021–2025 mean), high $54.97/MWh (2022 annual average). These are historical sensitivity values, not a 2026 forecast.
- Dispatch rating: 29 kW per bus, from the UD/Exelon comparator.
- Average regulation throughput ratio: 0.26; round-trip efficiency: 0.90, both from that comparator.
- Energy cost rate: $0.0744/kWh as published for UD large-light-and-power in Newark’s 2024 rate study through its FY2028 projection, with the study noting that RSA does not apply. Treat this as a tariff proxy to verify against UD’s current contract or bill.

Formulas:

```text
available_hours = 128 × 52
loss_power_kw_per_bus = 29 × 0.26 × (1 − 0.90)
gross_regulation_revenue_per_bus = (market_price_usd_per_mwh / 1000) × available_hours × 29
loss_energy_cost_per_bus = 0.0744 × available_hours × loss_power_kw_per_bus
net_before_fee_and_wear = (gross_regulation_revenue_per_bus − loss_energy_cost_per_bus) × 14
aggregator_fee = gross_regulation_revenue_per_bus × 14 × 15%
battery_wear_cost = (29 × 0.26 × available_hours × 14) × $0.03/kWh-throughput
annual_operating_net = net_before_fee_and_wear − aggregator_fee − battery_wear_cost
annualized_capital = project_capital_cost × CRF(5%, 10 years)
annualized_net_after_capital = annual_operating_net − annualized_capital
```

Aggregator fee (15%, sensitivity 10%–25%) and battery wear cost ($0.03/kWh, sensitivity $0.01–$0.08/kWh) are explicitly scenario assumptions, because no UD contract or bus-specific degradation price is available. Annual market values derived from the UD/Exelon report exclude aggregator fees and battery wear, so subtract those separately. Do not subtract charge-loss cost twice.

### Secondary: Newark retail tariff context

- Use $0.0744/kWh as a published UD-class energy-rate proxy, not a confirmed current bill rate. The published UD class does not show a time-of-use spread in the study. Therefore, default retail energy arbitrage value for Newark is **not claimed**; a flat energy rate plus conversion losses does not by itself create arbitrage savings.
- The study lists an $8.96/kW demand charge above 150 kW for the UD class. Do not apply demand-charge savings until the project has a facility meter class, monthly peak profile, and evidence V2G reduces the relevant billing peak. Default demand-charge savings to “not calculated.”
- Show the report’s $1,048/year per 33 kW vehicle Delmarva TOU result only as a separate comparison, never as the UD tariff or added to PJM Regulation value.

## Equipment and upgrade cost treatment

Use three visibly separate cost lines:

1. **Electric V2G bus reference:** $341,957 per bus from a WRI-reported 2022 case. Display the 14-bus reference fleet cost ($4,787,398) for context, but exclude it from incremental V2G payback because the baseline uses the same electric buses.
2. **V2G hardware:** Base case uses the 2026 UD/Exelon report’s $20/kW estimated mass-production incremental AC V2G cost × 60 kW × 14 = $16,800. This is a manufacturing increment estimate, not a retail or installed quote. Provide a conservative alternative using the WRI case’s $89,930 per 60 kW V2G DC charger (14 ports = $1,259,020); do not add the two equipment cases together.
3. **Site make-ready/install:** $113,573 one-time reference proxy derived from a WRI case package ($545,460 bus + charger + installation less $341,957 bus less $89,930 charger). Label it as an inferred project-specific make-ready/installation proxy, not a transmission-equipment quote or Newark estimate. Allow editing.

Transmission-upgrade equipment cost remains unknown and must be a separate optional user input. Default it to `null` / “not estimated”; never substitute the make-ready proxy or a citywide peak value for a transmission study.

Use 10-year asset life and 5% discount rate as editable scenario assumptions. Calculate annualized cost using the capital recovery factor; also show upfront capex and simple payback where net operating value is positive.

## Low, central, and high cases

- Low / central / high market-price cases use the published 2023 minimum, 2021–2025 mean, and 2022 maximum from the UD/Exelon report.
- Apply the same editable technical defaults to all three cases so users can see price sensitivity clearly.
- Also show a sensitivity control for charger cost case, aggregator fee, battery wear, reserve SoC, events/year, and number of available buses.
- Do not present the central case as a prediction or recommendation to invest.

## Illustrative result from the selected defaults

Using the defaults in `config/scenario_defaults.json`, the central historical PJM Regulation sensitivity is approximately **$56,983/year operating net before annualized V2G capital** and **$40,099/year after annualizing the selected AC incremental hardware plus site make-ready proxy**. The low and high price sensitivities are approximately **$5,392/year** and **$83,076/year**, respectively, after annualized capital. These are calculated scenario outputs, not expected UD savings or an investment recommendation.

The AC incremental hardware case is $16,800 (14 × 60 kW × $20/kW) plus the $113,573 site proxy, totaling $130,373 upfront. The annualized capex uses 10 years and 5%. The separate DC charger alternative is $1,259,020 for 14 chargers before any installation, and should be shown as a different cost case.

## Required demo outputs

- Theoretical nameplate export capacity (14 × 60 kW) and the energy-limited, three-hour dispatch capacity.
- kWh exported per event and per year for the 20-event scenario.
- PJM Regulation low / central / high gross revenue, recharge-loss cost, aggregator fee, battery-wear cost, operating net, annualized capex, and net after annualized capex.
- Full electric-bus reference acquisition cost, V2G hardware alternative costs, and make-ready proxy, all separated.
- Newark tariff and grid context with source links and caveats.
- Clear explanation that Newark citywide peak is not campus feeder load and no avoided transmission upgrade is calculated.
- “Assumptions & sources” view listing value, units, evidence type, source, date, and editable status.

## Build and acceptance checklist

- Create a Python calculation module with typed, named functions and input validation.
- Add tests for energy reserve limits, event duration, zero available buses, tariff loss costs, each revenue case, capital recovery factor, invalid inputs, and no double-counting.
- Add a polished local web demo (Streamlit is an acceptable MVP choice) with editable scenario controls and readable charts.
- Keep math/calculation layer separate from UI.
- Cite every published input inline and keep `SOURCES.md` as bibliography.
- Add `README.md` with setup, run, test, assumptions, limitations, and folder map.
- Run the app and tests before reporting completion.

## Finished implementation clarifications

The connected fleet count is shared between event and regulation analyses; weekly market availability remains separate. The regulation power used in all revenue, loss, and wear equations is `min(regulation rating per bus, charger kW per bus, site export limit / connected buses)` (zero for no connected buses). This prevents a revenue bid above entered hardware/export limits. The model does not enforce regulation SoC trajectories, symmetric import/export capability, actual dispatch signals, route schedules, market performance scoring, or qualification.

Nameplate output is connected buses times charger power; site-limited capacity is returned separately. Unknown transmission cost remains JSON null, and only an entered amount is included in capital arithmetic. Absence of an estimate is not a zero-cost conclusion. The same one-project installation proxy is used once for the fleet, without evidence of fleet-size scaling. Maintenance is editable and defaults to excluded; normal driving energy, taxes, incentives, financing fees, and unknown costs are excluded. No event payment or energy savings is modeled.

All numerical controls used in the demo are editable. Equipment unit assumptions and maintenance are included. Non-finite numbers, booleans, fractional counts, negative costs, and weekly availability above 168 hours are rejected. Price cases are independently editable and need not remain ordered. The default evidence table reads the configuration; full source dates/links remain in SOURCES.md. This revision retains source claims from the supplied project without a fresh full bibliography audit.
