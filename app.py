import streamlit as st
import pandas as pd
import zipfile
from io import BytesIO
import matplotlib.pyplot as plt

st.title('📊 Аналитика по брендам')

uploaded_files = st.file_uploader("Загрузите .zip файл", type='zip', accept_multiple_files=True)

if uploaded_files:
    all_data = []
    for file in uploaded_files:
        with zipfile.ZipFile(BytesIO(file.read())) as z:
            excel_file = [f for f in z.namelist() if f.endswith('.xlsx')][0]
            with z.open(excel_file) as f:
                df = pd.read_excel(f)

        df = df[['Бренд', 'К перечислению Продавцу за реализованный Товар', 'Услуги по доставке товара покупателю']]
        df.rename(columns={
            'К перечислению Продавцу за реализованный Товар': 'К перечислению',
            'Услуги по доставке товара покупателю': 'Доставка'
        }, inplace=True)

        all_data.append(df)

    result_df = pd.concat(all_data)
    summary_df = result_df.groupby('Бренд', as_index=False).agg({
        'К перечислению': 'sum',
        'Доставка': 'sum'
    })

    summary_df['Итого'] = summary_df['К перечислению'] - summary_df['Доставка']
    
    summary_df['Итого -7%'] = summary_df['Итого'] * 0.93


    for col in ['К перечислению', 'Доставка', 'Итого', 'Итого -7%']:
        summary_df[col] = summary_df[col].apply(lambda x: f"{x:.2f}".replace('.', ','))

    

    st.data_editor(summary_df, use_container_width=True, hide_index=True)

    # Круговая диаграмма по брендам (по "К перечислению")
    st.subheader("🟢 Доля брендов по перечислению")
    numeric_df = result_df.groupby('Бренд')['К перечислению'].sum()
    fig, ax = plt.subplots(facecolor='black')
    ax.set_facecolor('black')
    wedges, texts, autotexts = ax.pie(
        numeric_df,
        labels=numeric_df.index,
        autopct='%1.1f%%',
        startangle=90,
        textprops={'color': 'white'}
    )
    for text in texts + autotexts:
        text.set_color('white')
    ax.axis('equal')
    st.pyplot(fig)

else:
    st.info('Загрузите отчёт для отображения данных.')
