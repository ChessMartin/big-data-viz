import pandas as pd
import mysql.connector
import pandas as pd
import numpy as np
import os
import glob
from datetime import datetime
import matplotlib.pyplot as plt
import plotly.express as px
import dash
from dash.dash_table.Format import Group
from dash import Dash, html, dcc, callback, Output, Input
import plotly.graph_objs as go
import seaborn as sns

mydb = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="username",
            password="pwd",
            database="yourdatabase")
mycursor = mydb.cursor()

def find_alltime(name:str, number:int):
    
    sql = "SELECT {}, COUNT(*) AS Count FROM Music GROUP BY {} ORDER BY Count DESC LIMIT {};".format(name,name,number)
    mycursor.execute(sql)

    rows = mycursor.fetchall()
    Rank_alltime = pd.DataFrame(rows, columns=['{}'.format(name), 'count'])
   
    # mycursor.close()
    # mydb.close()
    return Rank_alltime

def find_weeklytop10(name:str):
    sql = f"""
    SELECT week, {name}, appearance_count
    FROM (
        SELECT 
            CONCAT(DATE(DATE_SUB(time, INTERVAL WEEKDAY(time) DAY)), ' to ', DATE(DATE_ADD(DATE_SUB(time, INTERVAL WEEKDAY(time) DAY), INTERVAL 6 DAY))) AS week,
            COALESCE({name}, 'Unknown') AS {name},
            COUNT(*) AS appearance_count,
            ROW_NUMBER() OVER (PARTITION BY CONCAT(DATE(DATE_SUB(time, INTERVAL WEEKDAY(time) DAY)), ' to ', DATE(DATE_ADD(DATE_SUB(time, INTERVAL WEEKDAY(time) DAY), INTERVAL 6 DAY))) ORDER BY COUNT(*) DESC) AS ranking
        FROM Music
        WHERE time IS NOT NULL AND {name} IS NOT NULL
        GROUP BY week, {name}
    ) AS ranked_{name}
    WHERE ranking between 1 and 10;
    """

    mycursor.execute(sql)
    rows = mycursor.fetchall()
    Rank_weekly = pd.DataFrame(rows, columns=['week','{}'.format(name), 'count'])
    return Rank_weekly

def Cross_Tabulation(name1:str,name2:str):
    sql = f"""SELECT {name1}, {name2}, COUNT(*) AS count
    FROM music
    GROUP BY {name1}, {name2}
    ORDER BY {name1}, {name2} ;
    """
    mycursor.execute(sql)
    rows = mycursor.fetchall()
    result = pd.DataFrame(rows, columns=['{}'.format(name1),'{}'.format(name2), 'count'])
    return result

def year_count(name:str):
    sql = f"""SELECT {name}, YEAR(time) AS year, COUNT(*) AS count
            FROM music
            WHERE time IS NOT NULL
            GROUP BY {name}, YEAR(time)
            ORDER BY {name}, YEAR(time)
            ;"""
    mycursor.execute(sql)
    rows = mycursor.fetchall()
    result = pd.DataFrame(rows, columns=['{}'.format(name),'year', 'count'])
    return result