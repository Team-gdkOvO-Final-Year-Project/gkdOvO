# utility
from flask import Flask, request,make_response,render_template,redirect,Response
import csv
from typing import Any, Dict, Optional
from datetime import datetime
import os
from flask.helpers import flash
from tkinter import Variable, messagebox
import pandas as pd
from pandas.core.frame import DataFrame
from pandas.plotting import  table
import matplotlib.pyplot as plt
import six
import numpy as np

#function
from pre_processing import pre_processing
from clustering import process_clustering
from classification import classification
from threshold import get_threshold
from matched_selection_kpi_prediction import MatchedShopSelection_KPIPrediction
 
app = Flask(__name__,template_folder='UI_pages')

overall_KPI = 0
def transform(text_file_contents):
    return text_file_contents.replace("=", ",")

def generate_download_headers(
        extension: str, filename: Optional[str] = None
) -> Dict[str, Any]:
    filename = filename if filename else datetime.now().strftime("%Y%m%d_%H%M%S")
    content_disp = f"attachment; filename={filename}.{extension}"
    headers = {"Content-Disposition": content_disp}
    return headers

def render_mpl_table(data, col_width=3.0, row_height=0.625, font_size=14,
                     header_color='#40466e', row_colors=['#f1f1f2', 'w'], edge_color='w',
                     bbox=[0, 0, 1, 1], header_columns=0,
                     ax=None, **kwargs):
    if ax is None:
        size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
        fig, ax = plt.subplots(figsize=size)
        ax.axis('off')

    mpl_table = ax.table(cellText=data.values, bbox=bbox, colLabels=data.columns, **kwargs)

    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(font_size)

    for k, cell in  six.iteritems(mpl_table._cells):
        cell.set_edgecolor(edge_color)
        if k[0] == 0 or k[1] < header_columns:
            cell.set_text_props(weight='bold', color='w')
            cell.set_facecolor(header_color)
        else:
            cell.set_facecolor(row_colors[k[0]%len(row_colors) ])
    return ax




@app.route('/uploader', methods=['GET','POST'])
def upload():
    #remove old preview table if exits
    # if os.path.isfile('Application/UI_pages/preview.html'):
    #     os.remove('Application/UI_pages/preview.html')
    
    #receive data from html, read csv file and convert to dataframe
    file = request.files['file']
    try:
        
        csv_data = pd.read_csv(file)
        preview_table = csv_data[0:23]    
        
        #drafting new preview.html
        with open('Application/UI_pages/preview_script.txt', 'wt') as f:
            # read_data = f.read()
            # f.seek(0)
            f.truncate()   #清空文件
            # # f.write(read_data.replace(preview_table.to_html()))
            f.writelines(preview_table.to_html())
        content = []
        with open('Application/UI_pages/preview_head.txt') as f:
            lines = f.readlines()
            for i in lines: 
                content.append(i)
        with open('Application/UI_pages/preview_script.txt') as f:
            lines = f.readlines()
            for l in lines: 
                content.append(l)
        with open('Application/UI_pages/preview_tail.txt') as f:
            lines = f.readlines()
            for l in lines: 
                content.append(l)

        with open('Application/UI_pages/preview.txt', 'a') as f:
            f.writelines('\n'.join(content))
        if os.path.isfile('Application/UI_pages/preview.html'):
            os.remove('Application/UI_pages/preview.html')

        os.rename('Application/UI_pages/preview.txt','Application/UI_pages/preview.html')
        # os.replace('preview_script.html','/Application/UI_pages/preview_script.html')
        return ('Please click Preview button')
        
    except:
        return ("no data")

# Receive data for analysis page, call functions from other py file for machine learning models
@app.route('/analysis', methods=['GET','POST'])
def analyse():
    #add path prefix for saving image
    url_prefix='Application/image/'

    #receive data from html, read csv file and convert to dataframe
    file = request.files['file2']
    try:
        csv_data = pd.read_csv(file)
        ###### Pre-processing ######
        #For normal case
        # whitelist_filled, non_whitelist_filled=pre_processing(url_prefix,csv_data)

        #For demo - import filled dataset
        non_whitelist_filled=csv_data[csv_data['decorated_indicator']==0]
        whitelist_filled=csv_data[csv_data['decorated_indicator']==1]
        non_whitelist_filled = non_whitelist_filled.drop(columns=['Unnamed: 0'])
        whitelist_filled = whitelist_filled.drop(columns=['Unnamed: 0'])

        ###### Clustering ######
        labelled_whitelist=process_clustering(whitelist_filled,url_prefix)

        ###### Classification ######
        matched_shops, unmatched_shops = classification(labelled_whitelist,non_whitelist_filled)

        ###### Prediction ######
        #unmatched cases
        unmatched_selected_shop=get_threshold(unmatched_shops, whitelist_filled)

        #matched cases
        global overall_KPI
        global selected_matched_data

        selected_matched_data , overall_KPI=MatchedShopSelection_KPIPrediction(matched_shops,unmatched_selected_shop,whitelist_filled,url_prefix)
        KPI = {'Estimated Number of Orders':int(overall_KPI)}
        KPI = pd.DataFrame(KPI,index = [0])

        kpi_png = render_mpl_table(KPI, header_columns=0, col_width=8.0)
        kpi_png.get_figure().savefig(url_prefix+'KPI.png')


        return ('Analysis result is successfully generated, please go back to analysis page')#render_template("charts.html")
    except:
        return ("no data")
        

@app.route('/preview')
def preview():    
    return render_template('preview.html')

@app.route('/remover',methods=['GET','POST'] )
def remove():
    content = []
    with open("Application/UI_pages/no_data.txt") as f:
        lines = f.readlines()
        for l in lines: 
            content.append(l)
    with open("Application/UI_pages/preview.html",'a') as f:
        f.truncate(0)
        f.writelines('\n'.join(content))
    return ('File is removed, please go back to preview page.')


@app.route('/export',methods=['GET','POST'])
def export():
    kpi = overall_KPI
    shops = selected_matched_data

    csv_bin_data = shops.to_csv(index=False, encoding="utf-8")  # 生成csv二进制流

    return Response(
        csv_bin_data,
        status=200,
        headers=generate_download_headers("csv"),
        mimetype="application/csv",
    )


if __name__ == '__main__':
    app.run(port=5000, debug=True)
    
