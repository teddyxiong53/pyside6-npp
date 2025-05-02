import json
import os
from typing import List, Optional

class History:
    """历史记录管理类，负责处理最近打开的文件历史"""
    
    def __init__(self, history_file: str = '.recent_files'):
        self.history_file = history_file
        self._recent_files: List[str] = []
        self.load_history()
    
    def load_history(self) -> None:
        """从隐藏文件加载历史记录"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self._recent_files = json.load(f)
            except json.JSONDecodeError:
                self._recent_files = []
    
    def save_history(self) -> None:
        """保存历史记录到隐藏文件"""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self._recent_files, f, ensure_ascii=False)
    
    @property
    def recent_files(self) -> List[str]:
        """获取最近打开的文件列表"""
        return self._recent_files
    
    def add_file(self, file_path: str) -> None:
        """添加文件到历史记录"""
        if not file_path:
            return
            
        # 如果文件已在列表中，先移除
        if file_path in self._recent_files:
            self._recent_files.remove(file_path)
        
        # 添加到列表开头
        self._recent_files.insert(0, file_path)
        
        # 保持最多10个记录
        self._recent_files = self._recent_files[:10]
        
        # 保存到文件
        self.save_history()
    
    def clear_history(self) -> None:
        """清空历史记录"""
        self._recent_files = []
        self.save_history()