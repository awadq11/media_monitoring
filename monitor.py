import sqlite3
import feedparser
from database import get_db_connection

# استعلامات دقيقة وموجهة تشمل الجوازات، المقيمين، وزارة الداخلية، وقيادتنا الرشيدة
TARGET_QUERIES = [
    "المديرية العامة للجوازات السعودية",
    "وزارة الداخلية السعودية",
    "وزیر الداخلية السعودي",
    "خادم الحرمين الشريفين الملك سلمان بن عبدالعزيز",
    "ولي العهد الأمير محمد بن سلمان",
    "مخالفي نظام الإقامة والعمل السعودية",
    "خدمات أبشر ومقيم السعودية",
    "تأشيرة الخروج النهائي والعودة السعودية"
]

# كلمات إجبارية لضمان ارتباط الخبر حصرياً بالجهات والقيادة والشأن المحلي المستهدف
OBLIGATORY_KEYWORDS = [
    "الجوازات", "إقامة", "الإقامة", "تأشيرة", "خروج وعودة", 
    "خروج نهائي", "مقيمي", "مخالفي", "أبشر", "مقيم", 
    "وزارة الداخلية", "الداخلية", "الملك سلمان", "ولي العهد", 
    "محمد بن سلمان", "وزير الداخلية"
]

# استبعاد أي أخبار خارجية أو لا تخص المملكة والقطاعات المستهدفة
EXCLUDED_KEYWORDS = [
    "الكويت", "مصر", "الإمارات", "قطر", "البحرين", "عمان", "الأردن", 
    "العراق", "سوريا", "لبنان", "المغرب", "تونس", "الجزائر", "السودان", 
    "اليمن", "كينيا", "كوريا", "أوروبا", "فرنسا", "فيتنام", "بيراميدز"
]

def classify_news(title):
    """تصنيف الخبر تلقائياً بناءً على محتوى العنوان والشأن المرصود"""
    if any(k in title for k in ["الملك سلمان", "ولي العهد", "محمد بن سلمان"]):
        return "القام السامية الكريمة"
    elif any(k in title for k in ["وزارة الداخلية", "وزير الداخلية", "الأمن العام", "شرطة"]):
        return "وزارة الداخلية والقيادة الأمنية"
    elif any(k in title for k in ["مخالفي", "أمن الحدود", "ضبط", "ترحيل", "مخالف"]):
        return "ضبط أمني ومخالفو الإقامة"
    elif any(k in title for k in ["أبشر", "مقيم", "إلكترونية", "خدمات", "تجديد"]):
        return "الخدمات الإلكترونية (أبشر/مقيم)"
    elif any(k in title for k in ["الجوازات", "مدير عام الجوازات", "تأشيرة", "إقامة"]):
        return "شؤون الجوازات والمقيمين"
    else:
        return "أخبار عامة ورسمية"

def fetch_and_store_rss(custom_url=None):
    conn, cursor = get_db_connection()
    added_count = 0
    
    queries_to_fetch = [custom_url] if custom_url and custom_url != "https://news.google.com/rss?hl=ar&gl=SA&ceid=SA:ar" else [
        f"https://news.google.com/rss/search?q={q.replace(' ', '%20')}%20when:2d&hl=ar&gl=SA&ceid=SA:ar" for q in TARGET_QUERIES
    ]
    
    for url in queries_to_fetch:
        print(f"جاري جلب الأخبار: {url}")
        feed = feedparser.parse(url)
        
        for entry in feed.entries:
            title = entry.get('title', '')
            link = entry.get('link', '')
            published = entry.get('published', '')
            
            # 1. استبعاد الدول والجهات الخارجية
            if any(ex in title for ex in EXCLUDED_KEYWORDS):
                continue
                
            # 2. التأكد من ارتباط الخبر بأحد الموضوعات المستهدفة حصرياً
            if not any(req in title for req in OBLIGATORY_KEYWORDS):
                continue
            
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO news (title, link, published_date)
                    VALUES (?, ?, ?)
                ''', (title, link, published))
                if cursor.rowcount > 0:
                    added_count += 1
            except Exception as e:
                print(f"خطأ أثناء الحفظ: {e}")
                
    conn.commit()
    conn.close()
    print(f"تمت إضافة {added_count} خبر جديد معتمد بنجاح.")

if __name__ == "__main__":
    fetch_and_store_rss()