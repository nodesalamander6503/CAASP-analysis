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

7. Estimate a linear regression relating average county CAASP performance to COE size.

We began by determining whether a linear relationship existed. By estimating a linear model relating CAASP scores to COE size, we were able to discern that a small but significant positive correlation existed between CAASP scores and COE size.

8. Produce maps and visualizations of the resulting dataset.

## Data Sources

I sourced a list of schools and school metadata from [California School Directory's](https://www.cde.ca.gov/SchoolDirectory/) and the [CDE export tool](https://www.cde.ca.gov/SchoolDirectory/ExportSelect?search=&allSearch=&tab=1&order=0&qdc=1520&qsc=26211&simpleSearch=Y&sax=true). If you'd like to get this data yourself, use the "Check All" button, then press "Export Text" at the bottom.

CAASP scores were not yet aggregated in a convenient manner, so I had to scrape them from [California School Dashboard](https://www.caschooldashboard.org) using a Python script.

## Limitations

This analysis is exploratory and correlational.

Several important factors are not controlled for, including:

- household income
- race and ethnicity
- English learner status
- urbanization
- school funding
- chronic absenteeism

As a result, any observed relationship between COE size and CAASP performance should not be interpreted as causal.

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

