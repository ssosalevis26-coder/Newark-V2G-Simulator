# Sources

This file records research and data sources used to develop the Newark V2G Fleet Value Simulator. Sources are grouped by type so readers can distinguish peer-reviewed research from observed data, official reports, product documentation, and scenario assumptions.

**Access date for web sources:** October 17, 2026, unless a different date is stated below.

## Peer-Reviewed Research

### V2G foundations and implementation

- Guille, Christophe, and George Gross. “A Conceptual Framework for the Vehicle-to-Grid (V2G) Implementation.” *Energy Policy* 37, no. 11 (2009): 4379–4390. https://doi.org/10.1016/j.enpol.2009.05.053.  
  **Use in this project:** Conceptual grounding for aggregating vehicles as grid resources and representing control, communication, and incentives. This is a framework source, not a source for Newark-specific values.

- Kempton, Willett, and Jasna Tomić. “Vehicle-to-Grid Power Fundamentals: Calculating Capacity and Net Revenue.” *Journal of Power Sources* 144, no. 1 (2005): 268–279. https://doi.org/10.1016/j.jpowsour.2004.12.025.  
  **Use in this project:** Foundation for estimating available V2G power and net revenue. Any implementation must adapt the paper’s concepts to the selected bus, charger, tariff, and operating assumptions.

- Lund, Henrik, and Willett Kempton. “Integration of Renewable Energy into the Transport and Electricity Sectors through V2G.” *Energy Policy* 36, no. 9 (2008): 3578–3587. https://doi.org/10.1016/j.enpol.2008.06.007.  
  **Use in this project:** Background on coordinating transport, electricity systems, V2G, and renewable integration. The article’s system-level findings are not direct predictions for Newark.

### Social and adoption considerations

- Sovacool, Benjamin K., Jonn Axsen, and Willett Kempton. “The Future Promise of Vehicle-to-Grid (V2G) Integration: A Sociotechnical Review and Research Agenda.” *Annual Review of Environment and Resources* 42 (2017): 377–406. https://doi.org/10.1146/annurev-environ-030117-020220.  
  **Use in this project:** Context for implementation barriers and sociotechnical considerations alongside technical performance.

- Sovacool, Benjamin K., Lance Noel, Jonn Axsen, and Willett Kempton. “The Neglected Social Dimensions to a Vehicle-to-Grid (V2G) Transition: A Critical and Systematic Review.” *Environmental Research Letters* 13, no. 1 (2018): 013001. https://doi.org/10.1088/1748-9326/aa9c6d.  
  **Use in this project:** Systematic review that motivates treating participation and implementation issues as relevant to V2G adoption, not just battery and grid calculations.

### V2G revenue, aggregation, and metering

- Metz, John G., and Willett Kempton. “Vehicle-to-Grid Revenue from Retail Time-of-Day Rates, Compared with Wholesale Market Participation under FERC Order 2222.” *Energies* 17, no. 11 (2024): 2664. https://doi.org/10.3390/en17112664.  
  **Use in this project:** Directly relevant framework for comparing retail time-of-use value with wholesale-market revenue from storage. The paper’s tariffs, market prices, and participation assumptions are not Newark or UD-specific; use it to guide scenario structure, not as a Newark revenue forecast.

- Mironenko, Olga, Garrett A. Ejzak, and Willett Kempton. “Integrated Electric Vehicle Shunt Current Sensing System for Concurrent Revenue Metering and Detection of DC Injection.” *Energies* 14, no. 4 (2021): 1193. https://doi.org/10.3390/en14041193.  
  **Use in this project:** Technical context on EV charging equipment metering and DC-injection detection. It does not establish the cost or certification status of any charger selected for this scenario.

- Nakano, Hikari, Ikumi Nawata, Shinkichi Inagaki, Akihiko Kawashima, Tatsuya Suzuki, Akira Ito, and Willett Kempton. “Aggregation of V2H Systems to Participate in Regulation Market.” *IEEE Transactions on Automation Science and Engineering* 18, no. 2 (2021): 668–680. https://doi.org/10.1109/TASE.2020.3001060.  
  **Use in this project:** Methods context for aggregating vehicle-based systems for regulation services. The study concerns vehicle-to-home systems and is not a direct model of UD buses or PJM bus-fleet participation.

### Additional conference research

- Kempton, Willett. “Electric Vehicles and Deploying Vehicle-to-Grid Power.” *Energy, COVID, and Climate Change*, 1st IAEE Online Conference, June 7–9, 2021. International Association for Energy Economics. https://iaee2021online.org/plenaryprogramme.html.  
  **Source type:** Conference presentation/program listing; peer-review status not established from the available record.  
  **Use in this project:** Background on V2G deployment. Treat it as contextual conference material, not as a peer-reviewed journal article or source of UD-specific parameters.

### Electric school bus economics and operations

- Noel, Lance, and Regina McCormack. “A Cost-Benefit Analysis of a V2G-Capable Electric School Bus Compared to a Traditional Diesel School Bus.” *Applied Energy* 126 (2014): 246–255. https://doi.org/10.1016/j.apenergy.2014.04.009.  
  **Use in this project:** Historical economic case study for a V2G-capable school bus. Its vehicle, market, and cost assumptions are period- and location-specific and should not be copied as current Newark prices.

- Shirazi, Yosef, Edward Carr, and Lauren Knapp. “A Cost-Benefit Analysis of Alternatively Fueled Buses with Special Considerations for V2G Technology.” *Energy Policy* 87 (2015): 591–603. https://doi.org/10.1016/j.enpol.2015.09.038.  
  **Use in this project:** Historical case study of alternative-fuel bus economics, including cold-temperature effects and V2G revenues. Its inputs reflect the study’s time and setting and should not be presented as current Newark prices.

## Datasets

- National Laboratory of the Rockies (NLR). “Hourly Electricity Demand Profiles for Each County in the Contiguous United States, 2016–2023.” Data.gov catalog record. https://catalog.data.gov/dataset/hourly-electricity-demand-profiles-for-each-county-in-the-contiguous-united-states. Dataset landing page: https://data.openei.org/submissions/8562. Download: https://data.openei.org/files/8562/historic_load_hourly_2016_2023_county.h5.  
  **Use in this project:** Estimated hourly demand profile for New Castle County as a time-shape proxy. It is county-level modeled/allocated data, not Newark meter data. If scaled to Newark’s measured annual peak, label the result a modeled Newark profile. The dataset uses UTC hour-ending timestamps and is licensed CC BY 4.0.

- National Laboratory of the Rockies (NLR). “National Summary Statistics for Depot-Based Medium- and Heavy-Duty Vehicle Operations.” NLR Data Catalog. https://data.nlr.gov/submissions/231.  
  **Use in this project:** Generic operating-pattern context for depot-based vehicles, including transit buses and school buses. It is not UD vehicle-level route or schedule data.

- World Resources Institute, Electric School Bus Initiative. “Dataset of U.S. Electric School Bus Adoption.” https://electricschoolbusinitiative.org/dataset-us-electric-school-bus-adoption.  
  **Use in this project:** Context on U.S. electric school bus deployment and adoption. It does not provide UD shuttle bus specifications.

- World Resources Institute, Electric School Bus Initiative. “Dataset of U.S. School Bus Fleets.” https://electricschoolbusinitiative.org/dataset-us-school-bus-fleets.  
  **Use in this project:** Fleet composition context, including bus types and manufacturers where available. School bus data should not be treated as a direct description of UD’s campus shuttle fleet.

## Technical Reports (Not Peer-Reviewed Journal Articles)

- Kempton, Willett, Garrett A. Ejzak, Safoura Faghri, Catherine M. Gilman, Maria Mediavilla Gallano, John G. Metz, and Rafael B. S. Veras. *Evaluating the Capabilities and Value of V2G Grid Services in Fleet Operations*. Final report for Exelon Corporate Strategy – Technology and R&D, March 31, 2026; minor corrections through June 8, 2026. University of Delaware Center for Research in Wind. https://bpb-us-w2.wpmucdn.com/sites.udel.edu/dist/5/8632/files/2026/06/UD-Exelon-Report-V2G-Fleet-Operation-2026.pdf.  
  **Use in this project:** Closest local technical comparator: a four-EV UD/Exelon/Delmarva pilot, PJM Regulation and Delmarva Power TOU analyses, 90% round-trip efficiency, measured 29 kW regulation dispatch from 33 kW-rated vehicles, and modeled annual value using 2021–2025 PJM regulation prices. Its annual revenue numbers are calculations from recorded signals and historical prices; PJM did not pay the pilot for those test dispatches. The report’s AC V2G incremental manufacturing-cost estimate of $20/kW is not a turnkey or installed quote.

## Government and Utility Reports

- Delaware Department of Natural Resources and Environmental Control (DNREC). *Interim Project Report: Baseline Conditions Assessment*. December 17, 2025. https://documents.dnrec.delaware.gov/energy/office/Grid-Analysis-Interim-Report-20251217.pdf.  
  **Use in this project:** Table 26 reports DEMEC member summer peak demand in 2020–2024, including Newark: 90.2 MW (2020), 94.1 MW (2021), 94.6 MW (2022), 94.0 MW (2023), and 87.5 MW (2024). These are annual city/utility peak values, not hourly feeder data.

- Delaware Department of Natural Resources and Environmental Control (DNREC). “Analysis of Delaware’s Electricity Distribution Grid.” https://dnrec.delaware.gov/climate-coastal-energy/energy-office/resilience/grid-study/.  
  **Use in this project:** Statewide distribution-grid planning and reliability context. Statewide findings do not establish the operating limits of a Newark feeder.

- City of Newark, Delaware. “Electrical Engineering.” https://newarkde.gov/18/Electrical-Engineering.  
  **Use in this project:** Description of the municipal electric utility and city distribution system. This page does not provide a feeder model or hourly load data.

- City of Newark, Delaware. “Delaware Municipal Electric Corporation.” https://newarkde.gov/1008/Delaware-Municipal-Electric-Corporation.  
  **Use in this project:** Newark utility context and published citywide peak-load information.

- City of Newark, Delaware. “Understanding Electric Demand Charges.” https://newarkde.gov/DocumentCenter/View/21398/Understanding-Electric-Demand-Charges.  
  **Use in this project:** Explains Newark’s residential demand charge introduced in 2026. The residential rate must not be applied to a campus or fleet meter unless that meter is actually billed under the residential class.

- City of Newark, Delaware. Bill No. 25-36, proposed ordinance revising electric rates effective January 1, 2026. https://newarkde.gov/DocumentCenter/View/21003/9E.  
  **Use in this project:** Candidate source for proposed 2026 rate schedules. The copy reviewed showed the second-reading field blank; verify the adopted tariff and the specific meter’s class before using these figures as actual rates.

- City of Newark, Delaware. *Newark Electric Rate Design as of May 29, 2024*. https://newarkde.gov/DocumentCenter/View/18860/4A.  
  **Use in this project:** Historical rate-design study with projected fiscal-year rates, including a UD large-light-and-power entry. It is a forecast/rate-design document, not confirmation of the current UD bill or contract terms.

- Delaware Municipal Electric Corporation (DEMEC). “Power Savers Program.” https://www.demecinc.net/sustainability/powersavers/.  
  **Use in this project:** Describes typical summer peak periods (generally 2–6 p.m.) for demand-response context. It does not establish a V2G payment rate or fleet eligibility.

- U.S. Energy Information Administration (EIA). “Delaware Electricity Profile 2024.” https://www.eia.gov/electricity/state/delaware/.  
  **Use in this project:** State-level electricity statistics. Do not treat state averages as Newark meter rates or feeder measurements.

- U.S. Department of Energy, Loan Programs Office. “LPO Announces Conditional Commitment to Zum Services, Inc. to Deploy Battery-Electric School Buses with V2G Capability, Creating Virtual Power Plants Nationwide.” January 17, 2025. https://stage.energy.gov/edf/articles/lpo-announces-conditional-commitment-zum-services-inc-deploy-battery-electric-school.  
  **Use in this project:** Example of a large proposed V2G school-bus deployment. Announced project totals are not specifications for UD buses.

- U.S. Department of Energy, Alternative Fuels Data Center (AFDC). *Electric School Bus U.S. Market Study and Buyer’s Guide*. https://afdc.energy.gov/files/u/publication/electric-school-bus-us-market-study-buyers-guide.pdf.  
  **Use in this project:** Historical planning ranges for charger equipment and installation. These ranges are not current vendor quotes and exclude potential grid-upgrade costs.

## Bus and Charger Documentation

- University of Delaware, Transportation. “Transportation.” https://sites.udel.edu/transportation/.  
  **Use in this project:** UD reports a fleet that includes 14 buses. The page does not establish that these buses are electric or V2G-capable and does not publish their battery specifications. The 14-bus case in this simulator is a UD fleet-size scenario, not a claim about the buses’ technology.

- University of Delaware, Transportation. “Bus Routes 2025–2026.” https://sites.udel.edu/transportation/bus-routes-2024-2025-copy/.  
  **Use in this project:** Public service-route context. Published route timetables do not identify each vehicle’s depot arrival/departure times, state of charge, or energy use.

- World Resources Institute, Electric School Bus Initiative. “Latest Lessons from Electric School Bus Vehicle-to-Grid Programs.” May 21, 2025. https://electricschoolbusinitiative.org/latest-lessons-electric-school-bus-vehicle-grid-programs.  
  **Use in this project:** Reports a Portland General Electric demonstration using a 155 kWh bus and 60 kW bidirectional charger, with three-hour discharge tests. This is a comparison case, not UD equipment.

- World Resources Institute, Electric School Bus Initiative. “Vehicle to Grid Charging in Cajon Valley.” https://www.wri.org/update/electric-school-bus-series-powering-grid-cajon-valley-union-school-district.  
  **Use in this project:** Case-study context for 132/169 kWh buses, 60 kW bidirectional chargers, reported bus discharge power, and site upgrades. Costs and program payments are specific to that California project and must not be transferred to Newark as actual prices.

- Wang, Jessica, and Eleanor Jackson. “The Electric School Bus Series: How North Carolina’s Eastern Band of Cherokee Indians Is Planning for Seven Generations of Sustainability.” World Resources Institute, August 4, 2022. https://www.wri.org/update/electric-school-bus-series-how-north-carolinas-eastern-band-cherokee-indians-planning-seven.  
  **Use in this project:** Published case-specific price evidence: one reported V2G bus at $341,957, a 60 kW DC fast charger at $89,930, and $545,460 for a bus, charger, and installation package. The difference ($113,573) is used only as an inferred, one-project make-ready/installation proxy, not a separately quoted transmission upgrade or Newark estimate.

- Heliox. “Heliox 60 kW V2G EV Charger.” https://www.heliox-energy.com/us-products/heliox-60-kw-v2g.  
  **Use in this project:** Manufacturer product documentation for a commercial bidirectional charger. The page reviewed did not provide a purchase price.

- EPRI OpenDSS. “Examples, Docs and Test Cases.” https://opendss.epri.com/ExamplesDocsandTestCases.html.  
  **Use in this project:** Public OpenDSS implementations of IEEE distribution test feeders for demonstration and validation. A test feeder is not Newark’s actual network.

## Model Assumptions

The following are scenario inputs unless a specific project source is added:

- Fleet size: 14 buses as a UD fleet-size scenario. This does not mean UD’s buses are electric or V2G-capable.
- Bus battery capacity, usable state-of-charge range, charge/discharge power, efficiency, degradation, and minimum departure charge.
- Bus availability during summer peak hours and route energy use.
- Number and rating of bidirectional chargers and the site export limit.
- Hourly Newark load shape derived by scaling a New Castle County profile to a Newark annual peak.
- Electricity rate, demand-charge applicability, V2G payment, dispatch-event count, and operating duration unless confirmed for the relevant customer/program.
- Charger price, installation, maintenance, and site-upgrade cost unless supported by a dated quote or directly applicable procurement record.
- Any avoided grid-upgrade cost. Do not report an avoided upgrade as a verified saving without a utility study or project estimate that supports it.

For each input used by the code, record its value, units, source, source date, access date, and evidence type: **measured**, **published**, **vendor quote**, **inferred**, or **scenario assumption**. If the source does not support the input directly, label the input as an assumption rather than implying it is measured.

## Citation and Data-Use Notes

- Cite sources in the README, report, and user interface near the claims or inputs they support.
- Do not use a peer-reviewed paper as the source for a local utility rate, bus specification, or charger quote unless that exact information is actually reported there.
- Preserve downloaded datasets’ original licenses and attribution requirements. The NLR county hourly demand dataset is marked CC BY 4.0 in its catalog record.
- Record any later data downloads, vendor quotes, interviews, or written confirmations here, including their dates and any usage restrictions.

## Engineering revision provenance

The bibliography and numerical evidence above were supplied with the project ZIP. This revision preserved their source claims and corrected the demo's WRI lessons link to the existing bibliography entry. It did not independently audit every publication, access date, quoted value, or current tariff. Treat the access date above as supplied project metadata. No new prices, fleet facts, vendor quotes, or utility study results were introduced.
