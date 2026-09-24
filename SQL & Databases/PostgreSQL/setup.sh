sudo service postgresql start

sudo service postgresql status

sudo -i -u postgres psql

الأمر,الوظيفة
l\,عرض كافة قواعد البيانات (Databases) الموجودة في السيرفر.
c database_name\,الانتقال والاتصال بقاعدة بيانات معينة.
dt\,عرض كل الجداول (Tables) في قاعدة البيانات الحالية.
d table_name\,عرض تفاصيل جدول معين (الأعمدة، أنواع البيانات، المفتات الأساسية PK).
du\,عرض جميع المستخدمين (Users) والصلاحيات الممنوحة لهم.
dn\,عرض الـ Schemas الموجودة داخل قاعدة البيانات.
q\,الخروج من شاشة PostgreSQL للـ Termina