import pandas as pd
# 1. load text file
saipe_textrows = open("est24-ca.txt").read().split("\n")[1:]
# 2. obtain mapping
saipe_mappings = [
    ("FIPS State code",  1, 2, None),
    ("FIPS county code", 4, 6, None),

    ("Quantity population in poverty",                   8, 15, float),
    ("Quantity population in poverty (90% conf lower)", 17, 24, float),
    ("Quantity population in poverty (90% conf upper)", 26, 33, float),
    ("Percent population in poverty",                   35, 38, float),
    ("Percent population in poverty (90% conf lower)",  40, 43, float),
    ("Percent population in poverty (90% conf upper)",  45, 48, float),

    ("Quantity Population age 0-17 in poverty",                  50, 57, float),
    ("Quantity Population age 0-17 in poverty (90% conf lower)", 59, 66, float),
    ("Quantity Population age 0-17 in poverty (90% conf upper)", 68, 75, float),
    ("Percent Population age 0-17 in poverty",                   77, 80, float),
    ("Percent Population age 0-17 in poverty (90% conf lower)",  82, 85, float),
    ("Percent Population age 0-17 in poverty (90% conf upper)",  87, 90, float),

    ("Quantity Related children age 5-17 in families in poverty",                   92,  99, float),
    ("Quantity Related children age 5-17 in families in poverty (90% conf lower)", 101, 108, float),
    ("Quantity Related children age 5-17 in families in poverty (90% conf upper)", 110, 117, float),
    ("Percent Related children age 5-17 in families in poverty",                   119, 122, float),
    ("Percent Related children age 5-17 in families in poverty (90% conf lower)",  124, 127, float),
    ("Percent Related children age 5-17 in families in poverty (90% conf upper)",  129, 132, float),
    
    ("Median household income",                  134, 139, float),
    ("Median household income (90% conf lower)", 141, 146, float),
    ("Median household income (90% conf upper)", 148, 153, float),
    
    ("County name",        194, 238, None),
    ("State abbreviation", 240, 241, None),
]
# 3. actually decompose stuff
def saipe_decompose_one(text, mapping):
    x = text[mapping[1]-1:mapping[2]].strip()
    if mapping[3] == None: return x
    try:
        return mapping[3](x)
    except:
        return None
saipe_data = []
for row in saipe_textrows:
    d = []
    for mapping in saipe_mappings:
        d.append(saipe_decompose_one(row, mapping))
    saipe_data.append(d)
# 4. dataframe
saipe_df = pd.DataFrame(data = saipe_data, columns = [x[0] for x in saipe_mappings])
# 5. test
if __name__ == "__main__":
    print(saipe_df)
    print(saipe_df.columns)

