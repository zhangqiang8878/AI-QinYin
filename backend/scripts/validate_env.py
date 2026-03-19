"""环境变量验证脚本 - 确保所有必需的配置项都已正确设置"""
import os
import re
from typing import List, Tuple

def validate_env_file(env_path: str = '.env') -> Tuple[List[str], List[str]]:
    """
    验证环境变量文件的完整性
    返回: (errors, warnings)
    """
    errors = []
    warnings = []

    required_vars = {
        # MongoDB
        'MONGODB_URI': r'mongodb://.+',
        'DATABASE_NAME': r'.+',

        # Redis
        'REDIS_HOST': r'.+',
        'REDIS_PORT': r'\d+',
        
        # JWT
        'JWT_SECRET': r'.{16,}',
        
        # Aliyun
        'SMS_ACCESS_KEY_ID': r'.+',
        'SMS_ACCESS_KEY_SECRET': r'.+',
        'OSS_ACCESS_KEY_ID': r'.+',
        'OSS_ACCESS_KEY_SECRET': r'.+',
        'OSS_BUCKET_NAME': r'.+',
        
        # WeChat
        'WECHAT_APPID': r'wx[0-9a-f]{16}',
        'WECHAT_MCH_ID': r'\d+',
        'WECHAT_API_KEY': r'.{32}',
        
        # TTS
        'TTS_SERVICE_URL': r'https?://.+'
    }

    env_vars = {}
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split('=', 1)
                    if len(parts) == 2:
                        env_vars[parts[0].strip()] = parts[1].strip()

    for var, pattern in required_vars.items():
        val = env_vars.get(var)
        if not val:
            errors.append(f"Missing required environment variable: {var}")
        elif not re.match(pattern, val):
            warnings.append(f"Environment variable {var} does not match expected format")

    return errors, warnings

if __name__ == "__main__":
    import sys
    env_file = sys.argv[1] if len(sys.argv) > 1 else '.env'
    print(f"Validating {env_file}...")
    errors, warnings = validate_env_file(env_file)
    
    for warning in warnings:
        print(f"WARNING: {warning}")
        
    for error in errors:
        print(f"ERROR: {error}")
        
    if errors:
        sys.exit(1)
    else:
        print("Validation passed!")