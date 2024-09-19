#highest avg bleach
#variability %s regions
#distribution depths
#% change decade
#highest % bleach

import pandas as pd
import matplotlib.pyplot as plt


def load_data(filepath):
    return pd.read_csv("Aquatic.csv")

def data_inspection(data):
    # inspection (need to know if there's missing/dup values
    # Miss uses isnull to capture missing fields and sum is for calc the amt
    print("Info:", data.info())
    print("Df Shape:", data.shape)
    print("Missing Values:", data.isnull().sum())
    print("Duplicate Values", data.duplicated().sum())
    critical_cols = ["Reef ID", "Reef Name", "Longitude Degrees", "Latitude Degrees", "Country", "Depth",
                     "Organism Code", "S1", "S2", "S3", "S4"]


#clean up
#list of  columns we need
def cleaner(data, critical_cols):
    data = data.dropna(subset=critical_cols)
    data = data.drop_duplicates()
    return data

################
#object = string, numb can be float/int64,

def standardize_data(data):
    #Standardize
    #want to merge multiple columns into Longi. I take data[longdeg] and convert to strings
    data["Longitude"] = data["Longitude Degrees"].astype(str)+ " " + data["Longitude Minutes"].astype(str)+ " " +data["Longitude Seconds"].astype(str)+ " " + data["Longitude Cardinal Direction"]

    data["Latitude"] = data["Latitude Degrees"].astype(str)+ " " + data["Latitude Minutes"].astype(str)+" " + data["Latitude Seconds"].astype(str)+" " + data["Latitude Cardinal Direction"]

    data["Depth"] = pd.to_numeric(data["Depth"], errors="coerce")
    #anytime we're missing a depth, we'll fill in with the avg depth
    data["Depth"].fillna(data["Depth"].mean(), inplace=True)


    data["Year"] = pd.to_numeric(data["Year"], errors="coerce")
    data["Year"].dropna(inplace=True)

#102.22.711E.11.48.310N,Koh Tien/Koh Thain West,102,22,42.7,E,11,48,18.6,N,Pacific,
# Thailand,Trat,Koh Chang,2008,10-Jan-08,4.5,Bleaching (% of colony),20,25,30,0,FALSE,
#the S1 s2 s3 s4 rep the amount of bleaching. Add the Ss

    def extract_bleaching(row):
        return row["S1"] + row["S2"] + row["S3"] + row["S4"]

    #apply is a method to apply a custom function to each row of a DataSet
    data["Bleaching_Percentage"] = data.apply(extract_bleaching, axis=1)

    #filling in any missing values which will be the Avg
    data["Bleaching_Percentage"].fillna(data["Bleaching_Percentage"].mean(), inplace=True)

    #excluding numbers over a 100. Bleach column, apply lambda, cap 100
    data["Bleaching_Percentage"] = data["Bleaching_Percentage"].apply(lambda x: min(x, 100))

    return data


################################

def filter_and_group(data):
    #Filter & Group

    #filtering reefs futher than 5M. So nothing less than 5
    #Bleaching over 50% over
    #years over year of 2000
    data_reef_depth = data[data["Depth"] > 5.0]
    data_high_bleaching = data[data["Bleaching_Percentage"] > 50]
    data_years = data[data["Year"] >= 2000]

    #grouping
    #grouping by country, by %. Agg to avg with standard deviation. Sory by avg in ascending order
    group_by_country = data.groupby("Country")["Bleaching_Percentage"].agg(["mean", "std"]).sort_values(by='mean', ascending=False).head(15)



    pivot = data.pivot_table(values="Bleaching_Percentage", index="Country", columns="Year", aggfunc="mean")
    #10 year span index
    pivot = pivot.loc[:,2007:2017]

    #worst coral bleaching sort. Getting avg, sort values in ascending with first 15
    top_countries = pivot.mean(axis=1).sort_index(ascending=False).head(15).index
    pivot = pivot.loc[top_countries]

    print(pivot)

    return data_high_bleaching, data_reef_depth, data_years, pivot, group_by_country
#################################


def visualization(group_by_country, data_reef_depth, pivot, data_high_bleaching):
    #Plotting


    #country with highest bleaching avg
    fig, axs = plt.subplots(2,2, figsize=(18,22))

    #group by county avg. bar graph color purple. Start at subplot 00
    group_by_country['mean'].plot(kind='bar', ax=axs[0,0], color='purple')
    axs[0, 0].set_title("Avg Bleaching by Country")
    axs[0, 0].set_ylabel("Avg Bleach")
    #standard deviation. Group by country index and avg. We want to check differences. YERR is the Y Error. FMT is format, C is color
    axs[0, 0].errorbar(group_by_country.index, group_by_country['mean'], yerr=group_by_country['std'], fmt='none', c='black', capsize=5, label="Standard Deviation")

    axs[0, 0].legend()


    # number of reefs by depth
    #grabbing datareefdpth. Astype needs to be INT. count what we have and sort them
    depth_count = data_reef_depth["Depth"].astype(int).value_counts().sort_index()
    axs[0, 1].scatter(depth_count.index, depth_count.values, color='red')
    axs[0, 1].set_title("Number of reefs by depth")
    axs[0, 1].set_xlabel("Depth")
    axs[0, 1].set_ylabel("Count")


    #Bleach % by Country decade
    #wdith of bars .8
    pivot.plot(kind='bar', ax=axs[1,0], width=0.8)
    axs[1, 0].set_title("Bleaching by Year and Country")
    axs[1, 0].set_ylabel("Bleaching Percentage")



    #Top 15  it'll be ones over 50% bleach
    #only 15, index to be Reefname. Bar graphy at 1.1
    data_high_bleaching.head(15).set_index("Reef Name")["Bleaching_Percentage"].plot(kind='bar', ax=axs[1,1])
    axs[1, 1].set_title("Top 15 Bleaching Locations")
    axs[1, 1].set_ylabel("Percentage")

    plt.tight_layout()
    plt.show()

#main is responsible for everything. LoadData returns the csv but we then store that in the term data
def main():
    data = load_data("Aquatic.csv")

    data_inspection(data)
    critical_cols = ["Reef ID", "Reef Name", "Longitude Degrees", "Latitude Degrees", "Country", "Depth",
                     "Organism Code", "S1", "S2", "S3", "S4"]
    data = cleaner(data, critical_cols)
    data = standardize_data(data)

    data_high_bleaching, data_reef_depth, data_years, pivot, group_by_country = filter_and_group(data)
    visualization(group_by_country, data_reef_depth, pivot, data_high_bleaching)

if __name__ in "__main__":
    main()