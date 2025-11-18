# 🏆 Олимпийский резерв - ИСПРАВЛЕННОЕ ПРИЛОЖЕНИЕ v5.1
# Исправлена ошибка с полем 'medal'
# Дата: 18 ноября 2025 г.

import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

# ===== КОНФИГУРАЦИЯ =====
st.set_page_config(
    page_title="🏆 Олимпийский резерв РФ",
    page_icon="🏆",
    layout="wide"
)

# ПРАВИЛЬНОЕ имя БД!
DB_NAME = 'app.db'

@st.cache_resource
def get_db_connection():
    """Подключение к БД"""
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        st.error(f"❌ Ошибка подключения: {e}")
        return None

@st.cache_data(ttl=3600)
def load_athletes():
    """Загрузить спортсменов"""
    try:
        conn = get_db_connection()
        if conn is None:
            return pd.DataFrame()
        df = pd.read_sql('SELECT * FROM athletes ORDER BY full_name', conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"❌ Ошибка загрузки спортсменов: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def load_competition_results():
    """Загрузить результаты"""
    try:
        conn = get_db_connection()
        if conn is None:
            return pd.DataFrame()
        df = pd.read_sql('''
            SELECT * FROM competition_results 
            ORDER BY competition_date DESC
        ''', conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"❌ Ошибка загрузки результатов: {e}")
        return pd.DataFrame()

# ===== АУТЕНТИФИКАЦИЯ =====

def authenticate(username, password):
    """Проверить учетные данные"""
    if username == 'admin' and password == 'admin123':
        return True
    return False

def login_page():
    """Страница входа"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("# 🏆 Олимпийский резерв")
        st.markdown("## Система управления спортсменами")
        st.markdown("---")
        
        with st.form("login_form"):
            username = st.text_input("👤 Логин")
            password = st.text_input("🔐 Пароль", type="password")
            submit = st.form_submit_button("Войти", use_container_width=True)
            
            if submit:
                if authenticate(username, password):
                    st.session_state.logged_in = True
                    st.success("✅ Вход выполнен!")
                    st.rerun()
                else:
                    st.error("❌ Неверные учетные данные")
    
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("📝 **Логин:** admin\n**Пароль:** admin123")

# ===== ГЛАВНАЯ ФУНКЦИЯ =====

def main():
    """Главное приложение"""
    
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        login_page()
    else:
        # Боковая панель
        with st.sidebar:
            st.title("🏆 Олимпийский резерв")
            page = st.radio("📊 Выберите страницу",
                           ["🏠 Главная", "👥 Спортсмены", 
                            "💼 Профиль", "📈 Результаты"])
            
            st.markdown("---")
            if st.button("🚪 Выход"):
                st.session_state.logged_in = False
                st.rerun()
        
        # Содержимое
        if page == "🏠 Главная":
            show_home()
        elif page == "👥 Спортсмены":
            show_athletes()
        elif page == "💼 Профиль":
            show_profile()
        elif page == "📈 Результаты":
            show_results()

def show_home():
    """Главная страница"""
    st.title("🏆 Главная")
    
    df = load_athletes()
    df_results = load_competition_results()
    
    if df.empty:
        st.warning("⚠️ БД не загружена. Проверьте файл app.db")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👥 Спортсменов", len(df))
    with col2:
        st.metric("🏅 Соревнований", len(df_results))
    with col3:
        avg_vo2 = df['vo2_max_ml_kg_min'].mean()
        st.metric("📈 Средний VO₂max", f"{avg_vo2:.1f}")
    with col4:
        # ИСПРАВЛЕНИЕ: проверка на наличие колонки 'medal'
        if not df_results.empty and 'medal' in df_results.columns:
            gold = len(df_results[df_results['medal'] == 'Золото'])
        else:
            gold = 0
        st.metric("🥇 Золотых медалей", gold)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        sport_counts = df['sport'].value_counts()
        fig = px.pie(values=sport_counts.values, names=sport_counts.index,
                    title="Распределение по видам спорта")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        gender_counts = df['gender'].value_counts()
        fig = px.bar(x=['Мужчины' if g == 'М' else 'Женщины' for g in gender_counts.index],
                    y=gender_counts.values, title="Распределение по полу")
        st.plotly_chart(fig, use_container_width=True)

def show_athletes():
    """Список спортсменов"""
    st.title("👥 Спортсмены")
    
    df = load_athletes()
    
    if df.empty:
        st.warning("⚠️ БД не загружена")
        return
    
    # Фильтры
    col1, col2 = st.columns(2)
    
    with col1:
        sports = ['Все'] + list(df['sport'].unique())
        selected_sport = st.selectbox("Вид спорта", sports)
    
    with col2:
        regions = ['Все'] + list(df['region'].unique())
        selected_region = st.selectbox("Регион", regions)
    
    # Фильтрация
    filtered_df = df.copy()
    if selected_sport != 'Все':
        filtered_df = filtered_df[filtered_df['sport'] == selected_sport]
    if selected_region != 'Все':
        filtered_df = filtered_df[filtered_df['region'] == selected_region]
    
    # Таблица
    display_df = filtered_df[['full_name', 'gender', 'age', 'sport', 'region', 'vo2_max_ml_kg_min']].copy()
    display_df.columns = ['ФИО', 'Пол', 'Возраст', 'Вид спорта', 'Регион', 'VO₂max']
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    st.write(f"**Всего:** {len(filtered_df)} спортсменов")

def show_profile():
    """Профиль спортсмена"""
    st.title("💼 Профиль")
    
    df = load_athletes()
    
    if df.empty:
        st.warning("⚠️ БД не загружена")
        return
    
    athlete_options = [f"{row['full_name']}" for _, row in df.iterrows()]
    selected = st.selectbox("Выберите спортсмена", athlete_options)
    
    athlete = df[df['full_name'] == selected].iloc[0]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📋 Информация")
        st.write(f"**ФИО:** {athlete['full_name']}")
        st.write(f"**Возраст:** {athlete['age']} лет")
        st.write(f"**Пол:** {'Мужской' if athlete['gender'] == 'М' else 'Женский'}")
        st.write(f"**Регион:** {athlete['region']}")
    
    with col2:
        st.subheader("💪 Антропометрия")
        st.write(f"**Рост:** {athlete['height_cm']} см")
        st.write(f"**Вес:** {athlete['weight_kg']} кг")
        st.write(f"**Жировая ткань:** {athlete['body_fat_percent']}%")
        st.write(f"**Мышечная масса:** {athlete['muscle_mass_percent']}%")
    
    with col3:
        st.subheader("🏃 Показатели")
        st.write(f"**VO₂max:** {athlete['vo2_max_ml_kg_min']}")
        st.write(f"**ЧСС покоя:** {athlete['resting_heart_rate_bpm']}")
        st.write(f"**ЧСС макс:** {athlete['heart_rate_peak_bpm']}")
        st.write(f"**Опыт:** {athlete['training_experience_years']} лет")

def show_results():
    """Результаты соревнований"""
    st.title("📈 Результаты")
    
    df = load_athletes()
    df_results = load_competition_results()
    
    if df.empty or df_results.empty:
        st.warning("⚠️ Данные не загружены")
        return
    
    athlete_options = [f"{row['full_name']}" for _, row in df.iterrows()]
    selected = st.selectbox("Выберите спортсмена", athlete_options)
    
    athlete = df[df['full_name'] == selected].iloc[0]
    athlete_results = df_results[df_results['athlete_id'] == athlete['athlete_id']].copy()
    
    if athlete_results.empty:
        st.info("ℹ️ Результатов нет")
        return
    
    athlete_results['competition_date'] = pd.to_datetime(athlete_results['competition_date'])
    athlete_results = athlete_results.sort_values('competition_date', ascending=False)
    
    st.subheader(f"Результаты {selected}")
    
    display_results = athlete_results[['competition_date', 'distance_km', 'finish_position']].head(20).copy()
    
    # ИСПРАВЛЕНИЕ: добавить колонку medal если она есть
    if 'medal' in athlete_results.columns:
        display_results['medal'] = athlete_results['medal'].head(20).values
        display_results.columns = ['Дата', 'Дистанция', 'Место', 'Медаль']
    else:
        display_results.columns = ['Дата', 'Дистанция', 'Место']
    
    st.dataframe(display_results, use_container_width=True, hide_index=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.line(athlete_results, x='competition_date', y='finish_position',
                     title='Динамика позиций', markers=True)
        fig.update_layout(yaxis_autorange='reversed')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # ИСПРАВЛЕНИЕ: проверка на наличие колонки
        if 'medal' in athlete_results.columns:
            medal_counts = athlete_results['medal'].value_counts()
            if not medal_counts.empty:
                fig = px.pie(values=medal_counts.values, names=medal_counts.index, title='Медали')
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Информация о медалях недоступна")

if __name__ == "__main__":
    main()