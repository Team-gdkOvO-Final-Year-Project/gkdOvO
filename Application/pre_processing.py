#utility
import pandas as pd
import numpy as np
from numpy import mean
from numpy import std

#visualisation
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import pyplot

#pre-processing
import missingno as msno
from sklearn.impute import KNNImputer

def pre_processing(url_prefix,data):
    
    # ======= visualize missing data of all ======
    missing_fig=msno.bar(data)
    # breakpoint()
    missing_fig_copy = missing_fig.get_figure()
    missing_fig_copy.savefig(url_prefix+'preprocessing_missing_value_all.png', bbox_inches = 'tight') 

    # ======= simple fill-null ======
    data["manage_shop_indicator"].fillna(0,inplace=True)

    #convert text into numeric value
    data['decorated_indicator'] = np.where(data['decorated_indicator']== 'N', 0, 1)
    data['new_seller_flag'] = np.where(data['new_seller_flag']== 'old_seller', 0, 1)

    #encode shop category into numeric number 
    data['shop_category']=pd.factorize(data['shop_category'])[0]
    data.loc[(data.shop_category == -1),'shop_category']=len(data['shop_category'].unique())-1

    # ====== Correlation Matrix ======
    sns.set(font_scale=6)
    plt.figure(figsize=(100,50))
    corr = data.corr()
    matrix = np.triu(corr)
    corr_fig=sns.heatmap(corr, annot=True, cmap='coolwarm', mask=matrix).get_figure()
    corr_fig.savefig(url_prefix+'preprocessing_corr.png', bbox_inches = 'tight')

    #drop columns with high correlation
    data = data.drop(columns=['shop_history_order', 'masked_product_page_view'])


    # ======= Split dataset =======

    # === Whitelist ===
    whitelist = data[data['decorated_indicator'] == 1]
    non_whitelist = data[data['decorated_indicator'] == 0]

    # for variables with few missing values, drop them (as the no. of missing values is vary small)
    whitelist.dropna(subset=["weighted_shop_rating"],inplace=True)

    #K-NN null value fill-up
    imputer = KNNImputer(n_neighbors=19, weights='uniform', metric='nan_euclidean')
    imputer.fit(whitelist.iloc[:,1:])
    whitelist_filled = imputer.transform(whitelist.iloc[:,1:])

    #label the filled values with column name and add shop_id back
    whitelist_filled=pd.DataFrame(whitelist_filled,columns=list(whitelist.columns)[1:])
    whitelist_filled['shop_index']=whitelist['shop_index'].values

    #export filled whitelist data
    # whitelist_filled.to_csv('whitelist_filled.csv')

    # === Non Whitelist ===
    #fill for 3 indicator columns
    non_whitelist_test=non_whitelist.copy(deep=False)
    non_whitelist_test = non_whitelist_test.drop(columns=['masked_shop_click_from_search','masked_campaign_tab_click', 'masked_other_tab_click'])
    non_whitelist_test_shop=non_whitelist_test.groupby('shop_index').mean() #construct a shop_id >> indicator pair

    non_whitelist_test_shop["officialstore_indicator"].fillna(np.random.randint(0,1), inplace =True)
    non_whitelist_test_shop["preferred_shop_indicator"].fillna(np.random.randint(0,1), inplace =True)
    non_whitelist_test_shop["crossborder_indicator"].fillna(np.random.randint(0,1), inplace =True)

    #fill NaN according to value assigned in non_whitelist_test_shop
    for index, row in non_whitelist[non_whitelist['officialstore_indicator'].isnull()].iterrows():
        non_whitelist.loc[index,'officialstore_indicator']=non_whitelist_test_shop['officialstore_indicator'][row['shop_index']]

    for index, row in non_whitelist[non_whitelist['preferred_shop_indicator'].isnull()].iterrows():
        non_whitelist.loc[index,'preferred_shop_indicator']=non_whitelist_test_shop['preferred_shop_indicator'][row['shop_index']]

    for index, row in non_whitelist[non_whitelist['crossborder_indicator'].isnull()].iterrows():
        non_whitelist.loc[index,'crossborder_indicator']=non_whitelist_test_shop['crossborder_indicator'][row['shop_index']]

    #K-NN null value fill-up
    imputer = KNNImputer(n_neighbors=19, weights='uniform', metric='nan_euclidean')
    imputer.fit(non_whitelist.iloc[:,1:]) #exclude shop_id
    non_whitelist_filled = imputer.transform(non_whitelist.iloc[:,1:]) #result is array format

    #transform result array into df
    non_whitelist_filled=pd.DataFrame(non_whitelist_filled,columns=list(non_whitelist.columns)[1:])
    non_whitelist_filled['shop_index']=non_whitelist['shop_index'].values

    #export into csv
    # non_whitelist_filled.to_csv('non_whitelist_filled.csv')

    return whitelist_filled, non_whitelist_filled
