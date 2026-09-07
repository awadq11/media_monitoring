import streamlit as st
import pandas as pd
import os
import base64
import streamlit.components.v1 as components
from database import get_db_connection, init_db
from monitor import fetch_and_store_rss, classify_news

init_db()

st.set_page_config(
    page_title="نظام الرصد الإعلامي | المديرية العامة للجوازات", 
    page_icon="🛡️", 
    layout="wide"
)

# كود جافا سكريبت لإزالة شارة Streamlit والشارة العائمة نهائياً من DOM الصفحة
components.html(
    """
    <script>
    const hideBadge = () => {
        try {
            const body = window.parent.document.body;
            const badges = body.querySelectorAll('a[href*="streamlit.cloud"], div[class*="viewerBadge"], [data-testid="stStatusWidget"], footer, [data-testid="stFooter"]');
            badges.forEach(el => el.remove());
        } catch(e) {}
    };
    setInterval(hideBadge, 100);
    </script>
    """,
    height=0,
)

# كود CSS الشامل لإخفاء شريط الأدوات والعناصر الافتراضية
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;900&display=swap');
    html, body, [class*="css"] { font-family: 'Tajawal', sans-serif; }
    
    header [kind="header"] { display: none !important; }
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important; display: none !important;}
    [data-testid="stFooter"] {display: none !important; visibility: hidden !important;}
    .stToolbar {visibility: hidden !important; display: none !important;}
    [data-testid="stDecoration"] {display: none !important;}
    [data-testid="stStatusWidget"] {visibility: hidden !important; display: none !important;}
    
    [data-testid="stSidebar"] { background-color: #121816; border-left: 1px solid #1f2c27; }
    .main-title { text-align: center; color: #ffffff; font-weight: 900; font-size: 2.2rem; padding: 10px 0; }
    .sub-banner { background: linear-gradient(135deg, #1B3B2B 0%, #0d1e15 100%); padding: 20px; border-radius: 12px; border: 1px solid #28543d; margin-bottom: 25px; text-align: center; color: #f0f4f1; }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    if os.path.exists("images.png"):
        col_img1, col_img2, col_img3 = st.columns([1, 2, 1])
        with col_img2:
            st.image("images.png")
            
    st.markdown("<h3 style='text-align: center; color: #4CAF50; font-size: 1.2rem; margin-top: 5px;'>لوحة التحكم والعمليات</h3>", unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("⚡ **إدارة ورصد المصادر**")
    if st.button("بدء الرصد الآلي الشامل", use_container_width=True, type="primary"):
        with st.spinner("جاري جلب وتصنيف أحدث أخبار الجوازات..."):
            fetch_and_store_rss()
            st.session_state['last_fetch_time'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        st.success("تم تحديث الرصد بنجاح!")
        st.rerun()

    if 'last_fetch_time' in st.session_state:
        st.caption(f"🕒 آخر تحديث: {st.session_state['last_fetch_time']}")
    else:
        st.caption("🕒 آخر تحديث: لم يتم الرصد بهذه الجلسة بعد")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("🎯 **فلاتر التقرير المتقدمة**")
    filter_option = st.selectbox(
        "التصنيف الموضوعي:", 
        [
            "الكل (جميع الأخبار المرصودة)", 
            "المقام السامي الكريم", 
            "وزارة الداخلية والقيادة الأمنية", 
            "شؤون الجوازات والمقيمين", 
            "الخدمات الإلكترونية (أبشر/مقيم)", 
            "ضبط أمني ومخالفو الإقامة"
        ],
        label_visibility="collapsed"
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("🛠️ **إدارة قاعدة البيانات**")
    if st.button("🗑️ تفريغ كافة الأخبار (بدء من جديد)", use_container_width=True):
        conn, cursor = get_db_connection()
        cursor.execute("DELETE FROM news")
        conn.commit()
        conn.close()
        st.success("تم مسح كافة البيانات بنجاح!")
        st.rerun()

    st.markdown("---")

conn, cursor = get_db_connection()
query = "SELECT title, link, published_date FROM news ORDER BY id DESC"
df = pd.read_sql(query, conn)
conn.close()

if not df.empty:
    df['source'] = df['title'].apply(lambda x: x.split(' - ')[-1] if ' - ' in x else 'مصدر رسمي')
    df['clean_title'] = df['title'].apply(lambda x: ' - '.join(x.split(' - ')[:-1]) if ' - ' in x else x)
    df['classification'] = df['clean_title'].apply(classify_news)
    df['datetime_parsed'] = pd.to_datetime(df['published_date'], errors='coerce')

    if filter_option == "المقام السامي الكريم":
        df = df[df['classification'] == "القام السامية الكريمة"]
    elif filter_option == "وزارة الداخلية والقيادة الأمنية":
        df = df[df['classification'] == "وزارة الداخلية والقيادة الأمنية"]
    elif filter_option == "شؤون الجوازات والمقيمين":
        df = df[df['classification'] == "شؤون الجوازات والمقيمين"]
    elif filter_option == "الخدمات الإلكترونية (أبشر/مقيم)":
        df = df[df['classification'] == "الخدمات الإلكترونية (أبشر/مقيم)"]
    elif filter_option == "ضبط أمني ومخالفو الإقامة":
        df = df[df['classification'] == "ضبط أمني ومخالفو الإقامة"]

    with st.sidebar:
        st.markdown("📅 **فلترة حسب الفترة الزمنية**")
        valid_dates = df['datetime_parsed'].dropna()
        if not valid_dates.empty:
            min_date = valid_dates.min().date()
            max_date = valid_dates.max().date()
            start_date = st.date_input("من تاريخ:", value=min_date, min_value=min_date, max_value=max_date)
            end_date = st.date_input("إلى تاريخ:", value=max_date, min_value=min_date, max_value=max_date)
            df = df[(df['datetime_parsed'].dt.date >= start_date) & (df['datetime_parsed'].dt.date <= end_date)]

with st.sidebar:
    st.markdown("---")
    with st.expander("❓ عن البرنامج والنظام"):
        st.markdown("* النظام: نظام الرصد الإعلامي الآلي\n* الإصدار: 3.0\n* الدعم: Awadh Alqarni 0599815775")

st.markdown("""
    <div class="sub-banner">
        <h2 style="margin:0; font-size: 1.8rem; color: #ffffff;">المملكة العربية السعودية — وزارة الداخلية</h2>
        <h1 class="main-title" style="margin: 5px 0 0 0;">المديرية العامة للجوازات</h1>
        <p style="margin: 5px 0 0 0; color: #b0c4b8; font-size: 0.95rem;">نظام الرصد الإعلامي الآلي والمتابعة الصحفية للقطاع</p>
    </div>
""", unsafe_allow_html=True)

if not df.empty:
    st.markdown("🔍 **البحث السريع في النتائج المرصودة:**")
    search_query = st.text_input("بحث برمز أو كلمة مفتاحية...", label_visibility="collapsed")
    if search_query:
        df = df[df['clean_title'].str.contains(search_query, case=False, na=False)]

col_m1, col_m2 = st.columns([2, 5])
with col_m1:
    st.metric(label="📊 إجمالي الأخبار المرصودة", value=len(df))

st.markdown("---")

if not df.empty:
    display_df = pd.DataFrame({
        'عنوان الخبر': df['clean_title'],
        'التصنيف': df['classification'],
        'مصدر الخبر': df['source'],
        'تاريخ النشر': df['published_date'],
        'رابط الخبر': df['link']
    })
    
    st.data_editor(
        display_df,
        column_config={
            "عنوان الخبر": st.column_config.TextColumn("عنوان الخبر", width="large"),
            "التصنيف": st.column_config.TextColumn("التصنيف الموضوعي", width="medium"),
            "مصدر الخبر": st.column_config.TextColumn("مصدر الخبر", width="small"),
            "تاريخ النشر": st.column_config.TextColumn("تاريخ النشر", width="small"),
            "رابط الخبر": st.column_config.LinkColumn("رابط الخبر", display_text="🔗 فتح الرابط", width="small")
        },
        hide_index=True,
        use_container_width=True
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("📌 استعراض تفاصيل وخيارات خبر محدد"):
        selected_title = st.selectbox("اختر الخبر للاطلاع على تفاصيله:", display_df['عنوان الخبر'].tolist())
        matched_row = display_df[display_df['عنوان الخبر'] == selected_title].iloc[0]
        st.markdown(f"**العنوان الكامل:** {matched_row['عنوان الخبر']}")
        st.markdown(f"**التصنيف:** `{matched_row['التصنيف']}`")
        st.markdown(f"**المصدر:** `{matched_row['مصدر الخبر']}` | **التاريخ:** `{matched_row['تاريخ النشر']}`")
        st.markdown(f"[🔗 رابط المصدر]({matched_row['رابط الخبر']})")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📥 تصدير التقارير الرسمية المعتمدة")
    
    export_col1, export_col2 = st.columns(2)
    with export_col1:
        csv_data = display_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📊 تحميل التقرير (Excel / CSV)", data=csv_data, file_name="Passports_Media_Report.csv", mime="text/csv", use_container_width=True)
        
    logo_base64 = ""
    if os.path.exists("images.png"):
        with open("images.png", "rb") as img_file:
            logo_base64 = base64.b64encode(img_file.read()).decode("utf-8")

    with export_col2:
        html_report = f"""<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><title>تقرير الجوازات</title></head><body><h2>المديرية العامة للجوازات - التقرير الإعلامي</h2><table><tr><th>العنوان</th><th>التصنيف</th><th>مصدر الخبر</th></tr>"""
        for _, row in display_df.iterrows():
            html_report += f"<tr><td>{row['عنوان الخبر']}</td><td>{row['التصنيف']}</td><td>{row['مصدر الخبر']}</td></tr>"
        html_report += "</table></body></html>"
        
        st.download_button("📄 تحميل التقرير الرسمي (HTML / طباعة)", data=html_report, file_name="Report.html", mime="application/html", use_container_width=True)
else:
    st.warning("⚠️ لا توجد أخبار مرصودة حالياً.")