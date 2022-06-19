import requests
import pandas
from flask import Flask, request, Response

SERVER_URL = 'http://tandem7.pythonanywhere.com' # same this for this one it's API_SERVER URL
endpoint = '/add'

# It is the function to read your csv data returnd by scraping script that you have.
def read_csv_data():

    #first let me show you how much already added data in database. 4195 already present data.
    # can you please show me this .csv file or put this csv file in same path of sccript?
    # yeah let me search for it..
    # you can also set it's path to csv file
    data = pandas.read_csv('final_df_sample_noindex_with_domain.csv', sep=',')
    return data # and here it's returning all the readed data from csv file , I am using pandas for reading file

def upload_data():
    csv_data = read_csv_data()

    for i in range(len(csv_data)):

        pmid = csv_data['pmid'][i]
        pm_link = csv_data['pm_link'][i]
        date_pub = csv_data['date_pub'][i]
        journal = csv_data['journal'][i]
        abstract = csv_data['abstract'][i]
        title = csv_data['title'][i]
        mesh = csv_data['mesh'][i]
        concept_id_1 = csv_data['concept_id_1'][i]
        concept_name = csv_data['concept_name'][i]
        study_design = csv_data['study_design'][i]
        data_type = csv_data['data_type'][i]
        domain_id = csv_data['domain_id'][i]
        category_name = csv_data['category_name'][i]
        print(category_name)

        # So now here is i am putting data to payload to send data to server via API
        data = {}
        data['pmid'] = str(pmid)
        data['pm_link'] = str(pm_link)
        data['date_pub'] = str(date_pub)
        data['journal'] = str(journal)
        data['abstract'] = str(abstract)
        data['title'] = str(title)
        data['mesh'] = str(mesh)
        data['concept_id_1'] = str(concept_id_1)
        data['concept_name'] = str(concept_name)
        data['study_design'] = str(study_design)
        data['data_type'] = str(data_type)
        data['domain_id'] = str(domain_id)
        data['category_name'] = str(category_name)
        print(data)

        res = requests.post(url=SERVER_URL + endpoint ,json=data) # and here sending data to server and getting response.
        if (res.status_code == 200):
            print(res.text + ": "+str(i) + " out of {}".format(len(csv_data['title'])))
        else:
            print(res.text)


    #Sure so now let me show you how you can add more columns in easy way but one more thing when you will add more columns you need to add columns in server script too.
    # ok, just show me please)
    # ok


if __name__ == "__main__":
    print(read_csv_data())


