from email.errors import InvalidMultipartContentTransferEncodingDefect
import json
from msilib.schema import Error
from urllib.robotparser import RequestRate
from flask_restful import reqparse, Api, Resource , request
from flaskext.mysql import MySQL
from flask_cors import CORS, cross_origin
from flask import Flask, jsonify, render_template, request, send_file, make_response, abort, session
# from plots_code import barchart_diseases
import pymysql
from pymysql import Error
import logging

app = Flask(__name__)
MySql = MySQL()
cors = CORS(app)
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'mydb'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
MySql.init_app(app)

# Sevrer script with two API endpoints (Upload and Fetch) that only accept http or https POST requests
@app.route('/add', methods=['POST']) #/add end point that can only be call via POST request
def add_article():
    #get data from the Client side through API and put data to the database
    json = request.json
    #print(json)
    pmid = json['pmid']
    pm_link = json['pm_link']
    date_pub = json['date_pub']
    journal = json['journal']
    abstract = json['abstract']
    title = json['title']
    mesh = json['mesh']
    concept_id_1 = json['concept_id_1']
    concept_name = json['concept_name']
    study_design = json['study_design']
    data_type = json['data_type']
    domain_id = json['domain_id']
    category_name = json['category_name']

    if pmid and pm_link and date_pub and journal and abstract and title and mesh and concept_id_1 and concept_name and study_design and data_type and domain_id and category_name and request.method == 'POST':
        SQL_Query = "INSERT INTO tb_articles(pmid, pm_link, date_pub,journal,abstract,title,mesh,concept_id_1,concept_name,study_design,data_type,domain_id,category_name) VALUES(%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        data = (pmid, pm_link, date_pub, journal, abstract, title, mesh, concept_id_1, concept_name, study_design, data_type,domain_id,category_name)
        connection =MySql.connect()
        Pointer = connection.cursor()
        Pointer.execute(SQL_Query, data)
        connection.commit()
        response = jsonify('Article Added!')
        response.status_code = 200 #if data addedd successfully: response 200

        return response
    else:
        return "err" # if error: response 500


@app.route('/fetch',methods=['POST'])  #Method to fetch / search data from the database
def fetch_article():
    json = request.json
    start = json['start']
    end = json['end']

    if (start and end and request.method == 'POST'):
        connection =MySql.connect()
        Pointer = connection.cursor(pymysql.cursors.DictCursor)
        Pointer.execute("select * from tb_articles limit "+str(start)+" , "+str(end)+";")
        records = Pointer.fetchall()

        response = jsonify(records)
        response.status_code = 200
        return response #return all the rows from (start , end)
    else:
        return "err"


@app.route('/get_study_design',methods=['POST'])
def get_study_design():
    if (request.method == 'POST'):
        connection =MySql.connect()
        Pointer = connection.cursor(pymysql.cursors.DictCursor)
        Pointer.execute("select DISTINCT study_design FROM tb_articles")
        records = Pointer.fetchall()

        response = jsonify(records)
        response.status_code = 200
        return response #return all the rows (start , end)
    else:
        return "err"


@app.route('/get_drug_categories',methods=['POST'])
def get_drug_categories():
    if (request.method == 'POST'):
        connection =MySql.connect()
        Pointer = connection.cursor(pymysql.cursors.DictCursor)
        Pointer.execute("select DISTINCT category_name FROM tb_articles where domain_id = 'Drug'")
        records = Pointer.fetchall()

        response = jsonify(records)
        response.status_code = 200
        return response #return all the rows (start , end)
    else:
        return "err"

@app.route('/get_condition_categories',methods=['POST'])
def get_condition_categories():
    if (request.method == 'POST'):
        connection =MySql.connect()
        Pointer = connection.cursor(pymysql.cursors.DictCursor)
        Pointer.execute("select DISTINCT category_name FROM tb_articles where domain_id = 'Condition'")
        records = Pointer.fetchall()

        response = jsonify(records)
        response.status_code = 200
        return response #return all the rows (start , end)
    else:
        return "err"



@app.route('/get_data_type',methods=['POST'])
def get_data_type():
    if (request.method == 'POST'):

        connection =MySql.connect()
        Pointer = connection.cursor(pymysql.cursors.DictCursor)
        Pointer.execute("select DISTINCT data_type FROM tb_articles")
        records = Pointer.fetchall()

        response = jsonify(records)
        response.status_code = 200
        return response #return all the rows (start , end)
    else:
        return "err"


@app.route('/fetch_by_tags',methods=['POST'])  #method to fetch / search data from database
def fetch_by_tags_article():
    json = request.json
    start = json['start']
    end = json['end']
    tags = json['tags']


    tags = tags.split(',')
    if (start and end and tags  and request.method == 'POST'):
        connection =MySql.connect()
        Pointer = connection.cursor(pymysql.cursors.DictCursor)
        query_statement = ''
        if (len(tags) == 1):
            mesh_1 = tags[0]
            one_query = ''
            if (str(mesh_1).isnumeric()):
                one_query = 'concept_id_1 = "'+mesh_1+'"'
            else:
                one_query = 'mesh = "'+mesh_1+'"'
            print("mesh: "+str(mesh_1))
            Pointer.execute("select * from tb_articles where "+one_query+" limit "+str(start)+" , "+str(end)+";")
            records = Pointer.fetchall()
            print(records)
            response = jsonify(records)
            response.status_code = 200
            return response #return all the rows (start , end)
        elif (len(tags) > 1):
            mesh_1 = tags[0]
            one_query = ''
            if (str(mesh_1).isnumeric()):
                one_query = 'concept_id_1 = "'+mesh_1+'"'
            else:
                one_query = 'mesh = "'+mesh_1+'"'
            print("mesh: "+str(mesh_1))
            Pointer.execute("select DISTINCT pmid from tb_articles where "+one_query+" limit "+str(start)+" , "+str(end)+";")
            records = Pointer.fetchall()
            #print(records)

            meshes = []
            concept_ids = []
            pmids = []
            i = 0
            for tag in tags:
                if (i > 0):
                    if (str(tag).isnumeric()):
                        concept_ids.append(tag)
                    else:
                        meshes.append(tag)
                i += 1
            results = []

            for pmid in records:
                found_res = 0
                pmid = pmid['pmid'] #[a,'b,c]

                    #print(mesh)
                if (len(meshes) > 0 and len(concept_ids) > 0):
                    for mesh in meshes:
                        q = "select * from tb_articles where pmid = '"+pmid + "' and mesh like '%"+str(mesh) + "%' limit "+str(start)+" , "+str(end)+";"
                        Pointer.execute(q)
                        records = Pointer.fetchall()
                        if (len(records) > 0):
                            found_res += 1
                            for concept_id in concept_ids:
                                q = "select * from tb_articles where pmid = '"+pmid + "' and concept_id_1 like '%"+concept_id + "%' limit "+str(start)+" , "+str(end)+";"
                                #print(q)
                                Pointer.execute(q)
                                records = Pointer.fetchall()
                                if (len(records) > 0):
                                    found_res += 1
                                else:
                                    found_res = 0
                        else:
                            found_res = 0
                elif (len(meshes) > 0 and len(concept_ids) == 0):
                    print("Only MESHES ...............")
                    for mesh in meshes:
                        q = "select * from tb_articles where pmid = '"+pmid + "' and mesh like '%"+str(mesh) + "%' limit "+str(start)+" , "+str(end)+";"
                        Pointer.execute(q)
                        records = Pointer.fetchall()
                        if (len(records) > 0):
                            found_res += 1
                        else:
                            found_res = 0
                elif (len(meshes) == 0 and len(concept_ids) > 0):

                    for concept_id in concept_ids:
                        q = "select * from tb_articles where pmid = '"+pmid + "' and concept_id_1 like '%"+concept_id + "%' limit "+str(start)+" , "+str(end)+";"
                        #print(q)
                        Pointer.execute(q)
                        records = Pointer.fetchall()
                        if (len(records) > 0):
                            found_res += 1
                        else:
                            found_res = 0

                if (found_res == len(meshes) + len(concept_ids)):
                    results.append(pmid)

            print(results)

            if (len(results) > 0):
                query = ' where ( '
                i = 0
                for result in results:
                    if (i == len(results) - 1):
                        query += " pmid = '"+result +"' ) "
                    else:
                        query += " pmid = '"+result +"' or "
                    i += 1


                q = "select * from tb_articles "+query + "limit "+str(start)+" , "+str(end)+";"
                print(q)
                Pointer.execute(q)
                records = Pointer.fetchall()
                print('res')
                print(result)
                return jsonify(records)

            return jsonify(results)


    else:
        return "err"


@app.route('/fetch_drugs',methods=['POST'])  #method to fetch / search data from database
def fetch_drugs():
    json = request.json
    pmid = json['pmid']
    concept_id_1 = json['concept_id_1']
    if (pmid and concept_id_1 and request.method == 'POST'):

        connection =MySql.connect()
        Pointer = connection.cursor(pymysql.cursors.DictCursor)
        Pointer.execute("select * from tb_articles where (pmid = '"+str(pmid)+"')  and (domain_id = 'Drug');")
        records = Pointer.fetchall()

        response = jsonify(records)
        response.status_code = 200
        return response #return all the rows (start , end)
    else:
        return "err"


@app.route('/fetch_condition',methods=['POST'])  #method to fetch / search data from database
def fetch_condition():
    json = request.json
    pmid = json['pmid']
    concept_id_1 = json['concept_id_1']
    if (pmid and concept_id_1 and request.method == 'POST'):

        connection =MySql.connect()
        Pointer = connection.cursor(pymysql.cursors.DictCursor)
        Pointer.execute("select * from tb_articles where (pmid = '"+str(pmid)+"')  and (domain_id = 'Condition');")
        records = Pointer.fetchall()

        response = jsonify(records)
        response.status_code = 200
        return response #return all the rows (start , end)
    else:
        return "err"


@app.route('/fetch_procedures',methods=['POST'])  #method to fetch / search data from database
def fetch_procedures():
    json = request.json
    pmid = json['pmid']
    concept_id_1 = json['concept_id_1']
    if (pmid and concept_id_1 and request.method == 'POST'):

        connection =MySql.connect()
        Pointer = connection.cursor(pymysql.cursors.DictCursor)
        Pointer.execute("select * from tb_articles where (pmid = '"+str(pmid)+"')  and (domain_id = 'Procedure');")
        records = Pointer.fetchall()

        response = jsonify(records)
        response.status_code = 200
        return response #return all the rows (start , end)
    else:
        return "err"


@app.route('/get_database_table_as_dataframe',methods=['POST'])  #method to fetch / search data from database
def get_database_table_as_dataframe():
    """Connect to a table named 'tb_articles'. Returns pandas dataframe."""
    try:
        connection =MySql.connect()
        articles_df = pd.read_sql(sql="""Sselect * FROM tb_articles""",
                               con=connection)
        logging.info(articles_df.head())
        return articles_df
    except:
        logging.exception('Failed to fetch dataframe from DB.')
        return "Oops!"


@app.route('/plots/articles_df/barchart_plot_diseases', methods=['GET'])
def barchart_plot_diseases():
    bytes_obj = barchart_diseases(get_database_table_as_dataframe)

    return send_file(bytes_obj,
                     attachment_filename='barchart_diseases.png',
                     mimetype='image/png')


@app.route('/plots/articles_df/barchart_plot_drugs', methods=['GET'])
def barchart_plot_drugs():
    bytes_obj = barchart_drugs(get_database_table_as_dataframe)

    return send_file(bytes_obj,
                     attachment_filename='barchart_drugs.png',
                     mimetype='image/png')


@app.route('/',methods=['POST','GET']) # '/' (only with slash), accepts POST and GET methods; Output - in the browser
def display():
    return render_template('index.html')
    # return "P is for Panther"

@app.route('/about',methods=['POST','GET']) 
def display_about():
    # return render_template('index.html')
    return "This is a About us page"

@app.route('/get_data',methods=['POST','GET']) 
def display_get():
    if request.method == "POST":
        filter_data = request.get_json()[0]['filter'].split(',')
        for i in filter_data:
            print(i)
    
        try:            
            connection = pymysql.connect(host='localhost',
                                         port=3306,
                                        user='root',
                                        password='',
                                        database='mydb')
            cursor = connection.cursor()
            sql = "SELECT * FROM articles"
            cursor.execute(sql)
            result = cursor.fetchall()
            print(result)
        except Error as err:
            print(err)
            results = {'processed': str(err)}
            return jsonify(results)

        results = {'processed': 'true'}
        return jsonify(results)
    if request.method == "GET":
        results = {'processed': 'GET is not supported'}
        return jsonify(results)
        


if __name__ == "__main__":
    app.run(debug=True)