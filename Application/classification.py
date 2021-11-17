#utility
import numpy as np
import pandas as pd
import copy
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
#dot
import matplotlib.pyplot as plt
import seaborn as sns
# %matplotlib inline

def classification(clustered_data,non_whitelist_data):
    #===========train random forest model=============
    
    x = clustered_data.iloc[:,:11]
    y = clustered_data.iloc[:,-1]
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=2018)

    # Create the model with 100 trees

    rf_model = RandomForestClassifier(n_estimators=100, bootstrap = True, max_features = 'sqrt')

    # Fit on training data
    rf_model.fit(x_train, y_train)

    # Actual class predictions
    # rf_predictions = rf_model.predict(x_test)

    # Probabilities for each class
    # rf_probs =rf_model.predict_proba(x_test)[:, 1]

    #prediction on non_whitelist data
    # predictions = rf_model.predict(non_whitelist_data[:,:11])
    # proba = rf_model.predict_proba(non_whitelist_data)

    #add in some visualization if needed
    #add in prediction results for non-whitelistdata
    
    X = copy.deepcopy(non_whitelist_data)
    X = X.groupby("shop_index").mean()
    
    X = X.drop(columns=['decorated_indicator','performance_date','masked_item_impression','masked_order','masked_shop_page_view','masked_shop_click_from_search','masked_campaign_tab_click','masked_other_tab_click'])
    rf_labels = rf_model.predict(X)
    rf_probs = rf_model.predict_proba(X)
    rf_prob = [np.max(i) for i in rf_probs]

    X.loc[:,'rf_label'] = rf_labels
    X.loc[:,'rf_probs'] = rf_prob

    #seperate results to match and unmatched data
    matched_shops = X[X['rf_probs']>0.7]
    matched_shops['shop_index']=matched_shops.index
    unmatched_shops = X[X['rf_probs']<=0.7]
    unmatched_shops['shop_index']=unmatched_shops.index

    match_df = matched_shops['rf_label']
    match = non_whitelist_data[non_whitelist_data['shop_index'].isin(list(matched_shops['shop_index']))]
    unmatch_result = non_whitelist_data[non_whitelist_data['shop_index'].isin(unmatched_shops['shop_index'])]
    match_result = pd.merge(match,match_df,on=['shop_index'])
    #output matched dataset, unmatched dataset
    return match_result, unmatch_result

