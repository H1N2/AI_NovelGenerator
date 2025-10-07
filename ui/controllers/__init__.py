"""
控制器模块
实现MVP架构中的Presenter层，负责协调Model和View之间的交互
"""

from .base_controller import BaseController, ControllerRegistry
from .novel_controller import NovelController
from .config_controller import ConfigController
from .generation_controller import GenerationController

__all__ = [
    'BaseController',
    'ControllerRegistry', 
    'NovelController',
    'ConfigController',
    'GenerationController'
]