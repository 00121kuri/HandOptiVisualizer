import streamlit as st
import matplotlib.pyplot as plt
from pymongo import MongoClient
import pandas as pd

import sys
sys.path.append('..')
from lib import db


def one_sequence_viewer(db, sequenceId):
    st.write(f"Sequence ID: {sequenceId}")
    documents = db['result'].find({'sequenceId': sequenceId})

    optiSettingHash = documents[0]['optiSettingHash']
    envSettingHash = documents[0]['envSettingHash']
    dateTime = documents[0]['dateTime']

    st.write(f"Date Time: {dateTime}")

    st.write(f"Opti Setting Hash: {optiSettingHash}")
    optiSetting = db['opti-setting'].find_one({'_id': optiSettingHash})
    with st.expander("Opti Setting Details"):
        # 辞書をDataFrameに変換
        df = pd.DataFrame(list(optiSetting['optiSetting'].items()), columns=['Parameter', 'Value'])
        st.table(df)
    

    st.write(f"Env Setting Hash: {envSettingHash}")
    envSetting = db['env-setting'].find_one({'_id': envSettingHash})
    with st.expander("Env Setting Details"):
        # 辞書をDataFrameに変換
        df = pd.DataFrame(list(envSetting['envSetting'].items()), columns=['Parameter', 'Value'])
        st.table(df)
    

    frameCountList = []
    scoreList = []
    distanceList = []
    angleList = []

    for document in documents:
        frameCountList.append(document['frameCount'])
        scoreList.append(document['score'])
        distanceList.append(document['distance'])
        angleList.append(document['angleDiff'])



    # scoreのグラフ
    fig, ax = plt.subplots()
    ax.bar(frameCountList, scoreList)
    ax.set_xlabel('Frame Count')
    ax.set_ylabel('Score')
    ax.set_title('Score Over Frame Count')
    ax.grid(True)
    plt.tight_layout()
    st.pyplot(fig)

    # distanceのグラフ
    fig, ax = plt.subplots()
    ax.bar(frameCountList, distanceList, color='orange')
    ax.set_xlabel('Frame Count')
    ax.set_ylabel('Distance')
    ax.set_title('Distance Over Frame Count')
    ax.grid(True)
    plt.tight_layout()
    st.pyplot(fig)

    # angleのグラフ
    fig, ax = plt.subplots()
    ax.bar(frameCountList, angleList, color='green')
    ax.set_xlabel('Frame Count')
    ax.set_ylabel('Angle')
    ax.set_title('Angle Over Frame Count')
    ax.grid(True)
    plt.tight_layout()
    st.pyplot(fig)


st.set_page_config(
    layout="wide",
)

st.title("One Sequence")

sequenceId = st.text_input("Sequence ID")

database = db.get_db()

if sequenceId != "":
    one_sequence_viewer(database, sequenceId)
else:
    st.write("Please input Sequence ID !")


