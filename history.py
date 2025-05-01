from typing import List, Optional
from config import Config

class History:
    """历史记录管理类，负责处理最近打开的文件历史"""
    
    def __init__(self, config: Config):
        self.config = config
        self._recent_files: List[str] = self.config.get_recent_files()
    
    @property
    def recent_files(self) -> List[str]:
        """获取最近打开的文件列表"""
        return self._recent_files
    
    def add_file(self, file_path: str) -> None:
        """添加文件到历史记录"""
        self.config.add_recent_file(file_path)
        self._recent_files = self.config.get_recent_files()
    
    def clear_history(self) -> None:
        """清空历史记录"""
        self._recent_files = []
        self.config.set_editor_setting('recent_files', '')