import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

# Add parent directory to sys.path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestInitDB:
    """测试MongoDB初始化脚本"""

    @pytest.mark.asyncio
    @patch('scripts.init_db.motor.motor_asyncio.AsyncIOMotorClient')
    async def test_create_indexes_success(self, mock_client_cls):
        """测试索引创建成功"""
        # 模拟数据库和集合
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_db = MagicMock()
        mock_client.__getitem__.return_value = mock_db
        
        mock_users = MagicMock()
        mock_voices = MagicMock()
        mock_subscriptions = MagicMock()
        mock_orders = MagicMock()
        mock_contents = MagicMock()

        mock_db.users = mock_users
        mock_db.voices = mock_voices
        mock_db.user_subscriptions = mock_subscriptions
        mock_db.orders = mock_orders
        mock_db.contents = mock_contents

        # 模拟create_index方法
        mock_users.create_index = AsyncMock()
        mock_voices.create_index = AsyncMock()
        mock_subscriptions.create_index = AsyncMock()
        mock_orders.create_index = AsyncMock()
        mock_contents.create_index = AsyncMock()

        from scripts.init_db import create_indexes
        await create_indexes()

        # 验证users集合索引被创建
        mock_users.create_index.assert_called()
        # 验证phone字段创建了唯一索引
        calls = [str(call) for call in mock_users.create_index.call_args_list]
        assert any('phone' in str(call) for call in calls)