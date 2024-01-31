import streamlit as st
import matplotlib.pyplot as plt
from pymongo import MongoClient
import pandas as pd
import os

import sys
from lib.params import ParamType

from lib.score import ScoreType
sys.path.append('..')
from lib import db

INIT_OPTI_SETTINGS = {
    'optiSettingHash': 'init',
    'mutationRate': -1,
    'sigma': -1,
    'mean': 0,
    'worstScore': -1,
    'maxSteps': -1,
    'isUsePreviousResult': False,
    'weightDistance': 1,
    'weightRotation': 0.1,
    'weightChromosomeDiff': 0,
    'wieghtInputChromosomeDiff': 0,
    'isUseInputChromosome': False,
}

def sort_sequence(database, optiSettingHashs, envSettingHashs, dateTimes, group_query, selected_opti_param, file_name = ''):
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
            ScoreType.SCORE.name_db: 'mean',
            'frameCount': 'max',
            ScoreType.DISTANCE.name_db: 'mean',
            ScoreType.ANGLE_DIFF.name_db: 'mean',
        })
    elif (group_query == 'optiSettingHash'):
        sequenceDf = sequenceDf.groupby(group_query).agg({
            ScoreType.SCORE.name_db: 'mean',
            ScoreType.DISTANCE.name_db: 'mean',
            ScoreType.ANGLE_DIFF.name_db: 'mean',
        })
    elif (group_query == 'envSettingHash'):
        sequenceDf = sequenceDf.groupby(group_query).agg({
            ScoreType.SCORE.name_db: 'mean',
            ScoreType.DISTANCE.name_db: 'mean',
            ScoreType.ANGLE_DIFF.name_db: 'mean',
        })
    elif (group_query == 'sequenceId'):
        sequenceDf = sequenceDf.groupby(group_query).agg({
            ScoreType.SCORE.name_db: 'mean',
            'frameCount': 'max',
            ScoreType.DISTANCE.name_db: 'mean',
            ScoreType.ANGLE_DIFF.name_db: 'mean',
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
            sequenceDf = sequenceDf.groupby(selected_opti_param.param_name).agg({
                ScoreType.SCORE.name_db: 'mean',
                ScoreType.DISTANCE.name_db: 'mean',
                ScoreType.ANGLE_DIFF.name_db: 'mean',
            })
        
    # scoreでソート
    sequenceDf = sequenceDf.sort_values([ScoreType.SCORE.name_db], ascending=True).reset_index()
    

    # matplotlibでグラフを描画
    fig, ax = plt.subplots(3, 1, figsize=(10, 10), sharex=True, sharey=False)
    if (group_query == 'optiSettingHash' and selected_opti_param):
        # x軸でソート
        sequenceDf = sequenceDf.sort_values([selected_opti_param.param_name], ascending=True)
        # score, distance, angleDiffを描画
        ax[0].plot(sequenceDf[selected_opti_param.param_name], sequenceDf[ScoreType.SCORE.name_db], color=ScoreType.SCORE.color, label=ScoreType.SCORE.label, marker='o')
        ax[1].plot(sequenceDf[selected_opti_param.param_name], sequenceDf[ScoreType.DISTANCE.name_db], color=ScoreType.DISTANCE.color, label=ScoreType.DISTANCE.label, marker='o')
        ax[2].plot(sequenceDf[selected_opti_param.param_name], sequenceDf[ScoreType.ANGLE_DIFF.name_db], color=ScoreType.ANGLE_DIFF.color, label=ScoreType.ANGLE_DIFF.label, marker='o')
        
    else:
        # score, distance, angleDiffをbarで描画
        ax[0].bar(sequenceDf.index, sequenceDf[ScoreType.SCORE.name_db], color=ScoreType.SCORE.color, label=ScoreType.SCORE.label)
        ax[1].bar(sequenceDf.index, sequenceDf[ScoreType.DISTANCE.name_db], color=ScoreType.DISTANCE.color, label=ScoreType.DISTANCE.label)
        ax[2].bar(sequenceDf.index, sequenceDf[ScoreType.ANGLE_DIFF.name_db], color=ScoreType.ANGLE_DIFF.color, label=ScoreType.ANGLE_DIFF.label)
    xlabel = group_query
    if (selected_opti_param):
        xlabel = selected_opti_param.label
    ax[2].set_xlabel(xlabel)

    ax[0].set_ylabel(ScoreType.SCORE.label)
    ax[1].set_ylabel(ScoreType.DISTANCE.label + ' [m]')
    ax[2].set_ylabel(ScoreType.ANGLE_DIFF.label + ' [deg]')

    # それぞれのグラフのy軸の最大値を取得
    max_score = sequenceDf[ScoreType.SCORE.name_db].max()
    max_distance = sequenceDf[ScoreType.DISTANCE.name_db].max()
    max_angleDiff = sequenceDf[ScoreType.ANGLE_DIFF.name_db].max()

    # y軸を0スタートにする
    ax[0].set_ylim(0, max_score*1.1)
    ax[1].set_ylim(0, max_distance*1.1)
    ax[2].set_ylim(0, max_angleDiff*1.1)

    #ax.set_title('Score Over Sequence ID')
    ax[0].grid(True)
    ax[1].grid(True)
    ax[2].grid(True)
    plt.tight_layout()
    st.pyplot(fig)

    # 表
    st.table(sequenceDf)

    # latexの表として表示
    tex = sequenceDf.to_latex(index=False)

    # 保存
    if file_name != '':
        if not os.path.exists(f'export/sort-sequence/{file_name}'):
            os.mkdir(f'export/sort-sequence/{file_name}')
        fig.savefig(f'export/sort-sequence/{file_name}/{file_name}.png')
        fig.savefig(f'export/sort-sequence/{file_name}/{file_name}.eps')
        fig.savefig(f'export/sort-sequence/{file_name}/{file_name}.pdf')
        with open(f'export/sort-sequence/{file_name}/{file_name}.tex', mode='w') as f:
            f.write(tex)
        # クエリを保存
        with open(f'export/sort-sequence/{file_name}/{file_name}-query.txt', mode='w') as f:
            f.write(str(query))

st.set_page_config(
    layout="wide",
)


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

group_querys = ['sequenceId', 'optiSettingHash', 'envSettingHash', 'dateTime']
group_query = st.selectbox("Group By", group_querys)


selected_opti_param = None
if (group_query == 'optiSettingHash'):
    selected_opti_param = st.selectbox("Opti Param", [param_type for param_type in ParamType])

file_name = st.text_input("File Name", value=f'')

if st.button("Sort Sequence", type="primary"):
    sort_sequence(database, selected_opti_settings, selected_env_settings, selected_dateTimes, group_query, selected_opti_param, file_name)
