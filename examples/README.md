# 示例文件

此目录包含 Cinder 的示例文件。

## 文件

### `soul.md` 和 `soul.meta.yaml`

Cinder 生成的示例 soul 画像文件。这些展示了输出格式：

- `soul.md`: 人类可读的 soul 画像
- `soul.meta.yaml`: 机器可读的元数据

### `config.yaml`

显示所有可用设置的示例配置文件。

## 使用方法

生成你自己的 soul 画像：

```bash
cinder init
```

使用自定义配置：

```bash
# 复制示例配置到主目录
mkdir -p ~/.cinder
cp examples/config.yaml ~/.cinder/config.yaml

# 根据需要编辑
vim ~/.cinder/config.yaml
```
