import streamlit as st
import matplotlib.pyplot as plt
from pymongo import MongoClient
import pandas as pd
import math
import os
import plotly.graph_objects as go
import plotly.io as pio

import sys
sys.path.append('..')
from lib import db
from lib.score import ScoreType


def multi_sequence_viewer(sequenceIds, col_num=1, folder_name=''):
    database = db.get_db()
    documents = database['result'].find({'sequenceId': {'$in': sequenceIds}})
    
    sequenceDf = pd.DataFrame(list(documents))

    if sequenceDf.empty:
        st.write("No Sequence Found")
        return

    # 不要なカラムを削除
    sequenceDf = sequenceDf.drop(['_id', 'resultPos', 'resultRot', 'initPos', 'initRot'], axis=1)

    # グループ化
    sequenceDf_group = sequenceDf.groupby('sequenceId').agg({
            'frameCount': 'max',
            'score': 'mean',
            'distance': 'mean',
            'angleDiff': 'mean',
            'dateTime': 'first',
            'optiSettingHash': 'first',
            'envSettingHash': 'first',
        })
    
    # scoreでソート
    #sequenceDf_group = sequenceDf_group.sort_values(['score'], ascending=True).reset_index()
    # sequenceIdsの順番にソート
    sequenceDf_group = sequenceDf_group.reindex(sequenceIds).reset_index()


    # 複数のグラフを並べて表示, ユニークなsequenceIdの数に応じて行数を変更
    for score_type in ScoreType:
        # データに含まれていないscore_typeはスキップ
        if score_type.name_db not in sequenceDf.columns:
            continue
        size = 2
        fig = plt.figure(figsize=(4 * size * int(col_num), 3 * size * math.ceil(len(sequenceIds)/col_num)))
        # y軸の範囲を揃えるために最大値を取得
        max_y = sequenceDf[score_type.name_db].max()
        for i, sequenceId in enumerate(sequenceDf_group['sequenceId']):
            sequence = sequenceDf[sequenceDf['sequenceId'] == sequenceId]
            # 順番に配置する
            ax = fig.add_subplot(math.ceil(len(sequenceIds)/col_num), col_num, i+1)
            ax.bar(sequence['frameCount'], sequence[score_type.name_db], color=score_type.color)
            ax.set_xlabel('Frame Count')
            ax.set_ylim(0, max_y*1.1)
            ax.set_ylabel(score_type.label)
            ax.set_title(f'{score_type.label} - Sequence ID: {sequenceId}')
            ax.grid(True)
        plt.tight_layout()
        st.pyplot(fig)
        # 画像を保存
        if folder_name != '':
            # フォルダがなければ作成
            export_dir = f'export/multi-sequence/{folder_name}'
            if not os.path.exists(export_dir):
                os.makedirs(export_dir)
            # pngを保存
            plt.savefig(f'{export_dir}/{folder_name}-{score_type.name_db}.png')
            # plt.savefig(f'export/multi-sequence/{folder_name}/{folder_name}-{score_type.name_db}.eps')
            plt.savefig(f'{export_dir}/{folder_name}-{score_type.name_db}.pdf')

    # 表を作成
    sequenceDf_group_table =sequenceDf_group.drop(['optiSettingHash', 'envSettingHash', 'dateTime'], axis=1)
    sequenceDf_group_table = sequenceDf_group_table.rename(columns={'frameCount': 'Frame Count', 'score': 'Score', 'distance': 'Distance', 'angleDiff': 'Angle Diff'})
    sequenceDf_group_table = sequenceDf_group_table.round(6)
    st.table(sequenceDf_group_table)

    # latexの表として表示
    tex = sequenceDf_group_table.to_latex(index=False)
    #st.latex(tex)

    # 各シーケンスごとにまとめたグラフを表示
    for i, sequenceId in enumerate(sequenceDf_group['sequenceId']):
        fig = plt.figure(figsize=(10, 8))
        fig.suptitle(f'Sequence ID: {sequenceId}')
        for score_type in ScoreType:
            if score_type.name_db not in sequenceDf.columns:
                continue
            if score_type.name_db == 'score':
                ax = plt.subplot(3, 1, 1)
            else:
                ax = plt.subplot(3, 2, score_type.id+1)
            sequence = sequenceDf[sequenceDf['sequenceId'] == sequenceId]
            ax.bar(sequence['frameCount'], sequence[score_type.name_db], color=score_type.color)
            ax.set_xlabel('Frame Count')
            ax.set_ylabel(score_type.label)
            ax.set_title(f'{score_type.label}')
            ax.grid(True)
        plt.tight_layout()
        st.pyplot(fig)
        # 画像を保存
        if folder_name != '':
            # pngを保存
            plt.savefig(f'{export_dir}/{folder_name}-{sequenceId}.png')
            # plt.savefig(f'export/multi-sequence/{folder_name}/{folder_name}-{sequenceId}.eps')
            plt.savefig(f'{export_dir}/{folder_name}-{sequenceId}.pdf')


    # それぞれのsequenceIdの詳細を表示
    for sequenceId in sequenceDf_group['sequenceId']:
        with st.expander(f"Sequence ID: {sequenceId}"):
            sequence = sequenceDf_group[sequenceDf_group['sequenceId'] == sequenceId]
            st.table(sequence.drop(['optiSettingHash', 'envSettingHash'], axis=1))
            optiSettingHash = sequence['optiSettingHash'].values[0]
            envSettingHash = sequence['envSettingHash'].values[0]
            optiSetting = database['opti-setting'].find_one({'_id': optiSettingHash})
            envSetting = database['env-setting'].find_one({'_id': envSettingHash})
            st.write(f"Opti Setting Hash: {optiSettingHash}")
            st.table(pd.DataFrame(list(optiSetting['optiSetting'].items()), columns=['Parameter', 'Value']))
            st.write(f"Env Setting Hash: {envSettingHash}")
            st.table(pd.DataFrame(list(envSetting['envSetting'].items()), columns=['Parameter', 'Value']))

    # 保存
    if folder_name != '':
        # csvを保存
        sequenceDf_group.to_csv(f'{export_dir}/{folder_name}.csv', index=False)
        # texを保存
        with open(f'{export_dir}/{folder_name}.tex', mode='w') as f:
            f.write(tex)
        # クエリを保存
        with open(f'{export_dir}/{folder_name}-query.txt', mode='w') as f:
            f.write(str(sequenceIds))
    
    

st.set_page_config(
    layout="wide",
)

st.title("Multi Sequence")


sequenceIds = st.multiselect("Sequence ID", db.get_all_sequenceIds())
# y_axis = st.selectbox("Y Axis", ['score', 'distance', 'angleDiff'])
# グラフを並べる横の数
col_num = st.slider("Column Num", 1, 5, 1)
# 生成したグラフを保存
file_name = st.text_input('File Name', value=f'')

database = db.get_db()

if st.button("Show") and sequenceIds:
    if file_name != '':
        multi_sequence_viewer(sequenceIds, col_num, file_name)
    else:
        multi_sequence_viewer(sequenceIds, col_num)
else:
    st.write("Please input Sequence ID !")


