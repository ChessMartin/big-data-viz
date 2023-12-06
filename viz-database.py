import pandas as pd
import os
import mysql.connector
from datetime import datetime

def add_data_from_csv():
    mydb = mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="yourpwd",
        database="yourdatabase"
    )


    mycursor = mydb.cursor()

    mycursor.execute("CREATE TABLE IF NOT EXISTS Music (id INT AUTO_INCREMENT PRIMARY KEY, listener TEXT, artist TEXT, album TEXT, track TEXT, time DATETIME)")


    folder_path = r'C:\dataViz\Viz\Lastfm'   #your file path
    total_files = len([file for file in os.listdir(folder_path) if file.endswith('.csv')])
    processed_files = 0
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.csv'):
            file_path = os.path.join(folder_path, file_name)            
            listener = os.path.splitext(file_name)[0]
            
            
            try:
                data = pd.read_csv(file_path, header=None)
                for index, row in data.iterrows():
                    
                    artist = row[0]
                    album = row[1]
                    track = row[2]
                    time = row[3]
                    
                    
                    if pd.isnull(artist):
                        artist = None
                    if pd.isnull(album):
                        album = None
                    if pd.isnull(track):
                        track = None
                    if pd.isnull(time):
                        time = None
                    else:
                        time = datetime.strptime(str(time), '%d %b %Y %H:%M')  
                    
                    
                    sql = "INSERT INTO Music (listener, artist, album, track, time) VALUES (%s, %s, %s, %s, %s)"
                    val = (listener, artist, album, track, time)
                    mycursor.execute(sql, val)
                    mydb.commit()
            except:
                artist, album, track, time = None, None, None, None
                sql = "INSERT INTO Music (listener, artist, album, track, time) VALUES (%s, %s, %s, %s, %s)"
                val = (listener, artist, album, track, time)
                mycursor.execute(sql, val)
                mydb.commit()
                
                

            processed_files += 1
            print(f"Processed file {listener}{processed_files} of {total_files}")
    print("finish")

    mycursor.close()
    mydb.close()
