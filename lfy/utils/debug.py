'错误缓存'
import logging


class InMemoryLogHandler(logging.Handler):
    """创建一个内存中的日志处理器

    Args:
        logging (_type_): _description_
    """

    def __init__(self, max_logs=20):
        super().__init__()
        self.log_buffer = []
        self.max_logs = max_logs

    def emit(self, record):
        log_entry = self.format(record)
        if len(self.log_buffer) >= self.max_logs:
            # 如果日志超过最大限制，删除最旧的日志
            self.log_buffer.pop(0)
        self.log_buffer.append(log_entry)

    def get_logs(self):
        """获取日志

        Returns:
            str: _description_
        """
        return "\n\n".join(self.log_buffer)


# 初始化日志系统
logger = logging.getLogger("lfy")
logger.setLevel(logging.DEBUG)

# 设置格式
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s\n[%(filename)s:%(lineno)d]\n%(message)s')
# 使用自定义内存日志处理器
in_memory_handler = InMemoryLogHandler(max_logs=10)
in_memory_handler.setFormatter(formatter)
logger.addHandler(in_memory_handler)

# 测试日志输出
# for i in range(15):
#     logger.info(f"Log message {i}")

# 打印当前的内存日志
# print("Current logs:")
# print(in_memory_handler.get_logs())


def get_logger():
    """提供给外部的接口

    Returns:
        _type_: _description_
    """
    return logger


def get_log_handler():
    """获取当前的内存日志

    Returns:
        _type_: _description_
    """
    return in_memory_handler
