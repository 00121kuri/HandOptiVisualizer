import streamlit as st
import matplotlib.pyplot as plt
from pymongo import MongoClient
import pandas as pd

import sys
sys.path.append('..')
from lib import db

INIT_OPTI_SETTINGS = {
    'optiSettingHash': 'init',
    'mutationRate': -1,
    'sigma': -1,
    'mean': -1,
    'worstScore': -1,
    'maxSteps': -1,
    'isUsePreviousResult': False,
    'weightDistance': 1,
    'weightRotation': 0.1,
    'weightChromosomeDiff': 0,
}

def sort_sequence(database, optiSettingHashs, envSettingHashs, dateTimes, group_query, selected_opti_param):
    # 辞書内包表記を使用してクエリを作成
    query = {
        'optiSettingHash': {'$in': optiSettingHashs} if optiSettingHashs else None,
        'envSettingHash': {'$in': envSettingHashs} if envSettingHashs else None,
        'dateTime': {'$in': dateTimes} if dateTimes else None
    }

    # 空の値を持つキーを除去
    query = {k: v for k, v in query.items() if v is not None}

    print(query)

    documents = database['result'].find(query)

    
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


    if (group_query == 'optiSettingHash'):
        # sequenceDfに結合
        optiSettings = db.get_all_optiSettings()
        optiSettings = optiSettings.rename(columns={'_id': 'optiSettingHash'})
        optiSettings_df = pd.DataFrame([INIT_OPTI_SETTINGS])
        # jsonを表に変換
        for i, row in optiSettings.iterrows():
            optiSetting = row['optiSetting']
            optiSettings_df.at[i, 'optiSettingHash'] = row['optiSettingHash']
            for key in optiSettings_df.columns:
                if key in optiSetting:
                    optiSettings_df.at[i, key] = optiSetting[key]
                elif key != 'optiSettingHash':
                    optiSettings_df.at[i, key] = INIT_OPTI_SETTINGS[key]

        
        sequenceDf = pd.merge(sequenceDf, optiSettings_df, on='optiSettingHash')
        
        # 選択したキーの値でグループ化
        if selected_opti_param:
            sequenceDf = sequenceDf.groupby(selected_opti_param).agg({
                'score': 'mean',
                'distance': 'mean',
                'angleDiff': 'mean',
            })
        
    # scoreでソート
    sequenceDf = sequenceDf.sort_values(['score'], ascending=True).reset_index()
    

    # matplotlibでグラフを描画
    fig, ax = plt.subplots()
    if (group_query == 'optiSettingHash' and selected_opti_param):
        if selected_opti_param == 'isUsePreviousResult':
            ax.bar(sequenceDf.index ,sequenceDf['score'])
        else:
            # x軸でソート
            sequenceDf = sequenceDf.sort_values([selected_opti_param], ascending=True).reset_index()
            # 点をプロット
            ax.plot(sequenceDf[selected_opti_param], sequenceDf['score'])
    else:
        ax.bar(sequenceDf.index ,sequenceDf['score'])
    xlabel = group_query
    if (selected_opti_param):
        xlabel += ' - ' + selected_opti_param
    ax.set_xlabel(xlabel)
    ax.set_ylabel('Score')
    #ax.set_title('Score Over Sequence ID')
    ax.grid(True)
    plt.tight_layout()
    st.pyplot(fig)

    # 表
    st.table(sequenceDf)



st.title("Sort Sequence Viewer")

database = db.get_db()

opti_settings = db.get_all_optiSettings()
opti_settings = opti_settings['_id'].to_list()
selected_opti_settings = st.multiselect("Opti Setting", opti_settings)

env_settings = db.get_all_envSettings()
env_settings = env_settings['_id'].to_list()
selected_env_settings = st.multiselect("Env Setting", env_settings)

dateTimes = db.get_all_dateTime()
selected_dateTimes = st.multiselect("Date Time", dateTimes)

group_querys = ['optiSettingHash', 'envSettingHash', 'dateTime', 'sequenceId']
group_query = st.selectbox("Group By", group_querys)


selected_opti_param = None
if (group_query == 'optiSettingHash'):
    selected_opti_param = st.text_input("Opti Setting Param", "maxSteps")


if st.button("Sort Sequence", type="primary"):
    sort_sequence(database, selected_opti_settings, selected_env_settings, selected_dateTimes, group_query, selected_opti_param)
