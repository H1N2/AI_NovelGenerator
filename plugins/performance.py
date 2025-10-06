# plugins/performance.py
"""
插件性能监控
监控插件的执行时间、内存使用等性能指标
"""

import time
import psutil
import threading
import logging
from typing import Dict, List, Any, Optional
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class PerformanceRecord:
    """性能记录"""
    plugin_name: str
    operation: str
    start_time: float
    end_time: float
    execution_time: float
    memory_before: float
    memory_after: float
    memory_delta: float
    cpu_usage: float = 0.0  # CPU使用率
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass 
class ResourceLimits:
    """资源限制配置"""
    max_execution_time: float = 30.0  # 最大执行时间(秒)
    max_memory_mb: float = 100.0      # 最大内存使用(MB)
    max_cpu_percent: float = 50.0     # 最大CPU使用率(%)
    max_calls_per_minute: int = 1000  # 每分钟最大调用次数
    enabled: bool = True


class PluginPerformanceMonitor:
    """插件性能监控器"""
    
    def __init__(self, max_records: int = 1000):
        self.max_records = max_records
        self._records: deque = deque(maxlen=max_records)
        self._service_stats: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))
        self._resource_limits: Dict[str, ResourceLimits] = {}
        self._call_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))  # 调用历史
        self._lock = threading.Lock()
        self._logger = logging.getLogger("plugin_performance")
        
        # 默认资源限制
        self._default_limits = ResourceLimits()
        
    def set_plugin_limits(self, plugin_name: str, limits: ResourceLimits):
        """设置插件资源限制"""
        with self._lock:
            self._resource_limits[plugin_name] = limits
            self._logger.info(f"为插件 {plugin_name} 设置资源限制: {limits}")
            
    def get_plugin_limits(self, plugin_name: str) -> ResourceLimits:
        """获取插件资源限制"""
        with self._lock:
            return self._resource_limits.get(plugin_name, self._default_limits)
            
    def start_monitoring(self, plugin_name: str, operation: str) -> 'PerformanceContext':
        """开始监控操作"""
        # 检查调用频率限制
        if not self._check_call_rate_limit(plugin_name):
            raise RuntimeError(f"插件 {plugin_name} 超过调用频率限制")
        return PerformanceContext(self, plugin_name, operation)
    
    def _check_call_rate_limit(self, plugin_name: str) -> bool:
        """检查调用频率限制"""
        limits = self.get_plugin_limits(plugin_name)
        if not limits.enabled:
            return True
        
        with self._lock:
            now = datetime.now()
            call_history = self._call_history[plugin_name]
            
            # 清理一分钟前的调用记录
            cutoff_time = now - timedelta(minutes=1)
            while call_history and call_history[0] < cutoff_time:
                call_history.popleft()
            
            # 检查是否超过限制
            if len(call_history) >= limits.max_calls_per_minute:
                self._logger.warning(f"插件 {plugin_name} 超过调用频率限制: {len(call_history)}/{limits.max_calls_per_minute}")
                return False
            
            # 记录本次调用
            call_history.append(now)
            return True
        
    def record_service_call(self, plugin_name: str, service_name: str, execution_time: float):
        """记录服务调用性能"""
        with self._lock:
            self._service_stats[plugin_name][service_name].append(execution_time)
            
            # 保持最近100次记录
            if len(self._service_stats[plugin_name][service_name]) > 100:
                self._service_stats[plugin_name][service_name] = \
                    self._service_stats[plugin_name][service_name][-100:]
                    
    def add_record(self, record: PerformanceRecord):
        """添加性能记录"""
        with self._lock:
            self._records.append(record)
            
    def get_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        with self._lock:
            stats = {
                'total_records': len(self._records),
                'plugins': {},
                'service_calls': {}
            }
            
            # 按插件统计
            plugin_stats = defaultdict(lambda: {
                'total_calls': 0,
                'total_time': 0.0,
                'avg_time': 0.0,
                'max_time': 0.0,
                'min_time': float('inf'),
                'memory_usage': []
            })
            
            for record in self._records:
                plugin_name = record.plugin_name
                plugin_stats[plugin_name]['total_calls'] += 1
                plugin_stats[plugin_name]['total_time'] += record.execution_time
                plugin_stats[plugin_name]['max_time'] = max(
                    plugin_stats[plugin_name]['max_time'], record.execution_time
                )
                plugin_stats[plugin_name]['min_time'] = min(
                    plugin_stats[plugin_name]['min_time'], record.execution_time
                )
                plugin_stats[plugin_name]['memory_usage'].append(record.memory_delta)
                
            # 计算平均值
            for plugin_name, data in plugin_stats.items():
                if data['total_calls'] > 0:
                    data['avg_time'] = data['total_time'] / data['total_calls']
                    data['avg_memory'] = sum(data['memory_usage']) / len(data['memory_usage'])
                if data['min_time'] == float('inf'):
                    data['min_time'] = 0.0
                    
            stats['plugins'] = dict(plugin_stats)
            
            # 服务调用统计
            for plugin_name, services in self._service_stats.items():
                stats['service_calls'][plugin_name] = {}
                for service_name, times in services.items():
                    if times:
                        stats['service_calls'][plugin_name][service_name] = {
                            'count': len(times),
                            'avg_time': sum(times) / len(times),
                            'max_time': max(times),
                            'min_time': min(times),
                            'total_time': sum(times)
                        }
                        
            return stats
            
    def check_resource_limits(self, plugin_name: str, execution_time: float, 
                            memory_usage: float, cpu_usage: float = 0.0) -> List[str]:
        """检查资源限制违规"""
        violations = []
        limits = self.get_plugin_limits(plugin_name)
        
        if not limits.enabled:
            return violations
        
        if execution_time > limits.max_execution_time:
            violations.append(f"执行时间超限: {execution_time:.2f}s > {limits.max_execution_time}s")
            
        if memory_usage > limits.max_memory_mb:
            violations.append(f"内存使用超限: {memory_usage:.2f}MB > {limits.max_memory_mb}MB")
            
        if cpu_usage > limits.max_cpu_percent:
            violations.append(f"CPU使用率超限: {cpu_usage:.1f}% > {limits.max_cpu_percent}%")
            
        return violations
        
    def get_recent_records(self, plugin_name: Optional[str] = None, 
                          limit: int = 50) -> List[PerformanceRecord]:
        """获取最近的性能记录"""
        with self._lock:
            records = list(self._records)
            
        if plugin_name:
            records = [r for r in records if r.plugin_name == plugin_name]
            
        return records[-limit:]
        
    def clear_stats(self):
        """清空统计数据"""
        with self._lock:
            self._records.clear()
            self._service_stats.clear()


class PerformanceContext:
    """性能监控上下文管理器"""
    
    def __init__(self, monitor: PluginPerformanceMonitor, plugin_name: str, operation: str):
        self.monitor = monitor
        self.plugin_name = plugin_name
        self.operation = operation
        self.start_time = 0
        self.memory_before = 0
        
    def __enter__(self):
        self.start_time = time.time()
        process = psutil.Process()
        self.memory_before = process.memory_info().rss / 1024 / 1024  # MB
        # 记录开始时的CPU使用率
        psutil.cpu_percent()  # 第一次调用初始化
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = time.time()
        execution_time = end_time - self.start_time
        
        process = psutil.Process()
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_delta = memory_after - self.memory_before
        cpu_usage = psutil.cpu_percent()  # 获取CPU使用率
        
        record = PerformanceRecord(
            plugin_name=self.plugin_name,
            operation=self.operation,
            start_time=self.start_time,
            end_time=end_time,
            execution_time=execution_time,
            memory_before=self.memory_before,
            memory_after=memory_after,
            memory_delta=memory_delta,
            cpu_usage=cpu_usage
        )
        
        self.monitor.add_record(record)
        
        # 检查资源限制
        violations = self.monitor.check_resource_limits(
            self.plugin_name, execution_time, memory_after, cpu_usage
        )
        
        if violations:
            logger = logging.getLogger("plugin_performance")
            logger.warning(f"插件 {self.plugin_name} 资源限制违规: {'; '.join(violations)}")
            
# 在文件末尾添加全局实例和装饰器

# 全局性能监控器实例
_performance_monitor = None

def get_performance_monitor() -> PluginPerformanceMonitor:
    """获取全局性能监控器实例"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PluginPerformanceMonitor()
    return _performance_monitor

def monitor_plugin_call(plugin_name: str, operation: str = "call"):
    """插件调用监控装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            monitor = get_performance_monitor()
            with monitor.start_monitoring(plugin_name, operation):
                return func(*args, **kwargs)
        return wrapper
    return decorator