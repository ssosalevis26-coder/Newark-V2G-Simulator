# Newark V2G Fleet Value Simulator

A small, source-linked Python project that estimates (1) the energy a hypothetical 14-bus University of Delaware fleet could export during a summer peak event and (2) a separate annual PJM Regulation value sensitivity. The same electric buses are used in both comparison cases; the model isolates the incremental value of adding V2G.

## Run it

You only need Python 3.10 or newer. The app uses Python's standard library and needs no package installation.

1. Open a terminal in this project folder.
2. Run:

   ```bash
   python app.py
   ```

3. Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.
4. Stop the server with `Ctrl+C` in the terminal.

On Windows, `py app.py` also works if the `python` command is not available.

## Run the tests

```bash
python -m unittest discover -s tests -v
```

## Default scenario preview

- **Peak event:** 14 buses, 155 kWh per bus, 90% starting charge, and 70% minimum departure charge. This leaves 434 kWh of battery energy above the route reserve across the fleet. At the 96% measured discharge-efficiency comparator, the model estimates about **417 kWh exported per three-hour event**, or about **139 kW average**. At 20 events per year, that is about **8.33 MWh/year**.
- **PJM Regulation sensitivity:** Uses 29 kW per bus and 128 available market hours per week, matching a published UD/Exelon report’s “40 hours unavailable” comparator. With the defaults, modeled annual net after fees, wear, and annualized AC equipment/site proxy is about **$5,392 low / $40,099 central / $83,076 high**. These are scenario outputs, not expected UD savings.
- **Selected capital case:** $16,800 for the published $20/kW AC V2G incremental manufacturing estimate, plus a $113,573 one-project site make-ready proxy, for $130,373 total. A separate DC charger comparison uses the WRI-reported $89,930 per 60 kW V2G charger. Neither number is a Newark quote.

The event-energy scenario and annual Regulation scenario are calculated separately. Do not add their values. The event count changes physical annual energy only; the Regulation estimate uses its own historical market availability assumption.

## Project files

- `app.py` — no-dependency local HTTP server and JSON API.
- `v2g_model.py` — validated calculations and scenario outputs.
- `static/` — responsive web demo.
- `config/scenario_defaults.json` — editable defaults with source and evidence labels.
- `PROJECT_SPEC.md` — model decisions, equations, cost treatment, and scope.
- `CODEX_BUILD_PROMPT.md` — reusable prompt for further Codex development.
- `SOURCES.md` — bibliography and data-use notes.
- `tests/` — calculation and input-validation tests.

## Evidence and limitations

Published comparison data does not make the modeled buses actual UD assets. The bus battery and 60 kW charger use WRI school-bus examples; market dispatch and efficiency use a UD/Exelon EV pilot report; and Newark's 2024 rate study is used as a UD-class tariff proxy that must be checked against a current bill or contract. The $20/kW AC figure is an estimated mass-production increment, not a complete installed price. The installation proxy is inferred from a separate WRI project package and is not a transmission upgrade quote.

The model does not estimate Newark feeder hosting capacity, a specific avoided transmission upgrade, confirmed PJM qualification, current utility payment, actual UD route energy, emissions, or battery warranty impacts. Demand-charge savings are not calculated. All uncertain inputs can be changed in the demo and are labeled in `PROJECT_SPEC.md` and `SOURCES.md`.

## Configuration

Edit `config/scenario_defaults.json` to change defaults. Source notes are kept beside the values. The web controls override defaults for that browser session without modifying the file.

## Clean setup (Windows PowerShell)

Python 3.10+ is required. No third-party packages, API keys, accounts, or paid services are needed. From this project directory:

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\python.exe app.py
```

Open http://127.0.0.1:8000. Stop with Ctrl+C. In a second terminal, run:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

On macOS/Linux, use `python3 -m venv .venv`, then `.venv/bin/python app.py` and `.venv/bin/python -m unittest discover -s tests -v`. There is no dependency install step; requirements.txt intentionally contains no packages. If port 8000 is busy, stop the previous demo before starting another instance. Run commands from the project root; no activation script is required.

## Interpretation and financial boundary

The shared connected-bus count affects both scenarios. Event duration, event count, departure reserve, and discharge efficiency affect physical event capability only. Market availability uses a separate weekly-hours assumption. Regulation bid power is capped by connected buses, charger power, and the entered site ceiling. This is a capacity/throughput benchmark, not a simulation proving battery reserve can support every regulation signal.

Regulation revenue subtracts incremental round-trip loss energy once, aggregator fees, throughput-based wear, and the annual maintenance allowance (excluded by default). It then subtracts selected equipment plus the one-site installation proxy annualized with a capital recovery factor. Bus purchase cost and normal driving/charging energy are excluded because the baseline already contains the same electric fleet. Taxes, incentives, financing fees, and unquoted project costs are excluded. Simple payback divides selected upfront cost by positive operating net before annualization; it is not discounted payback.

Transmission cost stays null / not estimated until a supported site-specific estimate is supplied. Its exclusion makes the result incomplete, not evidence that transmission work is free. No upgrade need or deferral value is predicted. The AC manufacturing increment and DC unit-price case are alternatives, not equivalent turnkey offers. The site proxy is applied once, without claiming it scales to a 14-bus depot. Event exports have no modeled revenue or savings and are never added to annual regulation value. Historical price cases can be edited and need not remain ordered.

The evidence register shows original defaults. Edited inputs are user assumptions. Dates and bibliography are retained in SOURCES.md; this engineering revision did not independently re-verify every external publication or current tariff. Confirm original reports and applicable contracts before using numbers beyond a portfolio illustration.

## Verification in this revision

The original 11 tests passed before edits. The expanded suite contains 18 tests covering independent financial arithmetic, reserve/energy limits, power ceilings, invalid and non-finite inputs, fractional counts, scenario separation, null transmission cost, payback, and HTTP success/error/static-file behavior. Browser checks are described in the delivery notes; unit/API tests do not constitute an accessibility certification or utility feasibility study.

Verified locally with Python 3.14.7 in a newly created `.venv`: all 18 tests passed. The local server started and served the page, JS, CSS, source document, defaults endpoint, and calculation API. Browser checks confirmed default results ($40,099 central annualized net; 417 kWh/event), a 6-hour event (69 kW average), negative DC-case net/chart, fractional-count error status, and reset. The observed 615 px viewport had no horizontal page overflow. Other Python versions, screen readers, and a broad device/browser matrix were not exercised.
