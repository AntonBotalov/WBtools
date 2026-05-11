import streamlit as st
import pandas as pd
import zipfile
from io import BytesIO
import matplotlib.pyplot as plt

st.set_page_config(page_title="Аналитика брендов", layout="wide")
st.title('📊 Аналитика по брендам')

uploaded_files = st.file_uploader("Загрузите .zip файл", type='zip', accept_multiple_files=True)

if uploaded_files:
    all_data = []
    for file in uploaded_files:
        with zipfile.ZipFile(BytesIO(file.read())) as z:
            excel_file = [f for f in z.namelist() if f.endswith('.xlsx')][0]
            with z.open(excel_file) as f:
                df = pd.read_excel(f)

        # Выбираем нужные колонки + Обоснование для фильтрации возвратов
        cols = [
            'Бренд', 
            'К перечислению Продавцу за реализованный Товар', 
            'Услуги по доставке товара покупателю',
            'Обоснование для оплаты'
        ]
        df = df[cols].copy()
        
        df.rename(columns={
            'К перечислению Продавцу за реализованный Товар': 'Сумма_исх',
            'Услуги по доставке товара покупателю': 'Доставка'
        }, inplace=True)

        # Разделяем на Продажи и Возвраты
        # К перечислению — только когда продажа
        df['К перечислению'] = df.apply(
            lambda x: x['Сумма_исх'] if 'Продажа' in str(x['Обоснование для оплаты']) else 0, axis=1
        )
        # Возвраты — только когда возврат
        df['Возвраты'] = df.apply(
            lambda x: x['Сумма_исх'] if 'Возврат' in str(x['Обоснование для оплаты']) else 0, axis=1
        )

        all_data.append(df)

    result_df = pd.concat(all_data)
    
    # Группируем данные
    summary_df = result_df.groupby('Бренд', as_index=False).agg({
        'К перечислению': 'sum',
        'Возвраты': 'sum',
        'Доставка': 'sum'
    })

    # Твоя логика налога (не трогаем): 7% от колонки К перечислению
    summary_df['Налог 7%'] = summary_df['К перечислению'] * 0.07
    
    # Итого теперь учитывает вычет возвратов
    # (Сумма - 7%) - Доставка - Возвраты
    summary_df['Итого'] = (summary_df['К перечислению'] * 0.93) - summary_df['Доставка'] - summary_df['Возвраты']

    # Форматирование для отображения
    display_df = summary_df.copy()
    for col in ['К перечислению', 'Возвраты', 'Доставка', 'Налог 7%', 'Итого']:
        display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}".replace('.', ','))

    st.data_editor(display_df, use_container_width=True, hide_index=True)

    # Круговая диаграмма
    st.subheader("🟢 Доля брендов по перечислению (без учета возвратов)")
    numeric_df = summary_df.groupby('Бренд')['К перечислению'].sum()
    
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
