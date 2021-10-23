# Gold Mastery Test.py

from flask import Flask, request
from flask_restful import Resource, Api

from sklearn import metrics

import pandas as pd
import sqlite3
import sqlalchemy
import json
import pyodbc

app = Flask(__name__)
api = Api(app)


class Submit(Resource):
    def post(self):
        # try:
        engine = sqlalchemy.create_engine(
            "mssql+pyodbc://julesd:Password1@akmtntest.database.windows.net/akmtntest?DRIVER={ODBC Driver 17 for SQL Server}",
            echo=True)
        # con = sqlite3.connect('data.db')
        # cursor = con.cursor()
        print('Line 25')
        data = request.get_json()
        print(data)

        name = data["name"]
        email = data["email"]
        x = data["x"]

        x_df = pd.DataFrame(columns=['imei', 'pred'])

        imei = list(x.keys())
        pred = list(x.values())
        x_df['imei'] = imei
        x_df['pred'] = pred
        x_df['pred'] = x_df['pred'].astype('int')
        # x_df['imei'] = x_df['imei'].astype('int64')
        x_df.index = x_df['imei']
        x_df.drop('imei', axis=1, inplace=True)
        x_df

        print('x_df created')

        # y = pd.read_sql_query('SELECT * FROM answer', con=con)
        y = pd.read_sql_query('SELECT * FROM answer', con=engine)
        y['status'] = y['status'].astype('int')
        print('past read_sql_query')

        print('con closed')

        # cnxn = sqlite3.connect('data.db')
        # cursor1 = cnxn.cursor()
        # print('cnxn open')

        # y['imei'] = y['imei'].astype('int64')
        y.index = y['imei']
        y.drop('imei', axis=1, inplace=True)

        result = pd.concat([x_df, y], axis=1)
        print(result.head())
        print('18:43')

        score = metrics.f1_score(result['pred'], result['status'])
        print(score)

        submissions = pd.read_sql('SELECT * FROM Submissions', con=engine)
        # print(submissions.head())
        submissions = submissions.append(
            {'ID': max(submissions['ID'] + 1), 'Name': name, 'email': email, 'score': score}, ignore_index=True)
        print('appended')

        # submissions.to_sql('Submissions',if_exists ='replace', con=con, index=False)
        submissions.to_sql('submissions', if_exists='replace', con=engine, index=False)

        # cursor.close()
        # con.close()

        print('complete')
        # print(sqlite3.__version__)

        return {'message': f'F1 Score: {score * 100}%'}

    # except Exception as e:
    #     return {'error message':str(e)}


class Scores(Resource):
    def get(self):
        engine = sqlalchemy.create_engine(
            "mssql+pyodbc://julesd:Password1@akmtntest.database.windows.net/akmtntest?DRIVER={ODBC Driver 17 for SQL Server}",
            echo=True)

        query = 'SELECT * FROM Submissions'

        results = pd.read_sql_query(query, con=engine)
        results = results.to_dict()

        return {'message': results}


class Home(Resource):
    def get(self):
        return "Home"


api.add_resource(Submit, '/submit')
api.add_resource(Scores, '/scores')
api.add_resource(Home, '/home')

app.run(port=5000)
