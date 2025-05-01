import os
import configparser
from typing import List, Optional

class Config:
    """配置管理类，负责读写npp.ini文件"""
    
    def __init__(self, config_file: str = 'npp.ini'):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.load_config()
    
    def load_config(self) -> None:
        """加载配置文件，如果不存在则创建默认配置"""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file, encoding='utf-8')
        else:
            self._create_default_config()
    
    def _create_default_config(self) -> None:
        """创建默认配置"""
        # 编辑器设置
        self.config['Editor'] = {
            'font_family': 'Monospace',
            'font_size': '12',
            'tab_size': '4',
            'show_whitespace': 'true',
            'whitespace_color': '#E8E8E8'
        }
        
        # 最近文件历史
        self.config['History'] = {
            'recent_files': ''
        }
        
        # 插件设置
        self.config['Plugins'] = {
            'enabled_plugins': ''
        }
        
        self.save_config()
    
    def save_config(self) -> None:
        """保存配置到文件"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            self.config.write(f)
    
    def get_editor_setting(self, key: str, default: str = '') -> str:
        """获取编辑器设置"""
        return self.config.get('Editor', key, fallback=default)
    
    def set_editor_setting(self, key: str, value: str) -> None:
        """设置编辑器配置"""
        if 'Editor' not in self.config:
            self.config['Editor'] = {}
        self.config['Editor'][key] = value
        self.save_config()
    
    def get_recent_files(self) -> List[str]:
        """获取最近打开的文件列表"""
        files = self.config.get('History', 'recent_files', fallback='')
        return files.split('|') if files else []
    
    def add_recent_file(self, file_path: str) -> None:
        """添加文件到最近打开列表"""
        files = self.get_recent_files()
        
        # 如果文件已在列表中，先移除
        if file_path in files:
            files.remove(file_path)
        
        # 添加到列表开头
        files.insert(0, file_path)
        
        # 保持最多5个记录
        files = files[:5]
        
        # 保存到配置
        self.config['History']['recent_files'] = '|'.join(files)
        self.save_config()
    
    def get_enabled_plugins(self) -> List[str]:
        """获取已启用的插件列表"""
        plugins = self.config.get('Plugins', 'enabled_plugins', fallback='')
        return plugins.split('|') if plugins else []
    
    def set_enabled_plugins(self, plugins: List[str]) -> None:
        """设置启用的插件列表"""
        self.config['Plugins']['enabled_plugins'] = '|'.join(plugins)
        self.save_config()