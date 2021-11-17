# Packages
import copy
import pandas as pd
import numpy as np
import scipy.cluster.hierarchy as sch
import matplotlib.pyplot as plt
import plotly as py
import plotly.graph_objs as go

# Models
from sklearn.cluster import KMeans


#Metrics
from sklearn import metrics
from scipy.cluster import hierarchy 
from scipy.spatial import distance_matrix 
from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import MeanShift, estimate_bandwidth

#data = pd.read_csv('whitelist_filled_latest.csv')

def process_clustering(data,image_path):
    
    data = data.drop(columns=['decorated_indicator','masked_item_impression','masked_shop_page_view',
                         'masked_shop_click_from_search','masked_campaign_tab_click','masked_other_tab_click','masked_order','performance_date'])
    X = data.groupby('shop_index').mean()
    
    # K Means

    clusters = []
    for i in range(1, 25):
        kmeans = KMeans(n_clusters = i, init = 'k-means++', max_iter = 300, n_init = 10, random_state = 0)
        kmeans.fit(X)
        clusters.append(kmeans.inertia_)
    
    plt.plot(range(1, 25), clusters)
    plt.title('The Elbow Method')
    plt.xlabel('Number of clusters')
    plt.ylabel('clusters')
    plt.savefig(image_path+'clustering_kmeans.png')
    #plt.show()

    kmeans = KMeans(n_clusters=5, random_state=0) 
    kmeans.fit(X)

    # - labels & matrics
    kmeans_labels = kmeans.labels_
    # kmean_score = metrics.silhouette_score(X, kmeans_labels, metric='euclidean')

    # AgglomerativeClustering
    # - complete
    # dist = distance_matrix(X, X)
    # Z = hierarchy.linkage(dist, 'complete')
    # plt.figure(figsize=(30, 10))
    # dendro = hierarchy.dendrogram(Z, leaf_rotation=0, leaf_font_size=12)
    # plt.axhline(y=0.2, color='r', linestyle='--')
    # plt.savefig(image_path+'clustering_agglo_complete.png')

    # # - ward
    # plt.figure(figsize=(30, 10))
    # plt.axhline(y=0.2, color='r', linestyle='--')
    # dendrogram = sch.dendrogram(sch.linkage(X, method = 'ward'))
    # plt.title('Dendrogram')
    # plt.xlabel('Shops')
    # plt.ylabel('Euclidean distances')
    # plt.savefig(image_path+'clustering_agglo_ward.png')

    # # Using the dendrogram to find the optimal number of clusters
    # plt.figure(figsize=(30, 10))
    # dendrogram = sch.dendrogram(sch.linkage(X, method = 'average'))
    # plt.axhline(y=0.2, color='r', linestyle='--')
    # plt.title('Dendrogram')
    # plt.xlabel('Shops')
    # plt.ylabel('Euclidean distances')
    # plt.savefig(image_path+'clustering_agglo_average.png')


    # # Using the dendrogram to find the optimal number of clusters
    # plt.figure(figsize=(30, 10))
    # dendrogram = sch.dendrogram(sch.linkage(X, method = 'single'))
    # plt.axhline(y=0.2, color='r', linestyle='--')
    # plt.title('Dendrogram')
    # plt.xlabel('Shops')
    # plt.ylabel('Euclidean distances')
    # dendrogram.savefig(image_path+'clustering_agglo_single.png')

    # - score
    # cluster_complete = AgglomerativeClustering(n_clusters=5, affinity='cosine', linkage='complete')  
    # cluster_complete_labels = cluster_complete.fit_predict(X)

    # complete_score = metrics.silhouette_score(X, cluster_complete_labels, metric='cosine')

    # cluster_ward = AgglomerativeClustering(n_clusters=5, affinity='euclidean', linkage='ward')  
    # cluster_ward_labels = cluster_ward.fit_predict(X)

    # ward_score = metrics.silhouette_score(X, cluster_ward_labels, metric='euclidean')

    # cluster_single = AgglomerativeClustering(n_clusters=4, affinity='cosine', linkage='single')  
    # cluster_single_labels = cluster_single.fit_predict(X)


    # single_score = metrics.silhouette_score(X, cluster_single_labels, metric='cosine')

    cluster_averagelink = AgglomerativeClustering(n_clusters = 5, affinity = 'cosine', linkage ='average')
    cluster_average_labels = cluster_averagelink.fit_predict(X)


    # cluster_average_labels = metrics.silhouette_score(X, cluster_averagelink, metric='cosine')


    # Mean Shift Clustering
    # bandwidth = estimate_bandwidth(X.values, quantile=0.4, n_samples=1000)

    # shop_meanshift = MeanShift(bandwidth=bandwidth)
    # shop_meanshift.fit(X.values)

    # meanshift_labels = shop_meanshift.labels_
    # labels_unique = np.unique(meanshift_labels)
    # n_clusters_ = len(labels_unique)

    # print('Estimated number of clusters: ' + str(n_clusters_))
    # meanshift_score = metrics.silhouette_score(X.values, meanshift_labels, metric='euclidean')

    # LABELS
    X2 = copy.deepcopy(X)

    # breakpoint()
    # X2.loc[:,'kmeans.labels'] = kmeans_labels
    X2.loc[:,'agglomerative.average.labels'] = cluster_average_labels
    # X2.loc[:,'agglomerative.complete.labels'] = cluster_complete_labels
    # X2.loc[:,'agglomerative.single.labels'] = cluster_single_labels
    # X2.loc[:,'agglomerative.ward.labels']= cluster_ward_labels
    # X2.loc[:,'meanshift.labels'] = meanshift_labels

    
    return X2
