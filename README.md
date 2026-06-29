# CAASPP Analysis

The purpose of this analysis is to investigate factors associated with student academic performance in California. In doing so, we attempt to find correlations between educational performance on the CAASPP math exam and factors including size of a County Office of Education and median household income. We find that while COE size shows a weak positive association with average CAASPP math performance in simple regressions, this relationship becomes statistically insignificant after controlling for median household income, which remains a strong predictor of performance.

More specifically, it stands to reason that the size and scale of local educational facilities may be correlated to the performance of students, as well as the median household income. We therefore investigate the impact of income and the size of a County Office of Education on students' average CAASPP math score per school or County Office of Education.


# Methodology and assumptions

## Background

In California, much administration, funding, and educator training is handled through organizations specialized in educational administration and support services. These County Offices of Education, or COEs, may operate schools, provide training, handle county-level grants, run educational initiatives, and generally provide other services. As they have so much to do with education, it stands to reason that they may have an impact on students' educational attainment. COE size is approximated by the number of schools associated with that COE. That is, if the COE "contains" 6 schools, its COE size is 6. For this analysis, CAASPP data are restricted to math scores. This is to simplify analysis.

CAASPP is the California state exam. It is one of the most widely available standardized measures of academic performance in California. While some schools may have better exams, schools' self-assigned grades may vary due to grading standards. Moreover, schools may get funding depending on their students' success, which could create incentives that complicate comparisons. As a result, I elect to approximate students' actual educational attainment via their CAASPP scores.

To gather data about private and household income, census data was needed. For this, data from the Small Area Income and Poverty Estimates (SAIPE) program was used. SAIPE gathers useful data about income and poverty rates. They are used as our source of California's private/household financial data, as we were unable to find any other reliable source of census data at a sufficiently small level.

## Methods

At a high level, we first scraped and downloaded data, then ran initial statistical analyses, conducted further tests to eliminate issues of confounding variables, and finally generated analyses, interpretations, and images.

Schools' locations, CAASPP math scores, and COE affiliations were scraped. These data were collected initially at the school level, then aggregated into COE-level and county-level averages and sums.

Moreover, SAIPE data were downloaded and parsed from their web page. It is rather limited, as it is recorded per county, but this is better than no data; it required a custom parser to account for its unusual format.

The dataset for 2024 can be found [as a downloadable text file](https://www2.census.gov/programs-surveys/saipe/datasets/2024/2024-state-and-county/est24-ca.txt); it was obtained from the SAIPE State and County Estimates for 2024 [web page](https://www.census.gov/data/datasets/2024/demo/saipe/2024-state-and-county.html). Its interpretation is [in a special document](https://www2.census.gov/programs-surveys/saipe/technical-documentation/file-layouts/state-county/2024-estimate-layout.txt), which are listed on [the State and County Estimate Layouts page](https://www.census.gov/programs-surveys/saipe/technical-documentation/file-layouts/state-county.html). Since this data is not in a conventional structured format, custom parsing rules were required.

Next, we conducted statistical analyses, ran linear regressions, and created maps and visualizations.

We began by determining whether a linear relationship existed. We ran several linear regressions, including the following:

- CAASPP score ~ COE size (COE level)
- CAASPP score ~ COE size + median household income (COE level)

## Data Sources

A list of schools and school metadata was obtained from [California School Directory](https://www.cde.ca.gov/SchoolDirectory/) and the [CDE export tool](https://www.cde.ca.gov/SchoolDirectory/ExportSelect?search=&allSearch=&tab=1&order=0&qdc=1520&qsc=26211&simpleSearch=Y&sax=true).

CAASPP scores were scraped from [California School Dashboard](https://www.caschooldashboard.org) using a Python script.

## Limitations

This analysis is exploratory and correlational.

Several important factors are not controlled for, including:

- race and ethnicity
- English learner status
- urbanization
- school funding
- chronic absenteeism

As a result, any observed relationship between COE size and CAASPP performance should not be interpreted as causal.

# Observations

### Regression: CAASPP score ~ COE Size

|Factor|P-value|Significant|
|-|-|
|Intercept|< 0.0001|Yes|
|COE Size|0.0109|Yes|

R² = 0.1102

n = 58

### Regression: CAASPP score ~ COE Size + Median household income

|Factor|P-value|Significant|
|-|-|
|Intercept|< 0.0001|Yes|
|COE Size|0.0585|No|
|Median household income|< 0.0001|Yes|

R² = 0.5493

n = 58

# Analysis

The initial linear regression suggests there may be some slight positive correlation between CAASPP scores and COE size. This implies that COE size, or some related factors, are related to CAASPP scores. This motivates the initial hypothesis, but does not confirm a causal relationship. However, the relation between CAASPP scores and COE size is not straightforward, so a confounder could exist.

Subsequently, the `CAASPP score ~ COE size + median household income` linear regression informed us that a significant positive correlation existed between CAASPP scores and median household income per county. However, this decreased the significance of the COE size coefficient, placing it just outside the 0.05 confidence level, and rendering it insignificant. This tells us that COE size and median household income are correlated in some way, and one may act as a confounder for the other.

# Reproducing the Analysis

Executing the analysis requires several mathematics libraries, which are as follows:
- Numpy
  - specific version required; use `pip install "numpy<2" --upgrade`
- Pandas
- SciPy
- geopy
- Matplotlib (`matplotlib`)

If you also want to execute the data scrape portion, then doing so requires scraping libraries. These are as follows:
- Beautiful Soup 4 (it may request `lxml` or `html5lib` but these are unneeded and you can safely ignore the warnings if you do not prefer to install these packages)
- Requests

Furthermore, this code is intended for Python 3.12. Newer or older versions may fail to function properly. It was tested on a MacOS machine on Apple Silicon; this should work on other systems, but compatibility with other machines can not be guaranteed.

A `requirements.txt` will be provided in the future.

# Future Work

- Control for demographic variables.
- Control for English learner status.
- Control for foster youth and homelessness.
- Incorporate urbanization and population density.
- Extend the analysis to the school level.
- Compare predictive models against simple linear regression.
- Investigate schools that substantially outperform expectations.

