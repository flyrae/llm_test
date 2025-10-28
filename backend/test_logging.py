"""测试日志功能"""
import logging
import sys

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("test")

logger.info("=" * 80)
logger.info("🚀 测试日志功能")
logger.info("这是一条INFO级别的日志")
logger.warning("这是一条WARNING级别的日志")
logger.error("这是一条ERROR级别的日志")
logger.info("=" * 80)

print("\n如果您能看到上面的日志输出，说明日志配置正常！")
