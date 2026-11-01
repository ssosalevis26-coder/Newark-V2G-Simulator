const $ = (id) => document.getElementById(id);
const inputFields = [...document.querySelectorAll('[data-key]')];
let defaults = null;
let debounceTimer = null;
let requestVersion = 0;

const money = (value) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value || 0);
const number = (value, digits = 0) => new Intl.NumberFormat('en-US', { maximumFractionDigits: digits, minimumFractionDigits: digits }).format(value || 0);

function setInputs(config) {
  const f = config.fleet, e = config.event, t = config.technical, v = config.value_scenarios, c = config.capital_costs, o = config.operating_costs;
  const values = {
    bus_count: f.bus_count.value, available_buses: f.available_for_peak_event.value,
    battery_kwh: f.battery_capacity_kwh_per_bus.value,
    starting_soc: f.starting_soc_fraction.value * 100,
    departure_soc: f.minimum_departure_soc_fraction.value * 100,
    charger_kw: e.dispatch_power_limit_kw_per_bus.value,
    event_hours: e.duration_hours.value, events_per_year: e.events_per_year.value,
    site_export_limit_kw: e.site_export_limit_kw.value,
    discharge_efficiency: (t.discharge_efficiency?.value ?? 0.96) * 100,
    round_trip_efficiency: t.round_trip_efficiency.value * 100,
    available_hours_per_week: t.availability_hours_per_week.value,
    regulation_power_kw: t.regulation_dispatch_power_kw_per_vehicle.value,
    regulation_throughput_ratio: t.regulation_average_power_throughput_ratio.value * 100,
    electricity_rate: v.retail_energy_cost_usd_per_kwh.value,
    price_low: v.regulation_price_usd_per_mwh.low.value,
    price_central: v.regulation_price_usd_per_mwh.central.value,
    price_high: v.regulation_price_usd_per_mwh.high.value,
    aggregator_fee_fraction: o.aggregator_fee_fraction_of_gross_market_revenue.value * 100,
    battery_wear_cost: o.battery_wear_cost_usd_per_kwh_throughput.value,
    maintenance_cost: o.annual_maintenance_cost_usd.value,
    site_cost: c.site_make_ready_installation_proxy_usd.value,
    ac_incremental_cost_per_kw: c.ac_v2g_incremental_cost_usd_per_kw.value,
    dc_charger_cost_per_bus: c.dc_v2g_charger_reference_usd_per_unit.value,
    asset_life_years: c.asset_life_years.value,
    discount_rate: c.discount_rate_fraction.value * 100
  };
  for (const field of inputFields) {
    field.value = values[field.dataset.key] ?? '';
  }
  $('cost-case').value = c.v2g_cost_case;
}

function readInputs() {
  const result = { cost_case: $('cost-case').value };
  for (const field of inputFields) {
    const key = field.dataset.key;
    if (field.value.trim() === '') {
      if (key === 'transmission_upgrade_cost_usd') result[key] = null;
      else throw new Error(`Enter ${key.replaceAll('_', ' ')}; only transmission cost may be blank.`);
      continue;
    }
    const value = Number(field.value);
    if (!Number.isFinite(value)) throw new Error(`Check the ${key.replaceAll('_', ' ')} input.`);
    if (key === 'starting_soc' || key === 'departure_soc' || key === 'aggregator_fee_fraction' || key === 'round_trip_efficiency' || key === 'discharge_efficiency' || key === 'discount_rate' || key === 'regulation_throughput_ratio') {
      result[key] = value / 100;
    } else {
      result[key] = value;
    }
  }
  return result;
}

function toast(message) {
  document.querySelector('.error-toast')?.remove();
  const node = document.createElement('div');
  node.className = 'error-toast';
  node.textContent = message;
  document.body.append(node);
  setTimeout(() => node.remove(), 4500);
}

async function calculateNow() {
  const version = ++requestVersion;
  try {
    const response = await fetch('/api/calculate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(readInputs()) });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Could not calculate this scenario.');
    if (version !== requestVersion) return;
    $('calculation-status').textContent = 'Results reflect the current inputs.';
    render(result);
  } catch (error) {
    if (version !== requestVersion) return;
    $('calculation-status').textContent = `Results are from the last valid scenario. ${error.message}`;
    toast(error.message);
  }
}

function render(result) {
  const p = result.peak_event, m = result.regulation, capital = result.capital;
  const low = m.scenarios.low, central = m.scenarios.central, high = m.scenarios.high;
  $('event-duration-label').textContent = `Across a ${number(p.event_duration_hours, 1)}-hour event`;
  $('event-pill').textContent = `${number(p.event_duration_hours, 1)} HOURS`;
  $('fleet-chip').textContent = `${p.active_buses} connected buses`;
  $('hero-energy').textContent = `${number(p.export_energy_per_event_kwh)} kWh`;
  $('hero-power').textContent = `${number(p.average_export_power_kw)} kW`;
  $('central-net').textContent = money(central.annualized_net_after_capital_usd);
  $('central-operating').textContent = money(central.operating_net_usd);
  $('annualized-capital').textContent = money(central.annualized_capital_cost_usd);
  $('low-net').textContent = money(low.annualized_net_after_capital_usd);
  $('high-net').textContent = money(high.annualized_net_after_capital_usd);
  $('low-gross').textContent = money(low.gross_revenue_usd);
  $('high-gross').textContent = money(high.gross_revenue_usd);
  $('battery-energy').textContent = `${number(p.available_battery_energy_dc_kwh)} kWh DC`;
  $('event-power').textContent = `${number(p.average_export_power_kw)} kW`;
  $('annual-event-energy').textContent = `${number(p.annual_export_energy_kwh / 1000, 2)} MWh`;
  $('nameplate-capacity').textContent = `${number(p.nameplate_export_capacity_kw)} kW nameplate`;
  const fillPct = p.nameplate_export_capacity_kw > 0 ? Math.min(100, p.average_export_power_kw / p.nameplate_export_capacity_kw * 100) : 0;
  $('capacity-fill').style.width = `${fillPct}%`;
  $('gross-revenue').textContent = money(central.gross_revenue_usd);
  $('loss-cost').textContent = `−${money(central.recharge_loss_cost_usd)}`;
  $('aggregator-fee').textContent = `−${money(central.aggregator_fee_usd)}`;
  $('wear-cost').textContent = `−${money(central.battery_wear_cost_usd)}`;
  $('maintenance-result').textContent = money(central.maintenance_cost_usd);
  $('equipment-result').textContent = money(capital.equipment_capex_usd);
  $('site-result').textContent = money(capital.site_make_ready_proxy_usd);
  $('transmission-result').textContent = capital.transmission_upgrade_cost_usd === null ? 'Not estimated - excluded' : money(capital.transmission_upgrade_cost_usd);
  $('bus-result').textContent = money(capital.electric_bus_reference_total_usd);
  $('dc-result').textContent = money(capital.dc_charger_reference_total_usd);
  $('payback-result').textContent = central.simple_payback_years === null ? 'No positive operating net' : `${number(central.simple_payback_years, 1)} years`;
  $('selected-capex').textContent = money(capital.total_project_capital_usd);
  $('selected-cost-note').textContent = `${capital.equipment_label} + site proxy${capital.transmission_upgrade_cost_usd ? ' + entered transmission cost' : ''}. Full bus acquisition is shown separately.`;
  renderChart({ low: low.annualized_net_after_capital_usd, central: central.annualized_net_after_capital_usd, high: high.annualized_net_after_capital_usd });
  $('limitation-list').innerHTML = result.limitations.map(item => `<li>${escapeHtml(item)}</li>`).join('');
}

function renderChart(values) {
  const max = Math.max(...Object.values(values).map(v => Math.abs(v)), 1);
  const chart = $('scenario-chart');
  chart.innerHTML = '';
  for (const key of ['low', 'central', 'high']) {
    const row = document.createElement('div');
    row.className = 'bar-row';
    const label = document.createElement('span'); label.className = 'bar-label'; label.textContent = key;
    const track = document.createElement('div'); track.className = 'bar-track';
    const fill = document.createElement('div'); fill.className = `bar-fill ${key}`; fill.style.width = `${Math.abs(values[key]) / max * 50}%`; fill.style.marginLeft = values[key] < 0 ? `${50 - Math.abs(values[key]) / max * 50}%` : '50%'; fill.classList.toggle('negative', values[key] < 0); track.append(fill);
    const value = document.createElement('span'); value.className = 'bar-value'; value.textContent = money(values[key]);
    row.append(label, track, value); chart.append(row);
  }
}

function escapeHtml(value) {
  return value.replace(/[&<>"']/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]));
}

function scheduleCalculate() {
  requestVersion++;
  $('calculation-status').textContent = 'Updating; displayed results belong to the previous valid scenario.';
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(calculateNow, 120);
}

inputFields.forEach((field) => field.addEventListener('input', scheduleCalculate));
$('cost-case').addEventListener('change', scheduleCalculate);
$('reset-button').addEventListener('click', () => { setInputs(defaults); calculateNow(); });

fetch('/api/defaults').then(response => response.json()).then(config => {
  defaults = config;
  setInputs(config);
  renderEvidence(config);
  calculateNow();
}).catch(() => toast('Could not load default assumptions. Try restarting the Python server.'));

function renderEvidence(config) {
  const rows = [];
  function visit(object, path = '') {
    for (const [key, entry] of Object.entries(object)) {
      if (!entry || typeof entry !== 'object') continue;
      if ('value' in entry) {
        rows.push(`<tr><th scope="row">${escapeHtml((path + key).replaceAll('_', ' '))}</th><td>${escapeHtml(String(entry.value ?? 'Not estimated'))} ${escapeHtml(entry.unit || '')}</td><td>${escapeHtml(entry.evidence || 'See specification')}</td><td>${escapeHtml(entry.source || 'Scenario assumption / unknown')}<br>${escapeHtml(entry.note || '')}</td></tr>`);
      } else visit(entry, path + key + ' / ');
    }
  }
  visit(config);
  $('evidence-body').innerHTML = rows.join('');
}
