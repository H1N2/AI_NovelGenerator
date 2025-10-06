# plugins/communicator.py
"""
插件通信器
支持插件间的服务调用和数据交换
"""

import json
import logging
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class ServiceCall:
    """服务调用记录"""
    caller: str
    target: str
    service: str
    args: List[Any]
    kwargs: Dict[str, Any]
    timestamp: datetime
    result: Optional[Any] = None
    error: Optional[str] = None


class PluginCommunicator:
    """插件通信器"""
    
    def __init__(self, plugin_manager):
        self.plugin_manager = plugin_manager
        self.logger = logging.getLogger("plugin_communicator")
        self._call_history: List[ServiceCall] = []
        self._max_history = 1000
        
    def call_service(self, caller_name: str, target_plugin: str, 
                    service_name: str, *args, **kwargs) -> Any:
        """调用插件服务"""
        call_record = ServiceCall(
            caller=caller_name,
            target=target_plugin,
            service=service_name,
            args=list(args),
            kwargs=kwargs,
            timestamp=datetime.now()
        )
        
        try:
            result = self.plugin_manager.call_plugin_service(
                target_plugin, service_name, *args, **kwargs
            )
            call_record.result = result
            self._add_call_record(call_record)
            return result
            
        except Exception as e:
            call_record.error = str(e)
            self._add_call_record(call_record)
            self.logger.error(f"服务调用失败 {caller_name} -> {target_plugin}.{service_name}: {e}")
            raise
            
    def broadcast_data(self, sender: str, data_type: str, data: Any):
        """广播数据给所有插件"""
        event_name = f"data_broadcast_{data_type}"
        event_data = {
            'sender': sender,
            'data_type': data_type,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        
        self.plugin_manager.emit_event(event_name, event_data)
        
    def send_data(self, sender: str, target: str, data_type: str, data: Any):
        """发送数据给特定插件"""
        event_name = f"data_message_{target}"
        event_data = {
            'sender': sender,
            'target': target,
            'data_type': data_type,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        
        self.plugin_manager.emit_event(event_name, event_data)
        
    def serialize_data(self, data: Any) -> str:
        """序列化数据"""
        try:
            if isinstance(data, (dict, list, str, int, float, bool)) or data is None:
                return json.dumps(data, ensure_ascii=False, indent=2)
            elif hasattr(data, '__dict__'):
                # 对象转字典
                return json.dumps(data.__dict__, ensure_ascii=False, indent=2)
            elif hasattr(data, '_asdict'):
                # namedtuple
                return json.dumps(data._asdict(), ensure_ascii=False, indent=2)
            else:
                # 其他类型转字符串
                return str(data)
        except Exception as e:
            self.logger.warning(f"数据序列化失败: {e}")
            return str(data)
            
    def deserialize_data(self, data_str: str, expected_type: Optional[type] = None) -> Any:
        """反序列化数据"""
        try:
            data = json.loads(data_str)
            
            if expected_type and hasattr(expected_type, '__annotations__'):
                # 尝试转换为指定类型（简单实现）
                if hasattr(expected_type, '__init__'):
                    try:
                        return expected_type(**data) if isinstance(data, dict) else expected_type(data)
                    except:
                        pass
                        
            return data
        except json.JSONDecodeError:
            return data_str
        except Exception as e:
            self.logger.warning(f"数据反序列化失败: {e}")
            return data_str
            
    def validate_data_format(self, data: Any, schema: Dict[str, Any]) -> bool:
        """验证数据格式（简单实现）"""
        try:
            if not isinstance(schema, dict):
                return True
                
            required_fields = schema.get('required', [])
            properties = schema.get('properties', {})
            
            if isinstance(data, dict):
                # 检查必需字段
                for field in required_fields:
                    if field not in data:
                        return False
                        
                # 检查字段类型
                for field, field_schema in properties.items():
                    if field in data:
                        expected_type = field_schema.get('type')
                        if expected_type:
                            if not self._check_type(data[field], expected_type):
                                return False
                                
            return True
            
        except Exception as e:
            self.logger.warning(f"数据格式验证失败: {e}")
            return False
            
    def _check_type(self, value: Any, expected_type: str) -> bool:
        """检查值类型"""
        type_mapping = {
            'string': str,
            'integer': int,
            'number': (int, float),
            'boolean': bool,
            'array': list,
            'object': dict,
            'null': type(None)
        }
        
        expected_python_type = type_mapping.get(expected_type)
        if expected_python_type:
            return isinstance(value, expected_python_type)
        return True
        
    def _add_call_record(self, record: ServiceCall):
        """添加调用记录"""
        self._call_history.append(record)
        if len(self._call_history) > self._max_history:
            self._call_history = self._call_history[-self._max_history:]
            
    def get_call_history(self, caller: Optional[str] = None, 
                        target: Optional[str] = None, limit: int = 50) -> List[ServiceCall]:
        """获取调用历史"""
        history = self._call_history
        
        if caller:
            history = [call for call in history if call.caller == caller]
        if target:
            history = [call for call in history if call.target == target]
            
        return history[-limit:]
        
    def get_communication_stats(self) -> Dict[str, Any]:
        """获取通信统计"""
        stats = {
            'total_calls': len(self._call_history),
            'successful_calls': len([call for call in self._call_history if call.error is None]),
            'failed_calls': len([call for call in self._call_history if call.error is not None]),
            'plugins': {},
            'services': {}
        }
        
        # 按插件统计
        for call in self._call_history:
            # 调用者统计
            if call.caller not in stats['plugins']:
                stats['plugins'][call.caller] = {'outgoing': 0, 'incoming': 0}
            stats['plugins'][call.caller]['outgoing'] += 1
            
            # 目标插件统计
            if call.target not in stats['plugins']:
                stats['plugins'][call.target] = {'outgoing': 0, 'incoming': 0}
            stats['plugins'][call.target]['incoming'] += 1
            
            # 服务统计
            service_key = f"{call.target}.{call.service}"
            if service_key not in stats['services']:
                stats['services'][service_key] = {'calls': 0, 'errors': 0}
            stats['services'][service_key]['calls'] += 1
            if call.error:
                stats['services'][service_key]['errors'] += 1
                
        return stats