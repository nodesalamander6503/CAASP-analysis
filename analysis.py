from pathlib import Path
from typing import Optional
import time
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import geopandas as gpd
import matplotlib.pyplot as plt
import requests
from util import *
from time import sleep
from saipe import saipe_df

actions = ["load", "augment", "process"] # options: scrape,load,augment,process

big_auto_table = ""
def add_to_auto_table(data):
    global big_auto_table
    PREC = 10000 # precision
    text = "### Regression: CAASPP score ~ " + " + ".join(data["factors"]) + "\n\n"
    text += "|Factor|P-value|Significant|\n"
    text += "|-|-|\n"
    for index, factor in enumerate(["Intercept"] + data["factors"]):
        p = data["p-values"][index]
        p = ("< " + str(1/PREC)) if p < (1/PREC) else str(round(data["p-values"][index] * PREC) / PREC)
        text += "|" + factor + \
                "|" + p + \
                "|" + ("Yes" if data["p-values"][index] < 0.05 else "No") + \
                "|\n"
    text += "\n"
    text += "R² = " + str(round(data["pearson's r-square"] * PREC) / PREC) + "\n\n"
    text += "n = " + str(data["n"]) + "\n\n"
    text += "\n"
    big_auto_table += text

INPUT_PATH = Path("pubdata.tsv")
OUTPUT_PATH = Path("ca_schools_with_caaspp.csv")
FIG_DIR = Path("figures")

LIMIT: Optional[int] = None
REQUEST_DELAY_SECONDS = 0.05

COUNTY_SHP_URL = "https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_us_county_500k.zip"


def plot_caasp_county_map(df: pd.DataFrame) -> None:
    FIG_DIR.mkdir(exist_ok=True)

    # Load US county shapes, then keep California.
    counties = gpd.read_file(COUNTY_SHP_URL)
    ca_counties = counties[counties["STATEFP"] == "06"].copy()

    # County names in Census file are like "San Diego"; your data should match this usually.
    county_scores = (
        df.dropna(subset=["CAASPP_SCORE"])
        .groupby("County", as_index=False)
        .agg(
            avg_caasp=("CAASPP_SCORE", "mean"),
            n_schools=("CAASPP_SCORE", "size"),
        )
    )

    ca_counties = ca_counties.merge(
        county_scores,
        left_on="NAME",
        right_on="County",
        how="left",
    )

    # Convert school points to GeoDataFrame.
    points_df = df.dropna(subset=["CAASPP_SCORE", "Latitude", "Longitude"]).copy()
    schools_gdf = gpd.GeoDataFrame(
        points_df,
        geometry=gpd.points_from_xy(points_df["Longitude"], points_df["Latitude"]),
        crs="EPSG:4326",
    )

    # Match projection.
    schools_gdf = schools_gdf.to_crs(ca_counties.crs)

    fig, ax = plt.subplots(figsize=(9, 11))

    ca_counties.plot(
        column="avg_caasp",
        ax=ax,
        legend=True,
        cmap="viridis",
        edgecolor="black",
        linewidth=0.3,
        missing_kwds={
            "color": "lightgray",
            "label": "No data",
        },
    )

    schools_gdf.plot(
        ax=ax,
        markersize=2,
        color="orange",
        alpha=0.35,
    )

    ax.set_title("Average CAASPP Score by California County, with School Locations")
    ax.set_axis_off()

    plt.tight_layout()
    plt.savefig(FIG_DIR / "caasp_county_map_with_schools.png", dpi=250)
    plt.close()


def normalize_cds_code(value) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip().split(".")[0]
    text = "".join(ch for ch in text if ch.isdigit())
    return text.zfill(14)


def find_column(df: pd.DataFrame, candidates: list[str]) -> str:
    cols = {c.lower(): c for c in df.columns}
    for candidate in candidates:
        if candidate.lower() in cols:
            return cols[candidate.lower()]
    raise KeyError(f"Missing one of {candidates}. Available: {list(df.columns)}")


def load_active_schools(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, sep="\t", dtype=str, low_memory=False)

    status_col = find_column(df, ["StatusType", "Status Type", "Status"])
    nces_col = find_column(df, ["NCESSchool", "NCES School"])
    cds_col = find_column(df, ["CDSCode", "CDS Code"])
    county_col = find_column(df, ["County"])
    district_col = find_column(df, ["District"])
    school_col = find_column(df, ["School"])
    lat_col = find_column(df, ["Latitude"])
    lon_col = find_column(df, ["Longitude"])

    # Normalize key filter columns.
    df["_StatusTypeClean"] = df[status_col].astype(str).str.strip()
    df["_NCESSchoolClean"] = df[nces_col].astype(str).str.strip()

    # Keep only active rows.
    df = df[df["_StatusTypeClean"].eq("Active")].copy()

    # Keep only rows with an actual NCES school identifier.
    # This helps remove weird/non-school rows that may still be "Active".
    df = df[
        df["_NCESSchoolClean"].notna()
        & df["_NCESSchoolClean"].ne("")
        & df["_NCESSchoolClean"].ne("No Data")
        & df["_NCESSchoolClean"].str.lower().ne("nan")
    ].copy()

    df["CDS_CODE"] = df[cds_col].map(normalize_cds_code)

    # Keep valid 14-digit CDS codes.
    df = df[df["CDS_CODE"].str.len().eq(14)].copy()

    # Exclude district-level records. School-level CDS codes should not end in 0000000.
    df = df[~df["CDS_CODE"].str.endswith("0000000")].copy()

    # Require a real school name.
    df = df[df[school_col].notna()].copy()
    df = df[df[school_col].astype(str).str.strip().ne("")].copy()

    out = pd.DataFrame({
        "CDS_CODE": df["CDS_CODE"],
        "County": df[county_col].str.strip(),
        "District": df[district_col].str.strip(),
        "School": df[school_col].str.strip(),
        "Status": df[status_col].str.strip(),
        "NCESSchool": df[nces_col].str.strip(),
        "Latitude": pd.to_numeric(df[lat_col], errors="coerce"),
        "Longitude": pd.to_numeric(df[lon_col], errors="coerce"),
    })

    for new_col, candidates in {
        "SchoolType": ["SchoolType", "School Type", "SOCType"],
        "Street": ["Street", "StreetAbr", "MailStreet"],
        "City": ["City", "MailCity"],
        "Zip": ["Zip", "MailZip"],
    }.items():
        try:
            source_col = find_column(df, candidates)
            out[new_col] = df[source_col]
        except KeyError:
            out[new_col] = pd.NA

    return out.reset_index(drop=True)


"""
def get_caasp_score(cds_code: str) -> Optional[int]:
    # "https://www.caschooldashboard.org/reports/" + code + "/" + str(year)
    url = f"https://api.caschooldashboard.org/Reports/{cds_code}/11/SummaryCards"
    response = requests.get(url, headers = headers)
    data = response.json()
    target_obj = list([obj for obj in data if obj["indicatorId"] == 7 and "status" in obj["primary"]])
    if len(target_obj) == 0:
        print("scrape failure")
        return None
    target_obj = target_obj[-1]
    x = target_obj["primary"]["status"]
    print("caasp", x)
    return x
"""
def get_caasp_score(cds_code: str) -> Optional[float]:
    url = f"https://api.caschooldashboard.org/Reports/{cds_code}/11/SummaryCards"

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        data = response.json()

        matches = [
            obj
            for obj in data
            if obj.get("indicatorId") == 7
            and "primary" in obj
            and "status" in obj["primary"]
        ]

        if not matches:
            print("scrape failure", cds_code, end = "\r")
            return None

        score = matches[-1]["primary"]["status"]

        print("caasp", cds_code, score, end = "\r")
        return score

    except Exception as exc:
        print("scrape error", cds_code, exc, end = "\r")
        return None


def enrich_with_caasp(schools: pd.DataFrame, limit: Optional[int] = None) -> pd.DataFrame:
    rows = []
    subset = schools.head(limit).copy() if limit is not None else schools.copy()

    q = len(subset)
    for n, (_, row) in enumerate(subset.iterrows(), start=1):
        error = None
        score = None

        qd = int(n/q * 20)
        print("[" + ("#" * qd) + (" " * (20-qd)) + "]" + " " + str(qd * 5) + "%" + (" " * 10), end = "\r")

        try:
            score = get_caasp_score(row["CDS_CODE"])
        except Exception as exc:
            error = repr(exc)
            sleep(random.randint(2, 4))

        out = row.to_dict()
        out["CAASPP_SCORE"] = score
        out["CAASPP_ERROR"] = error
        rows.append(out)

        if n % 50 == 0:
            print(f"Processed {n} schools...")
            sleep(16)

    return pd.DataFrame(rows)


def plot_school_locations(df: pd.DataFrame) -> None:
    FIG_DIR.mkdir(exist_ok=True)
    plot_df = df.dropna(subset=["Latitude", "Longitude"])

    plt.figure(figsize=(7, 9))
    plt.scatter(plot_df["Longitude"], plot_df["Latitude"], s=2, alpha=0.35)
    plt.title("California Schools in Dataset")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "school_locations.png", dpi=200)
    plt.close()


def bar_avg_caasp_by_county(df: pd.DataFrame) -> pd.DataFrame:
    FIG_DIR.mkdir(exist_ok=True)

    county = (
        df.dropna(subset=["CAASPP_SCORE"])
        .groupby("County", as_index=False)
        .agg(avg_caasp=("CAASPP_SCORE", "mean"), n=("CAASPP_SCORE", "size"))
        .sort_values("avg_caasp", ascending=False)
    )

    plt.figure(figsize=(9, 12))
    plt.barh(county["County"], county["avg_caasp"])
    plt.gca().invert_yaxis()
    plt.title("Average CAASPP Score by County")
    plt.xlabel("Average CAASPP score")
    plt.ylabel("County")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "avg_caasp_by_county.png", dpi=200)
    plt.close()

    return county


def bar_avg_caasp_by_district(df: pd.DataFrame, min_schools: int = 2, top_n: int = 40) -> pd.DataFrame:
    FIG_DIR.mkdir(exist_ok=True)

    district = (
        df.dropna(subset=["CAASPP_SCORE"])
        .groupby(["County", "District"], as_index=False)
        .agg(avg_caasp=("CAASPP_SCORE", "mean"), n=("CAASPP_SCORE", "size"))
    )

    district = district[district["n"] >= min_schools].sort_values("avg_caasp", ascending=False)

    plot_df = district.head(top_n).copy()
    plot_df["Label"] = plot_df["District"] + " (" + plot_df["County"] + ")"

    plt.figure(figsize=(10, 12))
    plt.barh(plot_df["Label"], plot_df["avg_caasp"])
    plt.gca().invert_yaxis()
    plt.title(f"Top {top_n} Districts by Average CAASPP Score")
    plt.xlabel("Average CAASPP score")
    plt.ylabel("District")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "avg_caasp_by_district_top.png", dpi=200)
    plt.close()

    return district


def chi_square_independence_location_score(
    df: pd.DataFrame,
    lat_bins: int = 4,
    lon_bins: int = 4,
):
    test_df = df.dropna(subset=["CAASPP_SCORE", "Latitude", "Longitude"]).copy()

    test_df["LatBin"] = pd.qcut(test_df["Latitude"], q=lat_bins, duplicates="drop")
    test_df["LonBin"] = pd.qcut(test_df["Longitude"], q=lon_bins, duplicates="drop")
    test_df["LocationBin"] = test_df["LatBin"].astype(str) + " | " + test_df["LonBin"].astype(str)
    test_df["ScoreCat"] = test_df["CAASPP_SCORE"].astype(int).astype(str)

    observed = pd.crosstab(test_df["LocationBin"], test_df["ScoreCat"])

    chi2, p_value, dof, expected = stats.chi2_contingency(observed)
    expected_df = pd.DataFrame(expected, index=observed.index, columns=observed.columns)

    return {
        "chi2": chi2,
        "p_value": p_value,
        "dof": dof,
        "observed": observed,
        "expected": expected_df,
    }


def ols_elements(df: pd.DataFrame, predictors: list[str]) -> pd.DataFrame:
    print("OLS ELEMENTS START: ", ", ".join(predictors))
    
    display_names = {
        "coe_size": "COE Size",
        "median_household_income": "Median household income",
        "latitude": "Latitude",
        "longitude": "Longitude",
    }

    reg_df = df.copy()
    reg_df["CAASPP_SCORE"] = pd.to_numeric(reg_df["CAASPP_SCORE"], errors="coerce")
    reg_df["median_household_income"] = pd.to_numeric(
        reg_df["median_household_income"],
        errors="coerce",
    )
    reg_df["latitude"] = pd.to_numeric(reg_df["Latitude"], errors="coerce")
    reg_df["longitude"] = pd.to_numeric(reg_df["Longitude"], errors="coerce")

    coe = (
        reg_df.groupby("County", as_index=False)
        .agg(
            avg_caasp=("CAASPP_SCORE", "mean"),
            coe_size=("School", "count"),
            n_caasp=("CAASPP_SCORE", "count"),
            median_household_income=("median_household_income", "first"),
            latitude=("latitude", "first"),
            longitude=("longitude", "first")
        )
        .dropna(subset=["avg_caasp", *predictors])
    )

    print(" - regress")

    y = coe["avg_caasp"].to_numpy(dtype=float)
    X_vars = coe[predictors].to_numpy(dtype=float)
    X = np.column_stack([np.ones(len(X_vars)), X_vars])

    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    y_hat = X @ beta
    residuals = y - y_hat

    n = len(y)
    p = X.shape[1]
    df_resid = n - p

    sse = float(np.sum(residuals ** 2))
    sigma2_hat = sse / df_resid
    cov_beta = sigma2_hat * np.linalg.pinv(X.T @ X)

    se = np.sqrt(np.diag(cov_beta))
    t_stats = beta / se
    p_values = 2 * (1 - stats.t.cdf(np.abs(t_stats), df=df_resid))

    ss_total = float(np.sum((y - y.mean()) ** 2))
    r2 = 1 - sse / ss_total

    result = pd.DataFrame({
        "term": ["Intercept"] + [display_names.get(p, p) for p in predictors],
        "estimate": beta,
        "std_error": se,
        "t_stat": t_stats,
        "p_value": p_values,
    })

    result.attrs["n"] = n
    result.attrs["df_resid"] = df_resid
    result.attrs["r2"] = r2
    result.attrs["sse"] = sse

    # fs

    file_annotation = "-".join(predictors)

    # summary statistics
    print(" - summarize")
    
    with open(FIG_DIR / ("regression-summary-" + file_annotation + ".txt"), "w") as f:
        f.write("OLS: average CAASPP score ~ " + "+".join([display_names[i] for i in predictors]) + "\n\n")
        f.write(result.to_string(index=False))
        f.write("\n\n")
        f.write(f"n = {result.attrs['n']}\n")
        f.write(f"df_resid = {result.attrs['df_resid']}\n")
        f.write(f"R^2 = {result.attrs['r2']}\n")

    print(" - big table summarize")
    add_to_auto_table({
        "factors": [display_names[i] for i in predictors],
        "mapped p-values": {
            display_names[i]: p_values[x + 1]
            for x, i in enumerate(predictors)
        },
        "p-values": p_values,
        "betas": beta,
        "t_stats": t_stats,
        "pearson's r-square": r2,
        "n": n,
    })

    # plot
    print(" - plot")

    output_path = FIG_DIR / ("regression-plot-" + file_annotation + ".png")

    x_col = predictors[-1]
    x = coe[x_col].to_numpy(dtype=float)
    y = coe["avg_caasp"].to_numpy(dtype=float)

    # scatter true county values
    plt.scatter(x, y, label = "Scattered COE average CAASPP scores")

    # line grid over x
    x_grid = np.linspace(x.min(), x.max(), 100)

    # construct design matrix for line
    line_df = pd.DataFrame()
    for pred in predictors:
        if pred == x_col:
            line_df[pred] = x_grid
        else:
            line_df[pred] = coe[pred].mean()

    X_line = np.column_stack([
        np.ones(len(line_df)),
        line_df[predictors].to_numpy(dtype=float),
    ])

    beta = result["estimate"].to_numpy(dtype=float)
    y_line = X_line @ beta

    plt.plot(x_grid, y_line, label = "Linear regression")
    plt.xlabel(x_col)
    plt.ylabel("Average CAASPP score")
    
    textbox = ["Linear regression: average CAASPP score ~ " + "+".join([display_names[i] for i in predictors])]
    if len(predictors) > 1:
        textbox.append("Hidden variables (set to their average for this plot): " + ", ".join([display_names[i] for i in predictors[-1:]]))
    textbox = '\n'.join(textbox)
    
    bbox = dict(boxstyle='square', facecolor='lavender', alpha=0.5)
    plt.text(1.1, 1, textbox, fontsize=10, bbox=bbox, verticalalignment='top')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()

    return result


def plot_coe_size_vs_caasp(df: pd.DataFrame) -> pd.DataFrame:
    FIG_DIR.mkdir(exist_ok=True)

    coe = (
        df.groupby("County", as_index=False)
        .agg(
            avg_caasp=("CAASPP_SCORE", "mean"),
            coe_size=("School", "count"),
            n_caasp=("CAASPP_SCORE", "count"),
        )
        .dropna(subset=["avg_caasp"])
    )

    x = coe["coe_size"].to_numpy(dtype=float)
    y = coe["avg_caasp"].to_numpy(dtype=float)

    slope, intercept = np.polyfit(x, y, 1)

    x_line = np.linspace(x.min(), x.max(), 200)
    y_line = slope * x_line + intercept

    plt.figure(figsize=(8, 6))

    plt.scatter(
        x,
        y,
        alpha=0.75,
        s=40,
    )

    plt.plot(
        x_line,
        y_line,
        linewidth=2,
        label=f"y = {slope:.3f}x + {intercept:.2f}",
    )

    for _, row in coe.iterrows():
        plt.annotate(
            row["County"],
            (row["coe_size"], row["avg_caasp"]),
            fontsize=6,
            alpha=0.7,
        )

    plt.title("Average CAASPP Score vs. COE Size")
    plt.xlabel("COE Size (Number of Schools)")
    plt.ylabel("Average CAASPP Score")
    plt.legend()

    plt.tight_layout()
    plt.savefig(FIG_DIR / "coe_size_vs_caasp.png", dpi=250)
    plt.close()

    return coe


def run_preliminary_stats(df: pd.DataFrame) -> None:
    df = df.copy()
    df["CAASPP_SCORE"] = pd.to_numeric(df["CAASPP_SCORE"], errors="coerce")
    print(df.describe())
    
    FIG_DIR.mkdir(exist_ok=True)

    plot_school_locations(df)

    county = bar_avg_caasp_by_county(df)
    county.to_csv(FIG_DIR / "avg_caasp_by_county.csv", index=False)

    district = bar_avg_caasp_by_district(df)
    district.to_csv(FIG_DIR / "avg_caasp_by_district.csv", index=False)

    #reg = ols_lat_lon_caasp(df)
    #reg.to_csv(FIG_DIR / "lat_lon_regression.csv", index=False)
    #
    #with open(FIG_DIR / "lat_lon_regression_summary.txt", "w") as f:
    #    f.write("OLS: CAASPP_SCORE ~ Latitude + Longitude\n\n")
    #    f.write(reg.to_string(index=False))
    #    f.write("\n\n")
    #    f.write(f"n = {reg.attrs['n']}\n")
    #    f.write(f"df_resid = {reg.attrs['df_resid']}\n")
    #    f.write(f"SSE = {reg.attrs['sse']}\n")
    #    f.write(f"R^2 = {reg.attrs['r2']}\n")

    ols_elements(df, ["latitude", "longitude"])

    chi = chi_square_independence_location_score(df)
    chi["observed"].to_csv(FIG_DIR / "chi_square_observed.csv")
    chi["expected"].to_csv(FIG_DIR / "chi_square_expected.csv")

    plot_caasp_county_map(df)

    with open(FIG_DIR / "chi_square_location_score_summary.txt", "w") as f:
        f.write("Chi-square test: binned location vs CAASPP score\n\n")
        f.write(f"chi2 = {chi['chi2']}\n")
        f.write(f"p_value = {chi['p_value']}\n")
        f.write(f"dof = {chi['dof']}\n")
    
    #coe_reg = ols_coe_size_caasp(df)
    #coe_reg.to_csv(FIG_DIR / "coe_size_regression.csv", index=False)
    #
    #with open(FIG_DIR / "coe_size_regression_summary.txt", "w") as f:
    #    f.write("OLS: average CAASPP score ~ COE size\n\n")
    #    f.write(coe_reg.to_string(index=False))
    #    f.write("\n\n")
    #    f.write(f"n = {coe_reg.attrs['n']}\n")
    #    f.write(f"df_resid = {coe_reg.attrs['df_resid']}\n")
    #    f.write(f"R^2 = {coe_reg.attrs['r2']}\n")
    #
    #coe_summary = plot_coe_size_vs_caasp(df)
    #coe_summary.to_csv(FIG_DIR / "coe_summary.csv", index=False)

    ols_elements(df, ["coe_size"])

    #coe_income_reg = ols_coe_size_income_caasp(df)
    #coe_income_reg.to_csv(FIG_DIR / "coe_size_income_regression.csv", index=False)
    #
    #with open(FIG_DIR / "coe_size_income_regression_summary.txt", "w") as f:
    #    f.write("OLS: average CAASPP score ~ COE size + median household income\n\n")
    #    f.write(coe_income_reg.to_string(index=False))
    #    f.write("\n\n")
    #    f.write(f"n = {coe_income_reg.attrs['n']}\n")
    #    f.write(f"df_resid = {coe_income_reg.attrs['df_resid']}\n")
    #    f.write(f"SSE = {coe_income_reg.attrs['sse']}\n")
    #    f.write(f"R^2 = {coe_income_reg.attrs['r2']}\n")

    ols_elements(df, ["coe_size", "median_household_income"])

    with open(FIG_DIR / "big_summary_table.txt", "w") as f:
        f.write(big_auto_table)


def augment(df):
    if True: # SAIPE data
        income_by_county = saipe_df[["County name", "Median household income"]].copy()
    
        income_by_county["County"] = (
            income_by_county["County name"]
            .str.replace(" County", "", regex=False)
            .str.strip()
        )
        
        income_by_county = income_by_county[[
            "County",
            "Median household income"
        ]].rename(columns={
            "Median household income": "median_household_income"
        })
        
        df = df.merge(
            income_by_county,
            on="County",
            how="left",
            validate="many_to_one"
        )
    
        print("Missing income values:", df["median_household_income"].isna().sum())
        print(df[df["median_household_income"].isna()]["County"].unique())
    
    # One may insert further augmentations here later

    return df

def main() -> None:
    for action in actions:
        if action == "scrape":
            schools = load_active_schools(INPUT_PATH)
            print(f"Loaded {len(schools)} active school rows.")
            enriched = enrich_with_caasp(schools, limit=LIMIT)
            enriched.to_csv(OUTPUT_PATH, index=False)
            print(f"Saved {len(enriched)} rows to {OUTPUT_PATH}.")
        if action == "load":
            enriched = pd.read_csv(OUTPUT_PATH)
        if action == "augment":
            enriched = augment(enriched)
        if action == "process":
            run_preliminary_stats(enriched)
            print(f"Saved preliminary outputs to {FIG_DIR}/.")


if __name__ == "__main__":
    main()
