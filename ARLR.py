import pandas as pd
import os
from mlxtend.frequent_patterns import apriori, association_rules
pd.set_option("display.max_columns",None)
pd.set_option("display.width",500)

############################DATA PREPARATION############################
file_path=os.getcwd()
df_ =pd.read_excel(file_path+"\\source_file\\online_retail_II.xlsx",sheet_name="Year 2010-2011",engine='openpyxl')
df = df_.copy()

def outlier(df,col):
    quartile1 = df[col].quantile(0.01)
    quartile3 = df[col].quantile(0.99)
    IQR = quartile3 - quartile1
    low_limit = df[col] - 1.5 * IQR
    high_limit =df[col] + 1.5 * IQR
    return low_limit,high_limit

def replace_with_thresholds(df,col):
    low_limit, high_limit = outlier(df,col)
    df.loc[df[col]<low_limit,col]=low_limit
    df.loc[df[col] >high_limit,col ] = high_limit

def retail_data_prep(df):
    df.dropna(inplace=True)
    df=df[~df["Invoice"].str.contains("C",na=False)]
    df = df[~df["Invoice"].str.contains("POST", na=False)]
    df = df[(df["Quantity"] > 0) & (df["Price"] > 0)]
    replace_with_thresholds(df,"Quantity")
    replace_with_thresholds(df, "Price")
    return df
df =retail_data_prep(df)
df.head()
df.shape

############################COUNTRY SELECTION############################
country_name =input("Please enter a country name : ").capitalize()
df_country = df[df["Country"]==country_name]

############################FLAGGING PROCESS############################
def pivot_flag(df,index,col,values):
    return df.pivot_table(index=index,columns=col,values=values).fillna(0).applymap(lambda x: 1 if x > 0 else 0)

def create_invoice_product_df(df,id =False):
    if id:
        return pivot_flag(df,"Invoice","StockCode","Quantity")
    else:
        return pivot_flag(df, "Invoice", "Description", "Quantity")
#create_invoice_product_df(df,id =False)[create_invoice_product_df(df,id =False).index==541877].iloc[:50,:5]
country_inv_pro_df = create_invoice_product_df(df_country,id=True)
#country_inv_pro_df.iloc[:50,:5]


############################PRODUCT_NAME############################
def check_id(df, stock_code):
    product_name = df[df["StockCode"] == stock_code][["Description"]].values[0].tolist()
    print(product_name)
# stock_code =[21987,23235,22747]
stock_code = int(input("Please, enter a stockcode"))
check_id(df_country,stock_code)


def create_rules(df):
    frequent_itemsets = apriori(df, min_support=0.01, use_colnames=True)
    rules = association_rules(frequent_itemsets, metric="support", min_threshold=0.01)
    return rules
rules = create_rules(country_inv_pro_df)

############################PRODUCT RECOMMENDATION############################
def arl_recommender(rules_df, product_id, rec_count=1):
    sorted_rules = rules_df.sort_values("lift", ascending=False)
    recommendation_list = []
    for i, product in sorted_rules["antecedents"].items():
        for j in list(product):
            if j == product_id:
                recommendation_list.append(list(sorted_rules.iloc[i]["consequents"]))
    recommendation_list = list({item for item_list in recommendation_list for item in item_list})
    return recommendation_list[:rec_count]
#21577
product_code = int(input("Please, enter a product code"))
arl_recommender(rules, product_code, 2)

############################PRODUCT RECOMMENDATION NAME############################
for i in arl_recommender(rules, product_code, 2):
    check_id(df_country, i)