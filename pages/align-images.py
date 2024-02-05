import datetime
import streamlit as st
import matplotlib.pyplot as plt
import os

def align_images(uploaded_files, folder_name, file_name, prefix, suffix):
    images = sort_images(uploaded_files)
    fig, ax = plt.subplots(1, len(images), figsize=(2 * len(images) * 0.9, 2), dpi=200)
    for i, image in enumerate(images):
        ax[i].imshow(plt.imread(image))
        title = prefix + image.name.split('.')[0] + suffix
        ax[i].set_title(title, y=-0.2)
        ax[i].axis('off')
    plt.tight_layout()
    st.pyplot(fig)
    
    # 画像を保存
    if folder_name != '':
        export_folder = 'export/align-images' + '/' + folder_name
    else:
        export_folder = 'export/align-images/out'
    if not os.path.exists(export_folder):
        os.makedirs(export_folder)
    if (file_name == ''):
        file_name = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    fig.savefig(f'{export_folder}/{file_name}.png', bbox_inches='tight')
    fig.savefig(f'{export_folder}/{file_name}.pdf', bbox_inches='tight')


def sort_images(uploaded_files):
    images = []
    for uploaded_file in uploaded_files:
        images.append(uploaded_file)
    images.sort(key=lambda x: int(x.name.split('.')[0]))
    print(images)
    return images


uploaded_files = st.file_uploader('Choose a Image files', accept_multiple_files=True)
folder_name = st.text_input('Folder Name', '')
file_name = st.text_input('File Name', '')
prefix = st.text_input('Prefix', 'Frame: ')
suffix = st.text_input('Suffix', '')

if st.button('Align Images') and uploaded_files:
    align_images(uploaded_files, folder_name, file_name, prefix, suffix)