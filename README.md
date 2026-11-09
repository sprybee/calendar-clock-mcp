# Calendar Clock MCP

一个无密钥、只读的日期时间 MCP 服务，使用 Python 标准库处理时区和日历计算，不联网、不写入持久化数据。

## 工具

- `convert_timezone`：将带明确偏移的 ISO 8601 时间转换为 IANA 时区。
- `date_difference`：计算两个 `YYYY-MM-DD` 日期的有符号日差。
- `count_business_days`：按周一至周五计算 `[start_date, end_date)` 的工作日，可排除指定节假日；不推断国家节假日或调休。
- `unix_timestamp_to_datetime`：Unix 秒时间戳转 ISO 时间。
- `date_to_unix_timestamp`：带明确时区偏移的 ISO 时间转 Unix 秒时间戳。

服务入口为 `calendar_clock_mcp.server:mcp`，平台自动托管为无状态 Streamable HTTP，无需自行启动 HTTP 服务。

## 示例

```json
{"iso_datetime":"2026-01-01T00:00:00Z","target_timezone":"Asia/Shanghai"}
```

## 本地开发

```bash
pip install -e ".[dev]"
pytest -q
```
