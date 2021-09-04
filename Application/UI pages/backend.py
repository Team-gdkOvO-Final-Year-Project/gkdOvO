from flask import Flask, request,make_response
import csv
import io
 
app = Flask(__name__)

def transform(text_file_contents):
    return text_file_contents.replace("=", ",")



@app.route('/tables')
def hello_world():
    r = request.args.get('info')
    if r==None:
        # do something
        return ''
    return r


@app.route('/uploader', methods=['GET','POST'])
def upload():
    file = request.files['file']
    stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
    csv_input = csv.reader(stream)
    #print("file contents: ", file_contents)
    #print(type(file_contents))
    print(csv_input)
    for row in csv_input:
        print(row)

    stream.seek(0)
    result = transform(stream.read())
    #===============================
    #to be used in exporint part
    # response = make_response(result)
    # response.headers["Content-Disposition"] = "attachment; filename=result.csv"
    # return response
    return result
    
    

 
if __name__ == '__main__':
    app.run(port=5000, debug=True)
