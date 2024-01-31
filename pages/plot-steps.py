import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import time
import os

import sys
sys.path.append('..')
from lib.score import ScoreType

def plot_steps(uploaded_files, max_steps, file_name):
    proggres_bar = st.progress(0, 'Loading Files...')
    percent_complete = 0.0
    # 経過時間の計測
    start_time = time.time()

    df_list = []

    for uploaded_file in uploaded_files:
        percent_complete += 1 / len(uploaded_files)
        if percent_complete < 1.0:
            proggres_bar.progress(percent_complete)
        df = pd.read_csv(uploaded_file)
        filled_df = fill_steps(df, max_steps)
        df_list.append(filled_df)
    
    proggres_bar.empty()

    # データフレームのリストを平均化
    mean_df = df_list[0]
    for i in range(1, len(df_list)):
        mean_df += df_list[i]
    mean_df /= len(df_list)
    # 平均化したデータフレームを描画

    export_folder = f'export/plot-steps/{file_name}'
    
    
    for score_type in ScoreType:
        # 角度差はスキップ
        if score_type == ScoreType.ANGLE_DIFF:
            continue
        fig = plt.figure(figsize=(4, 3))
        plt.plot(mean_df['frameCount'], mean_df[score_type.name_csv], color=score_type.color)
        plt.xlabel('Step Count')
        plt.ylabel(score_type.label)
        # plt.title(f'{score_type.label}')
        plt.grid(True)
        plt.tight_layout()
        # st.pyplot(fig)
        if (file_name != ''):
            # フォルダがなければ作成
            if not os.path.exists(export_folder):
                os.makedirs(export_folder)
            fig.savefig(f'{export_folder}/{file_name}-{max_steps}-{score_type.name_csv}.png')
            # pdf も出力
            fig.savefig(f'{export_folder}/{file_name}-{max_steps}-{score_type.name_csv}.pdf')
    
    # グラフを並べて表示
    fig = plt.figure(figsize=(10, 8))
    for score_type in ScoreType:
        # 角度差はスキップ
        if score_type == ScoreType.ANGLE_DIFF:
            continue
        if score_type.name_csv == 'score':
            ax = plt.subplot(3, 1, 1)
        else:
            ax = plt.subplot(3, 2, score_type.id+1)
        plt.plot(mean_df['frameCount'], mean_df[score_type.name_csv], color=score_type.color)
        plt.xlabel('Step Count')
        plt.ylabel(score_type.label)
        plt.title(f'{score_type.label}')
        plt.grid(True)
    plt.tight_layout()
    st.pyplot(fig)

    if (file_name != ''):
        fig.savefig(f'{export_folder}/{file_name}-{max_steps}.png')
        # pdf も出力
        fig.savefig(f'{export_folder}/{file_name}-{max_steps}.pdf')
    

    # 経過時間の表示
    elapsed_time = time.time() - start_time
    st.write(f'Elapsed Time: {elapsed_time} [sec]')

        

def fill_steps(df, max_steps):
    # proggres_bar = st.progress(0, 'Filling Steps...')
    # percent_complete = 0.0

    input_dict_array = df.to_dict('records')

    filled_dict_array = []
    filled_df = df.copy()
    #fremeCountの値ががない場合は追加して前のフレームの値をコピー
    step_index = -1
    for i in range(-1, max_steps):
        # percent_complete += 1 / max_steps
        # if percent_complete < 1.0:
        #     proggres_bar.progress(percent_complete)
        if i not in df['frameCount'].values:
            # # frameCountの値を更新
            insert_dict = input_dict_array[step_index].copy()
            insert_dict['frameCount'] = i
            filled_dict_array.append(insert_dict)

        else:
            step_index += 1
            filled_dict_array.append(input_dict_array[step_index])

    filled_df = pd.DataFrame(filled_dict_array)
    # proggres_bar.empty()

            

    # frameCountでソート
    filled_df = filled_df.sort_values(['frameCount'], ascending=True).reset_index(drop=True)
    return filled_df
    


uploaded_files = st.file_uploader("Choose a CSV file", accept_multiple_files=True)
max_steps = st.number_input("Max Steps", 100, 100000, 50000)

file_name = st.text_input("File Name", "")

if st.button("Plot") and uploaded_files:
    plot_steps(uploaded_files, max_steps, file_name)