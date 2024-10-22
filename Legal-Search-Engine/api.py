import flask
import re
from flask import request, jsonify
from test_queries import *
from netapp_test2 import *
from mySummarizer import *
from finaldetails import *
from flask import Flask, send_file, render_template
	
app = flask.Flask(__name__)
app.config["DEBUG"] = True


class DataStore():
    det=[]
data=DataStore()


@app.route('/advSearch', methods=['GET'])
def api_search1():
    return render_template("advSearch.html")


@app.route('/about', methods=['GET'])
def api_about():
    return render_template("about.html")


@app.route('/', methods=['GET'])
def api_home():
    return render_template('home.html')


@app.route('/askquery', methods=['GET'])
def api_query():
   text1=""
   text2=""
   if 'query' in request.args:
       ret=test_query(request.args['query'])
       fin=[]
       flag=0
       if 'date' in request.args:
           for i in ret:
               match=re.search(r'\d+', i)
               name=match.group()
               if (retrieve_firstdate(name)==request.args['date']):
                   fin.append(i)
           if(request.args['date']):
               flag=1
       if 'appeal_no' in request.args:
           for i in ret:
               match=re.search(r'\d+', i)
               name=match.group()
               appellate_jurisdiction, appeal_num=retrieve_AppellateJurisdiction(name)
               if (appeal_num==request.args['appeal_no']):
                   fin.append(i)
           if(request.args['appeal_no']):
               flag=1
       if 'appellate' in request.args:
           ret1=request.args['appellate']
           ret1=ret1.lower()
           for i in ret:
               match=re.search(r'\d+', i)
               name=match.group()
               appellate_jurisdiction, appeal_num=retrieve_AppellateJurisdiction(name)
               if(appellate_jurisdiction):
                   if (appellate_jurisdiction.lower()==ret1):
                       fin.append(i)
           if(request.args['appellate']):
               flag=1
       if 'case-type' in request.args:
           ret1=request.args['case-type']
           ret1=ret1.lower()
           for i in ret:
                match=re.search(r'\d+', i)
                name=match.group()
                ctype = retrieve_case_type(name)
                if(appellate_jurisdiction):
                    if (appellate_jurisdiction.lower()==ret1):
                        fin.append(i)
           if(request.args['case-type']):
                flag=1
       if flag!=1:
           fin=ret
       if len(fin)==0:
           text1= "No relevant document found."
   else:
       text2= "Error: No query provided. Please specify query."
   cleanlist=[]
   [cleanlist.append(x) for x in fin if x not in cleanlist]   
   fin=cleanlist 

   det2=[]
   count_file=1
   for filename in fin:
       if (re.search(r'\d+', filename)):
           det2.append(getdetails(filename,count_file))
           count_file+=1
           
   while(len(det2)<10):
       det2.append(("","","","","","",""))
   data.det=det2
   return render_template("searchResults.html",text1=text1,text2=text2,det=det2)


@app.route('/docwise')
def api_docwise():
    try:
        if 'document' in request.args:
                ret=retrieve_finalJudgement((request.args.get('document', 0, type=str)).zfill(4))
                if ret is None:
                    return jsonify(result="Error: Could not retrieve data for the specified document.")
        else:
            return jsonify(result="Error: No document number provided. Please specify.")
        return jsonify(result=ret)
    except Exception as e:
        return str(e)  
    
    
@app.route('/docwise2')
def api_docwise2():
    try:
        if 'document' in request.args:
                pc=retrieve_penalCodes((request.args.get('document', 0, type=str)).zfill(4))
                ret=[]
                if pc is None:
                    return jsonify(result="Error: Could not retrieve data for the specified document.")
                for ipc, codename in pc:
                    ret.append(" "+codename+" "+ipc)
                if len(ret) == 0:
                    return jsonify(result="There are no Penal Codes in this document.")
                
        else:
            return jsonify(result="Error: No document number provided. Please specify.")
        if len(ret) == 0:
            return jsonify(result="There are no Penal Codes in this document.")
        return jsonify(result=ret)
    except Exception as e:
        return str(e)  
    
    
@app.route('/docwise3')
def api_docwise3():
    try:
        if 'document' in request.args:
            ret=retrieve_firstdate((request.args.get('document', 0, type=str)).zfill(4))
            if ret is None:
                return jsonify(result="Error: Could not retrieve data for the specified document.")
        else:
            return jsonify(result="Error: No document number provided. Please specify.")
        return jsonify(result=ret)
    except Exception as e:
        return str(e)  
    
    
@app.route('/docwise4')
def api_docwise4():
    try:
        if 'document' in request.args:
                ret=retrieve_AppellateJurisdiction((request.args.get('document', 0, type=str)).zfill(4))
                if ret[0] is None:
                    return jsonify(result="This document does not contain an appellate jurisdiction.")
        else:
            return jsonify(result="Error: No document number provided. Please specify.")
        return jsonify(result=ret)
    except Exception as e:
        return str(e)  


@app.route('/download')
def download_file():
  if 'doc' in request.args:
    fileno=request.args['doc'].zfill(4)
    path = "Prior_Cases/prior_case_"+fileno+'.txt'
  else:
    return "Enter document name."
  return send_file(path, as_attachment=True)


@app.route('/download1')
def download1_file():
    if 'doc' in request.args:
        if request.args['doc'] == "det00":
            filename=data.det[0][5]
        elif request.args['doc'] == "det10":
            filename=data.det[1][5]
        elif request.args['doc'] == "det20":
            filename=data.det[2][5]
        elif request.args['doc'] == "det30":
            filename=data.det[3][5]
        elif request.args['doc'] == "det40":
            filename=data.det[4][5]
        elif request.args['doc'] == "det50":
            filename=data.det[5][5]
        elif request.args['doc'] == "det60":
            filename=data.det[6][5]
        elif request.args['doc'] == "det70":
            filename=data.det[7][5]
        elif request.args['doc'] == "det80":
            filename=data.det[8][5]
        elif request.args['doc'] == "det90":
            filename=data.det[9][5]
        path = "Prior_Cases/"+filename
    else:
        return "Invalid Link"
    return send_file(path, as_attachment=True)


@app.route('/background_process')
def background_process():
    try:
        if 'query' in request.args:
            ret=test_query(request.args['query'])
            fin=[]
            flag=0
            if 'date' in request.args:
                for i in ret:
                    if (retrieve_firstdate(i)==request.args['date']):
                        fin.append(i)
                        print(i)
                if(request.args['date']):
                    flag=1
            if 'appeal_no' in request.args:
                for i in ret:
                    appellate_jurisdiction, appeal_num=retrieve_AppellateJurisdiction(i)
                    if (appeal_num==request.args['appeal_no']):
                        fin.append(i)
                if(request.args['appeal_no']):
                    flag=1
            if 'appellate' in request.args:
                ret1=request.args['appellate']
                ret1=ret1.lower()
                for i in ret:
                    appellate_jurisdiction, appeal_num=retrieve_AppellateJurisdiction(i)
                    if(appellate_jurisdiction):
                        if (appellate_jurisdiction.lower()==ret1):
                            fin.append(i)
                if(request.args['appellate']):
                    flag=1
            if flag!=1:
                fin=ret
        else:
            fin.append( "Error: No query provided. Please specify query.")
        cleanlist=[]
        [cleanlist.append(x) for x in fin if x not in cleanlist]   
        fin=cleanlist 
        for i in range (len(fin),10):
            fin.append(" ")
        return jsonify(result = fin)
    except Exception as e:
        return str(e)


app.run()
