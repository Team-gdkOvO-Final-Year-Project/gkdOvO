# utility
from flask import Flask, request,make_response,render_template,redirect
import csv
from io import StringIO
import os
from flask.helpers import flash
from tkinter import messagebox
import pandas as pd

#function
from pre_processing import pre_processing
from clustering import process_clustering
from classification import classification
from threshold import get_threshold
from matched_selection_kpi_prediction import MatchedShopSelection_KPIPrediction
 
app = Flask(__name__,template_folder='UI_pages')


def transform(text_file_contents):
    return text_file_contents.replace("=", ",")


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
    return ('ok')


@app.route('/export',methods=['GET','POST'])
def export():
    csvList = ['10','5']
    si = StringIO()
    cw = csv.writer(si)
    cw.writerows(csvList)
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=export.csv"
    output.headers["Content-type"] = "text/csv"
    return output

    
 
if __name__ == '__main__':
    app.run(port=5000, debug=True)
    
