# 测试文件夹

这个文件夹包含了项目的所有测试文件。

## 文件结构

```
tests/
├── __init__.py          # 测试模块初始化文件
├── README.md            # 本说明文件
└── test_config.py       # 配置系统测试
```

## 运行测试

### 配置系统测试

```bash
# 在项目根目录下运行
cd tests
python test_config.py

# 或者从项目根目录直接运行
python tests/test_config.py
```

### 测试说明

- **test_config.py**: 测试配置系统的加载、验证和修改功能
  - 验证配置文件是否能正确加载
  - 测试配置参数的访问和修改
  - 验证配置验证机制是否正常工作

## 添加新测试

当添加新的测试文件时，请遵循以下规范：

1. 文件名以 `test_` 开头
2. 在文件开头添加项目根目录到Python路径：
   ```python
   import sys
   from pathlib import Path
   
   # 添加项目根目录到Python路径
   project_root = Path(__file__).parent.parent
   sys.path.insert(0, str(project_root))
   ```
3. 使用相对于项目根目录的路径引用配置文件和其他资源
4. 添加适当的日志记录和错误处理

## 注意事项

- 所有测试文件都应该能够独立运行
- 测试文件不应该修改项目的实际配置文件
- 如果需要临时文件，请在测试结束后清理