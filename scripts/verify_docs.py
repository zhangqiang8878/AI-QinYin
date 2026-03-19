"""文档完整性验证脚本 - 确保部署文档包含所有必要信息"""
import os
import re
from pathlib import Path

def verify_deploy_doc():
    """验证部署文档的完整性"""
    doc_path = Path('docs/DEPLOY.md')
    errors = []
    warnings = []

    if not doc_path.exists():
        errors.append("部署文档不存在: docs/DEPLOY.md")
        return errors, warnings

    content = doc_path.read_text(encoding='utf-8')

    # 检查必需章节
    required_sections = [
        ('系统架构', r'##\s*系统架构'),
        ('部署步骤', r'##\s*部署步骤'),
        ('云端服务器部署', r'###\s*.*云端'),
        ('TTS服务部署', r'###\s*.*TTS|vllm'),
        ('微信小程序部署', r'###\s*.*微信'),
        ('配置检查清单', r'##\s*配置检查清单|检查清单'),
        ('监控与维护', r'##\s*监控|维护'),
        ('故障排查', r'##\s*故障排查|排查'),
    ]

    for section_name, pattern in required_sections:
        if not re.search(pattern, content, re.IGNORECASE):
            errors.append(f"缺少必需章节: {section_name}")

    # 检查关键命令示例
    command_checks = [
        ('Docker启动命令', r'docker\s+(run|build)'),
        ('环境变量示例', r'(MONGODB_URI|JWT_SECRET)\s*='),
        ('端口配置', r':\d{4,5}'),
    ]

    for check_name, pattern in command_checks:
        if not re.search(pattern, content):
            warnings.append(f"建议添加: {check_name}")

    return errors, warnings

def verify_env_example():
    """验证环境变量示例文件"""
    env_path = Path('backend/.env.example')
    errors = []
    warnings = []

    if not env_path.exists():
        errors.append("环境变量示例文件不存在: backend/.env.example")
        return errors, warnings

    content = env_path.read_text(encoding='utf-8')

    required_vars = [
        'MONGODB_URI', 'REDIS_HOST', 'JWT_SECRET',
        'SMS_ACCESS_KEY_ID', 'OSS_ACCESS_KEY_ID',
        'WECHAT_APPID', 'TTS_SERVICE_URL'
    ]

    for var in required_vars:
        if var not in content:
            errors.append(f".env.example缺少必需变量: {var}")

    return errors, warnings

def main():
    print("=" * 60)
    print("AI亲音文档完整性验证")
    print("=" * 60)

    all_errors = []
    all_warnings = []

    # 验证部署文档
    print("\n检查 docs/DEPLOY.md ...")
    errors, warnings = verify_deploy_doc()
    all_errors.extend(errors)
    all_warnings.extend(warnings)

    # 验证环境变量示例
    print("检查 backend/.env.example ...")
    errors, warnings = verify_env_example()
    all_errors.extend(errors)
    all_warnings.extend(warnings)

    if all_warnings:
        print("\n⚠️  警告:")
        for warning in all_warnings:
            print(f"  - {warning}")

    if all_errors:
        print("\n❌ 错误:")
        for error in all_errors:
            print(f"  - {error}")
        exit(1)
    else:
        print("\n✅ 所有文档验证通过!")
        exit(0)

if __name__ == '__main__':
    main()