# fairino package
# FR3机械臂控制SDK

from .Robot import RPC

# 创建Robot类包装器以保持向后兼容
class Robot:
    RPC = RPC

__all__ = ['Robot', 'RPC']