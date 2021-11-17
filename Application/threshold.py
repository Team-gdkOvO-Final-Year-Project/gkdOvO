#utility
import numpy as np
import pandas as pd
#model selection package
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import f_regression


def get_threshold(unmatch_data, whitelist_data):
    # unmatch_data = unmatch_data.drop(columns=['Unnamed: 0','decorated_indicator'])
    unmatch = unmatch_data[unmatch_data['performance_date']==8]
    #select k best fetures
    w_df = whitelist_data[whitelist_data['performance_date']==8]
    # w_df = w_df.drop(['Unnamed: 0','decorated_indicator'],1)
    w_df = w_df.drop(['masked_campaign_tab_click'],1)
    w_x = w_df.drop("masked_order",1)
    w_y = w_df["masked_order"]
    bestfeatures = SelectKBest(score_func=f_regression, k=5)
    fit = bestfeatures.fit(w_x,w_y)
    dfscores = pd.DataFrame(fit.scores_)
    dfcolumns = pd.DataFrame(w_x.columns)
    featureScores = pd.concat([dfcolumns,dfscores],axis=1)
    featureScores.columns = ['Specs','Score']
    
    #calculate coefficient
    feature = featureScores.nlargest(5,'Score')
    feature['Score'] = feature['Score']/(feature['Score'].sum())

    #calculate score for whitelist shops
    features = list(feature['Specs'])
    scores = list(feature['Score'])
    equation = ''
    for i in range(len(features)):
        equation  += str(scores[i]) +'*'+str(features[i])+'+'
    equation = 'Score='+ equation[:len(equation)-1]
    wf_process = w_df[features]
    wf_process = wf_process.eval(equation)
    pd.set_option('display.float_format',lambda x : '%.2f' % x)

    #get shreshold
    score = wf_process['Score']
    threshold = np.percentile(score,50)
    #calculate score for unmatched shops
    unmatch.set_index(["shop_index"], inplace=True)
    un_data_process = unmatch[features]
    un_data_process = un_data_process.eval(equation)
    #match threshold on unmatch shops
    select_shop = un_data_process[un_data_process['Score']>threshold]
    final = unmatch_data[unmatch_data['shop_index'].isin(select_shop.index)]
    

    return final

