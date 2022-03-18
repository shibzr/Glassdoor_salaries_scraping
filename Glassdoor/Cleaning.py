
def clean_rated_salaries_df(df):
    # 1) droping star column
    df.drop(columns=["Star"], inplace=True)
    # 2) Changing some data types
    df["Rating"] = df["Rating"].astype(np.float32)
    df["Company"] = df["Company"].astype(str)
    df["Job_Title"] = df["Job_Title"].astype(str)


    # Cleaning Min & Max range
    df[["Min Range", "Max Range"]] = df[["Min Range", "Max Range"]].replace([' ', 'K'],
                                                                                                          ['', '000'],
                                                                                                          regex=True)
    ##removing non-digit characters
    df["Min Range"] = df["Min Range"].str.extract('(\d+)', expand=False).astype(float)
    df["Max Range"] = df["Max Range"].str.extract('(\d+)', expand=False).astype(float)

    # Cleaning Annual Salary
    series = df["Annual Salary"]
    df["Annual Salary"] = [s.encode('ascii', 'ignore').strip()
                                          for s in series.str.decode('unicode_escape')]

    df["Annual Salary"] = df["Annual Salary"].str.decode("utf-8")

    ##removing non-digit characters
    # df["Annual Salary"] = df["Annual Salary"].str.extract('(\d+)', expand=False).astype(float)

    # If df["Annual Salary"] is not number it is "About": we take the minimum range as salary and we place yearly "an" in the column Yearl/Monthyly
    for r in range(0, len(df["Annual Salary"])):
        if not df["Annual Salary"][r].isdigit():
            # replace with minimum range salary
            df["Annual Salary"][r] = df["Min Range"][r]
            # fillin Yearly/Monthly with "yr"  "mo"
            if df["Annual Salary"][r] > 15000:
                df.iloc[r, 4] = "yr"
            else:
                df.iloc[r, 4] = "mo"

    # Changing annual salary to float
    df["Annual Salary"] = df["Annual Salary"].astype(float)

    # removing all non-digits characters from "Based_On Count", "How many salaries on Glassdoor"
    count_list = ["Based_On Count", "How many salaries on Glassdoor"]
    for r in count_list:
        df[r] = df[r].str.extract('(\d+)', expand=False).astype(int)

    # Cleaning "Yearly/Monthly"
    df["Yearly/Monthly"] = df["Yearly/Monthly"].apply(
        lambda x: re.sub('[^a-zA-Z]+', '', x))

    return df