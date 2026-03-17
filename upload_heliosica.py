#!/usr/bin/env python3
import os
"""HELIOSICA Upload v1.0.0 - باستخدام نفس الأسلوب المجرب من TSU-WAVE"""

import requests
import hashlib
import os
import glob
import sys


print("="*60)
print("☀️ HELIOSICA v1.0.0 Upload - PyPI")
print("="*60)
print("📋 DOI: 10.5281/zenodo.19042948")
print("="*60)

# التأكد من وجود المجلد
if not os.path.exists('dist'):
    os.makedirs('dist')
    print("📁 تم إنشاء مجلد dist")

# قراءة README.md
try:
    with open('README.md', 'r', encoding='utf-8') as f:
        readme = f.read()
    print(f"📄 README.md: {len(readme)} حرف")
except FileNotFoundError:
    print("❌ ملف README.md غير موجود")
    sys.exit(1)

# البحث عن ملفات التوزيع
wheel_files = glob.glob("dist/*.whl")
tar_files = glob.glob("dist/*.tar.gz")

if not wheel_files and not tar_files:
    print("\n📦 لا توجد ملفات توزيع. جاري بناء الحزمة...")
    os.system("python -m build")
    
    # البحث مرة أخرى
    wheel_files = glob.glob("dist/*.whl")
    tar_files = glob.glob("dist/*.tar.gz")

if not wheel_files and not tar_files:
    print("❌ فشل بناء الحزمة")
    sys.exit(1)

print(f"\n📦 الملفات الموجودة:")
for f in wheel_files + tar_files:
    size = os.path.getsize(f) / 1024
    print(f"   • {os.path.basename(f)} ({size:.1f} KB)")

# رفع كل ملف
success_count = 0
for filepath in wheel_files + tar_files:
    filename = os.path.basename(filepath)
    print(f"\n📤 رفع: {filename}")

    # تحديد نوع الملف
    if filename.endswith('.tar.gz'):
        filetype = 'sdist'
        pyversion = 'source'
    else:
        filetype = 'bdist_wheel'
        pyversion = 'py3'

    # حساب الهاشات
    with open(filepath, 'rb') as f:
        content = f.read()
    md5_hash = hashlib.md5(content).hexdigest()
    sha256_hash = hashlib.sha256(content).hexdigest()

    # بيانات الرفع
    data = {
        ':action': 'file_upload',
        'metadata_version': '2.1',
        'name': 'heliosica',
        'version': '1.0.0',
        'filetype': filetype,
        'pyversion': pyversion,
        'md5_digest': md5_hash,
        'sha256_digest': sha256_hash,
        'description': readme,
        'description_content_type': 'text/markdown',
        'author': 'Samir Baladi',
        'author_email': 'gitdeeper@gmail.com',
        'license': 'MIT',
        'summary': 'HELIOSICA: Nine Parameters to Decode the Solar Wind and Shield Our Digital World',
        'home_page': 'https://heliosica.netlify.app',
        'project_url': 'https://github.com/gitdeeper9/heliosica',
        'requires_python': '>=3.9',
        'keywords': 'space-weather, heliophysics, cme, solar-wind, geomagnetic-storm, kp-index, dst-index, dbm, gssi, magnetopause, forbush-decrease'
    }

    # رفع الملف
    with open(filepath, 'rb') as f:
        response = requests.post(
            'https://upload.pypi.org/legacy/',
            files={'content': (filename, f, 'application/octet-stream')},
            data=data,
            auth=('__token__', TOKEN),
            timeout=60,
            headers={'User-Agent': 'HELIOSICA-Uploader/1.0'}
        )

    print(f"   الحالة: {response.status_code}")

    if response.status_code == 200:
        print("   ✅✅✅ تم الرفع بنجاح!")
        success_count += 1
    else:
        print(f"   ❌ خطأ: {response.text[:200]}")

print("\n" + "="*60)
print(f"📊 تم رفع {success_count} من {len(wheel_files) + len(tar_files)} ملف بنجاح")
print("🔗 https://pypi.org/project/heliosica/1.0.0/")
print("📦 pip install heliosica")
print("="*60)
