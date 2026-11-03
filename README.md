# Property Estimate

A Python-based research project exploring which factors have the greatest influence on real estate prices.

The project will analyze each factor using methods suited to the comparison, bring the findings together, and evaluate their relative importance. A local HTML interface is planned for exploring the results through interactive visualizations.

## Research Questions

- How strongly are school districts associated with property prices?
- How does access to public transportation relate to property values?
- How does proximity to employment centers affect prices?
- How do housing policy changes relate to price movements?
- How do prices differ across higher-, middle-, and lower-tier residential areas?
- How do apartment characteristics interact with location—for example, an older apartment in a higher-tier area versus a newly built apartment in a lower-tier area?

## Analysis Plan

The methods below are initial candidates. Final choices will depend on data availability, data quality, and the assumptions required for each analysis.

| Factor | Planned comparison | Candidate methods |
| --- | --- | --- |
| School districts | Compare prices across school districts and levels of access to schools | Hedonic regression, matched comparisons |
| Public transportation | Compare prices by distance to stations, transit access, and travel time | Spatial regression, generalized additive models |
| Proximity to employment | Compare prices by commute time and access to employment centers | Multiple regression, gradient boosting |
| Government policy | Compare price trends before and after policy changes, using comparison groups where available | Difference-in-differences, event studies, interrupted time-series analysis |
| Area characteristics | Compare higher-, middle-, and lower-tier areas while accounting for property differences | Multilevel regression, stratified comparisons |
| Apartment characteristics | Compare building age, size, and other available features across area tiers | Hedonic regression with interaction terms, matched comparisons, tree-based models |

Area tiers will be defined using documented criteria. If tiers are defined using property prices, they will be treated as descriptive groupings rather than independent explanations of those same prices.

## Bringing the Results Together

1. Assemble transaction data and relevant school, transit, employment, policy, neighborhood, and apartment data.
2. Clean and align the datasets by location and time, and define a consistent price measure.
3. Analyze each factor while accounting for available confounders such as transaction date, location, apartment size, and building age.
4. Record effect estimates, uncertainty, predictive performance, and limitations for each comparison.
5. Fit a combined model and compare factor groups using held-out permutation importance and the change in predictive performance when each group is removed. Use SHAP values where useful to explain model predictions.
6. Summarize which factors show the strongest relationships with prices, and how those relationships vary across locations and time periods.

Feature-importance scores from unrelated models will not be directly combined into a single ranking. The overall comparison will use a shared dataset, target, and evaluation setup, with time-based or geographic validation where appropriate to reduce leakage.

Observed associations and predictive importance do not by themselves establish causation. Policy analyses will require additional checks of their identification assumptions before any causal interpretation.

## Planned Technology

- **Language:** Python
- **Data preparation:** pandas and NumPy
- **Statistical analysis and modeling:** statsmodels and scikit-learn
- **Geospatial analysis:** GeoPandas, where needed
- **Visualization:** Python-generated charts and interactive browser visualizations
- **Local interface:** HTML, CSS, and JavaScript, connected to a local Python backend

The specific libraries and backend framework will be finalized during implementation.

## Planned Local Interface

The application will run locally and provide a browser-based interface for:

- Exploring property prices and factor distributions.
- Comparing results across factors, neighborhoods, and time periods.
- Inspecting charts, maps, model explanations, and uncertainty.
- Reviewing a consolidated report of the factors most strongly associated with prices.

## Roadmap

- [ ] Inventory data sources and document their coverage and definitions.
- [ ] Build a reproducible data-cleaning and feature-engineering pipeline.
- [ ] Establish baseline price models.
- [ ] Implement and validate each factor-specific analysis.
- [ ] Combine findings and evaluate relative factor importance.
- [ ] Build the local HTML interface and interactive visualizations.
- [ ] Document results, limitations, and instructions for running the application.

## Project Status

The project is in the planning and data-preparation stage. The analyses, findings, and local application described above are planned work. Setup and run instructions will be added once an executable application is available.
