import streamlit as st

# إخفاء شريط الأدوات العائم وأيقونات Streamlit عن المستخدمين
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stToolbar {visibility: hidden;}
    [data-testid="stDecoration"] {display: none;}
    [data-testid="stStatusWidget"] {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# إعدادات الصفحة الأساسية
st.set_page_config(
    page_title="نظام الرصد الإعلامي الآلي والمتابعة الصحفية",
    page_icon="📰",
    layout="wide"
)

# عنوان النظام الرئيسي
st.markdown("""
    <div style="background-color: #0d2315; padding: 20px; border-radius: 10px; border: 1px solid #1e4d2b;">
        <h2 style="color: #ffffff; margin: 0; font-family: Tahoma, sans-serif;">المملكة العربية السعودية — المديرية العامة للجوازات</h2>
        <p style="color: #a3c1ad; margin: 5px 0 0 0; font-size: 14px;">نظام الرصد الإعلامي الآلي والمتابعة الصحفية</p>
    </div>
""", unsafe_allow_html=True)

st.write("")

# محتوى لوحة المؤشرات الرئيسية
st.markdown("### 📊 لوحة المؤشرات والتحليلات")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="إجمالي الأخبار المرصودة", value="1,245", delta="+12 اليوم")

with col2:
    st.metric(label="التغطيات الإيجابية", value="98%", delta="+1.5%")

with col3:
    st.metric(label="التقارير المرفوعة", value="48", delta="نشط")

st.markdown("---")

# قسم المحتوى التحليلي أو الجداول
st.info("💡 النظام يعمل بكفاءة وجاهز لاستعراض التقارير والبيانات المحدثة.")