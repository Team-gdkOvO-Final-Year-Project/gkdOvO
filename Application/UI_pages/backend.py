from flask import Flask, request,make_response,render_template,redirect
import csv
import io
import os
import pandas as pd
 
app = Flask(__name__)


def transform(text_file_contents):
    return text_file_contents.replace("=", ",")



@app.route('/uploader', methods=['GET','POST'])
def upload():
    #remove old preview table if exits
    if os.path.isfile('Application/UI_pages/preview.html'):
        os.remove('Application/UI_pages/preview.html')
    
    #receive data from html, read csv file and convert to dataframe
    file = request.files['file']
    csv_data = pd.read_csv(file)
    preview_table = csv_data[0:23]    
    
    #drafting new preview.html
    with open('Application/UI_pages/preview_script.txt', 'wt') as f:
        # read_data = f.read()
        # f.seek(0)
        # f.truncate()   #清空文件
        # # f.write(read_data.replace(preview_table.to_html()))
        f.writelines(preview_table.to_html())
    content = []
    with open('Application/templates/preview_head.txt') as f:
        lines = f.readlines()
        for i in lines: 
            content.append(i)
    with open('Application/templates/preview_script.txt') as f:
        lines = f.readlines()
        for l in lines: 
            content.append(l)
    with open('Application/templates/preview_tail.txt') as f:
        lines = f.readlines()
        for l in lines: 
            content.append(l)

    with open('Application/templates/preview.txt', 'a') as f:
        f.writelines('\n'.join(content))
    os.rename('Application/templates/preview.txt','Application/templates/preview.html')
    # os.replace('preview_script.html','/Application/UI_pages/preview_script.html')
    return redirect('/preview')
    # return('ok')

@app.route('/preview')
def preview():    
    return render_template('Application/templates/preview.html')

 
if __name__ == '__main__':
    app.run(port=5000, debug=True)
