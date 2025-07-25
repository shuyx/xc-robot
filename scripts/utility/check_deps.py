#!/usr/bin/env python3

required_packages = [
    "fastapi",
    "uvicorn", 
    "websockets",
    "pydantic",
    "multipart"  # python-multipart is imported as 'multipart'
]

missing = []
available = []

for package in required_packages:
    try:
        __import__(package)
        available.append(package)
        print(f"✅ {package} - 已安装")
    except ImportError:
        missing.append(package)
        print(f"❌ {package} - 未安装")

print(f"\n总结:")
print(f"已安装: {len(available)} 个")
print(f"缺失: {len(missing)} 个")

if missing:
    print(f"\n需要安装的包:")
    print(f"python3 -m pip install {' '.join(missing)}")