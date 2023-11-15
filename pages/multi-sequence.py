import streamlit as st
import matplotlib.pyplot as plt
from pymongo import MongoClient
import pandas as pd

import sys
sys.path.append('..')
from lib import db

def sort_sequence(db, optiSettingHash, envSettingHash, dateTime, group_query):
    # 辞書内包表記を使用してクエリを作成
    query = {
        'optiSettingHash': optiSettingHash if optiSettingHash else None,
        'envSettingHash': envSettingHash if envSettingHash else None,
        'dateTime': dateTime if dateTime else None
    }

    # 空の値を持つキーを除去
    query = {k: v for k, v in query.items() if v is not None}

    documents = db['result'].find(query)

    
    sequenceDf = pd.DataFrame(list(documents))

    if sequenceDf.empty:
        st.write("No Sequence Found")
        return

    # 不要なカラムを削除
    sequenceDf = sequenceDf.drop(['_id', 'resultPos', 'resultRot', 'initPos', 'initRot'], axis=1)
    
    
    # グループ化
    if (group_query == 'dateTime'):
        sequenceDf = sequenceDf.groupby(group_query).agg({
            'score': 'mean',
            'frameCount': 'max',
            'distance': 'mean',
            'angleDiff': 'mean',
            'optiSettingHash': 'first',
            'envSettingHash': 'first',
        })
    elif (group_query == 'optiSettingHash'):
        sequenceDf = sequenceDf.groupby(group_query).agg({
            'score': 'mean',
            'distance': 'mean',
            'angleDiff': 'mean',
        })
    elif (group_query == 'envSettingHash'):
        sequenceDf = sequenceDf.groupby(group_query).agg({
            'score': 'mean',
            'distance': 'mean',
            'angleDiff': 'mean',
        })
    elif (group_query == 'sequenceId'):
        sequenceDf = sequenceDf.groupby(group_query).agg({
            'score': 'mean',
            'frameCount': 'max',
            'distance': 'mean',
            'angleDiff': 'mean',
            'dateTime': 'first',
            'optiSettingHash': 'first',
            'envSettingHash': 'first',
        })


    # scoreでソート
    sequenceDf = sequenceDf.sort_values(['score'], ascending=True).reset_index()

    

    # matplotlibでグラフを描画
    fig, ax = plt.subplots()
    ax.bar(sequenceDf.index ,sequenceDf['score'])
    ax.set_xlabel('Sequence ID')
    ax.set_ylabel('Score')
    ax.set_title('Score Over Sequence ID')
    ax.grid(True)
    plt.tight_layout()
    st.pyplot(fig)

    # 表
    st.table(sequenceDf)



st.title("Sort Sequence Viewer")

database = db.get_db()

opti_settings = db.get_all_optiSettings()
opti_settings = opti_settings['_id'].to_list()
opti_settings.insert(0, None)
selected_opti_setting = st.selectbox("Opti Setting", opti_settings)

env_settings = db.get_all_envSettings()
env_settings = env_settings['_id'].to_list()
env_settings.insert(0, None)
selected_env_setting = st.selectbox("Env Setting", env_settings)

selected_dateTime = st.text_input("Date Time")

group_querys = ['optiSettingHash', 'envSettingHash', 'dateTime', 'sequenceId']
group_query = st.selectbox("Group By", group_querys)



if st.button("Sort Sequence", type="primary"):
    sort_sequence(database, selected_opti_setting, selected_env_setting, selected_dateTime, group_query)
