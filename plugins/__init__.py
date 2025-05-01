from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Type
import os
import importlib.util
from PySide6.QtWidgets import QMainWindow

class Plugin(ABC):
    """插件基类，所有插件必须继承此类"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """插件名称"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """插件描述"""
        pass
    
    @abstractmethod
    def initialize(self, window: QMainWindow) -> None:
        """初始化插件"""
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """清理插件资源"""
        pass

class PluginManager:
    """插件管理器，负责加载和管理插件"""
    
    def __init__(self, plugin_dir: str):
        self.plugin_dir = plugin_dir
        self.plugins: Dict[str, Plugin] = {}
        
        # 确保插件目录存在
        if not os.path.exists(plugin_dir):
            os.makedirs(plugin_dir)
    
    def discover_plugins(self) -> List[str]:
        """发现可用的插件"""
        plugin_files = []
        for file in os.listdir(self.plugin_dir):
            if file.endswith('.py') and not file.startswith('__'):
                plugin_files.append(os.path.splitext(file)[0])
        return plugin_files
    
    def load_plugin(self, plugin_name: str, window: QMainWindow) -> Optional[Plugin]:
        """加载单个插件"""
        if plugin_name in self.plugins:
            return self.plugins[plugin_name]
        
        plugin_path = os.path.join(self.plugin_dir, f'{plugin_name}.py')
        if not os.path.exists(plugin_path):
            return None
        
        try:
            # 动态导入插件模块
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
            if spec is None or spec.loader is None:
                return None
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 查找插件类（继承自Plugin的类）
            plugin_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, Plugin) and attr != Plugin:
                    plugin_class = attr
                    break
            
            if plugin_class is None:
                return None
            
            # 实例化插件并初始化
            plugin = plugin_class()
            plugin.initialize(window)
            self.plugins[plugin_name] = plugin
            return plugin
            
        except Exception as e:
            print(f'Failed to load plugin {plugin_name}: {str(e)}')
            return None
    
    def load_plugins(self, plugin_names: List[str], window: QMainWindow) -> None:
        """加载多个插件"""
        for name in plugin_names:
            self.load_plugin(name, window)
    
    def unload_plugin(self, plugin_name: str) -> None:
        """卸载插件"""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].cleanup()
            del self.plugins[plugin_name]
    
    def unload_all_plugins(self) -> None:
        """卸载所有插件"""
        for plugin_name in list(self.plugins.keys()):
            self.unload_plugin(plugin_name)