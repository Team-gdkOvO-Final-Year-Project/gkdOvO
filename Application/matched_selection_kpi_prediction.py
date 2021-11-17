import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib

import matplotlib.pyplot as plt
from pandas.plotting import table
from scipy.stats import skew
from scipy.stats.stats import pearsonr
from pandas.plotting import table


#feature selection
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import f_regression

#Prediction
from sklearn import metrics
from sklearn.metrics import r2_score
from sklearn import linear_model
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import  train_test_split
from sklearn.ensemble import RandomForestRegressor

#%config InlineBackend.figure_format = 'png' #set 'png' here when working on notebook
#%matplotlib inline




def MatchedShopSelection_KPIPrediction(raw_matched_data,selected_unmatched,whitelist_filled_latest,image_path):
    #run after unmatched shops selection

    #Preprocessing
    #raw_matched_data <-- matched_with_label
    #raw_matched_data = raw_matched_data.drop(columns=['Unnamed: 0','decorated_indicator'])
    matched_data = raw_matched_data.groupby('shop_index').sum()

    #feature selection
    raw_data_X = raw_matched_data.drop("masked_order",1)
    raw_data_y = raw_matched_data["masked_order"]


    #get matched shop features


    #apply SelectKBest class to extract top 5 best features
    bestfeatures = SelectKBest(score_func=f_regression, k=5)
    fit = bestfeatures.fit(raw_data_X,raw_data_y)
    dfscores = pd.DataFrame(fit.scores_)
    dfcolumns = pd.DataFrame(raw_data_X.columns)

    #concat two dataframes for better visualization 
    featureScores = pd.concat([dfcolumns,dfscores],axis=1)
    featureScores.columns = ['Specs','Score']  #naming the dataframe columns
    print(featureScores.nlargest(5,'Score'))  #print 5 best features


    features = featureScores.nlargest(5,'Score')
    features = features['Specs'].tolist()  
    print(features)

    #  Prediction
    #prediction on umatched data with features selected


    model1=linear_model.LinearRegression()
    #features = ['shop_L180D_order','masked_item_impression','masked_other_tab_click','shop_follower_number']

    X = matched_data[features]
    y = matched_data['masked_order']
    # print(X.shape,y.shape)

    # /////// Log Transformation Visualizations ///////
    matplotlib.rcParams['figure.figsize'] = (12.0, 6.0)
    shop_L180D_order = pd.DataFrame({"shop_L180D_order":X["shop_L180D_order"], "log(shop_L180D_order + 1)":np.log1p(X["shop_L180D_order"])})
    shop_L180D_order.hist()
    plt.savefig(image_path + 'matched_selection_log_transformationX.png')

    matplotlib.rcParams['figure.figsize'] = (12.0, 6.0)
    masked_order = pd.DataFrame({"masked_order":y, "log(masked_order + 1)":np.log1p(y)})
    masked_order.hist()
    plt.savefig(image_path + 'matched_selection_log_transformationY.png')

    #log transform the target:
    y = np.log1p(y)

    #log transform skewed numeric features:
    numeric_feats = X.dtypes[X.dtypes != "object"].index

    skewed_feats = X[numeric_feats].apply(lambda x: skew(x.dropna())) #compute skewness
    skewed_feats = skewed_feats[skewed_feats > 0.75]
    skewed_feats = skewed_feats.index

    X[skewed_feats] = np.log1p(X[skewed_feats])


    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)

    # RandomForestRegressor Model 

    RFregressor_model = RandomForestRegressor()
    RFregressor_model.fit(X_train,y_train)

    test_predicted_orders = RFregressor_model.predict(X_test)
    print(test_predicted_orders)
    print("MSE for Random Forest Regressor:",metrics.mean_squared_log_error(test_predicted_orders, y_test))
    # print(metrics.mean_squared_log_error(predicted_prices, y_test))

    #evaluation
    r2_score(y_test, test_predicted_orders)

    # Actual Prediction 
    X = raw_matched_data[features]

    predicted_orders = RFregressor_model.predict(X)
    raw_matched_data.loc[:,'predicted_orders'] = predicted_orders
    campaignday_prediction = raw_matched_data[raw_matched_data['performance_date'] == 8]

    sorted_campaignday_prediction = campaignday_prediction.sort_values(by = 'predicted_orders',ascending = False)

  
    n_percentage = 20
    top_n_per_matched_shops = sorted_campaignday_prediction.head(int(len(sorted_campaignday_prediction)*(n_percentage/100)))

    # top n distribution
    topn_dist = top_n_per_matched_shops['rf_label'].value_counts()
    # original distribution
    raw_dist = raw_matched_data['rf_label'].value_counts()

    per_pd = pd.DataFrame({'top n numbers':topn_dist,'cluster numbers':raw_dist})
    per_pd.loc[:,'percentage'] = per_pd['top n numbers'].values/per_pd['cluster numbers'].values
    topn_result_df = per_pd.sort_values(by = 'percentage',ascending = False)

    #visualization
    topn_result_df.index.name = 'cluster label'
    topn_result_df = topn_result_df.reset_index()
    col_name = topn_result_df.index.name

    fig = plt.figure(figsize=(3,4), dpi =1400)
    ax = fig.add_subplot(111,frame_on=False)
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)

    table(ax, topn_result_df, loc = 'center')
    plt.savefig(image_path + 'matched_cluster.png')


    #Output
    selected_clusters = [topn_result_df.index[0],topn_result_df.index[1]]
    selected_matched_data = pd.concat([raw_matched_data[raw_matched_data['rf_label'] == selected_clusters[0]],raw_matched_data[raw_matched_data['rf_label'] == selected_clusters[1]]])

    #selected_matched_data.to_csv('selected_matched_shops.csv', index = False)

    #KPI Prediction
    KPI_matched = campaignday_prediction['predicted_orders']
    
    
    #unmatched_data = pd.read_csv('selected_unmatch.csv')
    X_unmatched = unmatched_data[features]
    unmatched_prediction = RFregressor_model.predict(X_unmatched)
    unmatched_data.loc[:,'unmatched_prediction'] = unmatched_prediction
    unmatched_campaignday_prediction = unmatched_data[unmatched_data['performance_date'] == 8]
    KPI_unmatched = unmatched_campaignday_prediction['unmatched_prediction']
    

    #whitelisted_shops = pd.read_csv('whitelist_filled_latest.csv')
    X_whitelist = whitelisted_shops[features]
    whitelisted_prediction = RFregressor_model.predict(X_whitelist)
    whitelisted_shops.loc[:,'whitelisted_prediction'] = whitelisted_prediction
    whitelisted_campaignday_prediction = whitelisted_shops[whitelisted_shops['performance_date'] == 8]
    KPI_whitelisted = whitelisted_campaignday_prediction['whitelisted_prediction']


    overall_KPI = sum(KPI_unmatched)+sum(KPI_whitelisted)+sum(KPI_matched)


    return selected_matched_data , overall_KPI