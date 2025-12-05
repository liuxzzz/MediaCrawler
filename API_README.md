# MediaCrawler API 服务使用指南

## 快速开始

### 启动服务

```bash
# 方式1: 使用启动脚本
python start_api.py

# 方式2: 直接使用 uvicorn
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

服务启动后，访问以下地址：
- API 文档: http://localhost:8000/docs
- 交互式 API 文档: http://localhost:8000/redoc
- 健康检查: http://localhost:8000/health

## API 接口说明

### 1. 启动爬虫任务

**接口**: `POST /api/v1/crawler/start`

**请求体示例**:
```json
{
  "platform": "xhs",
  "login_type": "qrcode",
  "crawler_type": "search",
  "keywords": "编程副业,编程兼职",
  "start_page": 1,
  "get_comment": true,
  "get_sub_comment": false,
  "save_data_option": "json",
  "cookies": ""
}
```

**参数说明**:
- `platform`: 媒体平台 (xhs/dy/ks/bili/wb/tieba/zhihu)
- `login_type`: 登录方式 (qrcode/phone/cookie)
- `crawler_type`: 爬虫类型 (search/detail/creator)
- `keywords`: 关键词，多个用逗号分隔
- `start_page`: 起始页码，默认为 1
- `get_comment`: 是否爬取一级评论，默认为 true
- `get_sub_comment`: 是否爬取二级评论，默认为 false
- `save_data_option`: 数据保存方式 (csv/db/json/sqlite/mongodb/excel)，默认为 json
- `cookies`: Cookie 登录方式使用的 Cookie 值

**响应示例**:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "爬虫任务已启动",
  "created_at": "2025-01-27T10:00:00"
}
```

### 2. 查询任务状态

**接口**: `GET /api/v1/tasks/{task_id}`

**响应示例**:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "platform": "xhs",
  "crawler_type": "search",
  "keywords": "编程副业,编程兼职",
  "created_at": "2025-01-27T10:00:00",
  "completed_at": null,
  "error": null
}
```

**任务状态说明**:
- `pending`: 等待中
- `running`: 运行中
- `completed`: 已完成
- `failed`: 失败

### 3. 列出所有任务

**接口**: `GET /api/v1/tasks?limit=50&skip=0`

**查询参数**:
- `limit`: 返回任务数量，默认为 50
- `skip`: 跳过任务数量，默认为 0

### 4. 初始化数据库

**接口**: `POST /api/v1/db/init?db_type=sqlite`

**查询参数**:
- `db_type`: 数据库类型 (sqlite/mysql)

### 5. 获取支持的平台列表

**接口**: `GET /api/v1/platforms`

**响应示例**:
```json
{
  "platforms": [
    {"value": "xhs", "name": "小红书"},
    {"value": "dy", "name": "抖音"},
    {"value": "ks", "name": "快手"},
    {"value": "bili", "name": "哔哩哔哩"},
    {"value": "wb", "name": "微博"},
    {"value": "tieba", "name": "百度贴吧"},
    {"value": "zhihu", "name": "知乎"}
  ]
}
```

## 使用示例

### 使用 curl

```bash
# 启动爬虫任务
curl -X POST "http://localhost:8000/api/v1/crawler/start" \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "xhs",
    "keywords": "编程副业",
    "crawler_type": "search"
  }'

# 查询任务状态
curl "http://localhost:8000/api/v1/tasks/{task_id}"

# 列出所有任务
curl "http://localhost:8000/api/v1/tasks"
```

### 使用 Python requests

```python
import requests

# 启动爬虫任务
response = requests.post(
    "http://localhost:8000/api/v1/crawler/start",
    json={
        "platform": "xhs",
        "keywords": "编程副业",
        "crawler_type": "search"
    }
)
task = response.json()
task_id = task["task_id"]

# 查询任务状态
status_response = requests.get(
    f"http://localhost:8000/api/v1/tasks/{task_id}"
)
print(status_response.json())
```

## 注意事项

1. 爬虫任务在后台异步执行，启动接口会立即返回任务ID
2. 任务状态会实时更新，可以通过查询接口获取最新状态
3. 如果任务失败，错误信息会保存在 `error` 字段中
4. 建议在生产环境中使用 Redis 或数据库来存储任务状态，而不是内存字典
5. 确保已正确配置相关平台的登录信息（Cookie 或二维码登录）

## 开发建议

1. 生产环境部署时，建议使用进程管理器（如 supervisor、systemd）来管理服务
2. 可以添加认证和授权机制来保护 API
3. 可以添加任务队列（如 Celery）来更好地管理并发任务
4. 可以添加日志记录和监控功能

