# CAASP Analysis

The purpose of this analysis is to investigate factors associated with student academic performance in California.

# Methodology and assumptions

## Definitions

In California, much administration, funding, and educator training is handled through organizations specialized in educational administration and support services. These County Offices of Education, or COEs, may operate schools, provide training, handle county-level grants, run educational initiatives, and generally provide other services. As they have so much to do with education, it stands to reason that they may have an impact on students' educational attainment.

CAASP is the California state exam. It is one of the most widely available standardized measures of academic performance in California. While some schools may have better exams, schools' self-assigned grades may vary due to grading standards. Moreover, schools may get funding depending on their students' success, which could create incentives that complicate comparisons. As a result, I elect to approximate students' actual educational attainment via their CAASP scores.

## Assumptions and Definitions

COE size is approximated by the number of schools associated with that COE, and CAASP scores are restricted to only CAASP Math.

While CAASP Math is not a reliable reflection of the entirety of student performance, it is one of the most consistently-available scores. I thus use CAASP Math as an approximation for general academic attainment, because it is a useful, consistent, and readily available proxy for academic performance.

## Methods

TODO: write this :)

1. Obtain school metadata from the California School Directory.

2. Scrape CAASP Mathematics scores from the California School Dashboard.

3. Merge school metadata and CAASP records.

4. Associate schools with their respective County Offices of Education.

5. Compute COE size as the number of schools associated with each county.

6. Aggregate school-level performance metrics to the county level.

7. Obtain auxiliary datasets

7a. Obtain SAIPE data

SAIPE contains data about poverty and income. It's rather limited, as it is recorded per county, but this is better than no data.

The dataset for 2024 can be found [as a downloadable text file](https://www2.census.gov/programs-surveys/saipe/datasets/2024/2024-state-and-county/est24-ca.txt); it was obtained from the SAIPE State and County Estimates for 2024 [web page](https://www.census.gov/data/datasets/2024/demo/saipe/2024-state-and-county.html). Its interpretation is [in a special document](https://www2.census.gov/programs-surveys/saipe/technical-documentation/file-layouts/state-county/2024-estimate-layout.txt), which are listed on [the State and County Estimate Layouts page](https://www.census.gov/programs-surveys/saipe/technical-documentation/file-layouts/state-county.html). Since this data is not in a conventional structured data format, custom parsing rules were required.

8. Estimate linear regressions

8a. Regression relating average county CAASP performance to COE size.

We began by determining whether a linear relationship existed. By estimating a linear model relating CAASP scores to COE size, we were able to discern that a small but significant positive correlation existed between CAASP scores and COE size.

8b. Regression relating average county CAASP performance to COE size and median household income.

This estimate informed us that a significant positive correlation existed between CAASP scores and median household income per county. However, this decreased the significance of the COE size coefficient, placing it just ouside the 0.05 confidence level. This suggests that COE size and median household income are correlated in some way, and one may act as a confounder for the other.

9. Produce maps and visualizations of the resulting dataset.

## Data Sources

I sourced a list of schools and school metadata from [California School Directory's](https://www.cde.ca.gov/SchoolDirectory/) and the [CDE export tool](https://www.cde.ca.gov/SchoolDirectory/ExportSelect?search=&allSearch=&tab=1&order=0&qdc=1520&qsc=26211&simpleSearch=Y&sax=true). If you'd like to get this data yourself, use the "Check All" button, then press "Export Text" at the bottom.

CAASP scores were not yet aggregated in a convenient manner, so I had to scrape them from [California School Dashboard](https://www.caschooldashboard.org) using a Python script.

## Limitations

This analysis is exploratory and correlational.

Several important factors are not controlled for, including:

- school-level household income
- race and ethnicity
- English learner status
- urbanization
- school funding
- chronic absenteeism

As a result, any observed relationship between COE size and CAASP performance should not be interpreted as causal.

# Observations

At the county level:
- Statistically significant relation between COE size and CAASP performance
  - Variable: COE size
    - P-value of 0.01092 is significant at the 0.05 alpha level
    - Coefficient of 0.024853 suggests that each additional school in a COE is correlated to a roughly 0.025 point increase in average CAASP score at that COE
  - Summary: COE size is a statistically significant predictor for CAASP performance
- Statistically significant relation between county-level median income and CAASP performance, even when COE size is accounted for
  - Variable: COE size
    - P-value of 5.847908e-02 is not significant at the 0.05 alpha level
    - Coefficient of 0.013439 suggests that each additional school in a COE is correlated to a roughly 0.01 point increase in average CAASP score at that COE
  - Variable: Median household income
    - P-value of 1.122515e-09 is significant at the 0.05 alpha level
    - Coefficient of 0.000634 suggests that every $1,000.00 in median income per household in a county is correlated to about 0.634 points in CAASP score at that COE
  - Summary: Median income seems to be a statistically significant predictor for CAASP performance, but COE size might not be; it would seem that income is a confounder for county size, and perhaps larger counties just tend to be wealthier. This suggests that the original relationship between COE size and CAASP performance may be partly explained by income differences across counties, rather than COE size alone. Interpretation must therefore be cautious.

# Analysis

TODO: analyze the results :3

Initial results are consistent with a possible economies-of-scale explanation, but the current analysis does not establish this mechanism.

# Execution notes

- requires several mathematics libraries
  - numpy
    - specific version required due to python jank; use `pip install "numpy<2" --upgrade`
  - scipy
  - matplotlib
- may require libraries for scraping if you're running that part
  - urllib
  - bs4

Furthermore, this code is intended for Python 3.12. Newer or older versions may fail to function properly. It was tested on a MacOS machine on Apple Silicon; systems with incompatible matrix routines may differ in float handling.

# Future Work

- Control for median household income.
- Control for demographic variables.
- Control for English learner status.
- Control for foster youth and homelessness.
- Incorporate urbanization and population density.
- Extend the analysis to the school level.
- Compare predictive models against simple linear regression.
- Investigate schools that substantially outperform expectations.

# TODO

## Immediate Next Steps

- [ ] Complete the Methods section.
- [ ] Obtain at least one additional county-level dataset for use as a control variable.
- [ ] Extend the model from simple linear regression to multiple linear regression.
- [ ] Re-estimate the relationship between COE size and CAASP performance after introducing controls.

## Candidate Control Variables

- [ ] Median household income.
- [ ] Poverty rate.
- [ ] Race and ethnicity.
- [ ] English learner percentage.
- [ ] Foster youth percentage.
- [ ] Homeless student percentage.
- [ ] Chronic absenteeism.
- [ ] Population density.
- [ ] Urban/rural classification.

## Future Directions

- [ ] Move from county-level analysis to school-level analysis.
- [ ] Compare linear models against regularized models.
- [ ] Compare linear models against tree-based methods.
- [ ] Identify schools that substantially outperform model predictions.
- [ ] Investigate whether economies of scale remain after controlling for demographics and income.

