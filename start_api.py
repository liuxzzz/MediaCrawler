#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FastAPI 服务启动脚本
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8001,
        reload=True,  # 开发模式下自动重载
        log_level="info"
    )

