import pandas as pd
import numpy as np


inflation_data = pd.read_csv("../data/inflation_data.csv",index_col="year")
dollars2022 = inflation_data.loc[2022, "amount"]

def convert_to_2022_dollars(year, amount):
    conversion_rate = dollars2022 / inflation_data.loc[year, "amount"]
    return conversion_rate * amount


def get_tract_spending(tracts_df, projects_df):
    totals = projects_df.pivot_table(index="GEO_ID", values=["APPROVED AMOUNT 2022"], aggfunc=["sum"])
    new_df = tracts_df.merge(totals, on="GEO_ID", how="left")
    new_df.rename(inplace=True, columns={('sum', 'APPROVED AMOUNT 2022'): "TOTAL_SPENT"})
    new_df['TOTAL_SPENT'].fillna(0, inplace=True)
    return new_df


def add_overlapping_tif(df, tif, year):
    end_year =  year + 10
    tifapprv = tif.loc[(tif["APPROVAL_YEAR"] >= year)&(tif['APPROVAL_YEAR'] < end_year)]
    tifcurrent = tif.loc[(tif['APPROVAL_YEAR'] < end_year) & (tif['EXPIRATION_YEAR'] > end_year)]
    tifapprv = tifapprv.sjoin(df)
    tifcurrent = tifcurrent.sjoin(df)
    tifapprv = tifapprv.pivot_table(index="GEO_ID", values=["NAME"], aggfunc=[lambda x : ";".join(x)])
    tifcurrent = tifcurrent.pivot_table(index="GEO_ID", values=["NAME"], aggfunc=[lambda x : ";".join(x)])
    tifapprv = tifapprv.droplevel(0, axis=1)
    tifcurrent = tifcurrent.droplevel(0, axis=1)
    tifapprv.rename(inplace=True, columns={"NAME": "APPROVED_TIFS"})
    tifcurrent.rename(inplace=True, columns={"NAME": "ALL_TIFS"})
    df = df.merge(tifapprv, how="left", on="GEO_ID")
    df = df.merge(tifcurrent, how="left", on="GEO_ID")
    df['IN_TIF_DISTRICT'] = df['ALL_TIFS'].notnull()
    df['IN_NEW_TIF_DISTRICT'] = df['APPROVED_TIFS'].notnull()
    return df


def get_thirds(df):
    bottom = df['WHITE_PROPORTION'].quantile(0.33)
    top = df['WHITE_PROPORTION'].quantile(0.67)

    df['WHITE_PROPORTION_THIRD'] = np.where(df['WHITE_PROPORTION'] >= top, "Top Third",\
                                              np.where(df['WHITE_PROPORTION'] >= bottom,\
                                                       "Middle Third", "Bottom Third"))
