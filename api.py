# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1
#


"""
FastAPI 服务入口文件
提供 HTTP API 接口
"""

from fastapi import FastAPI
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="MediaCrawler API",
    description="媒体爬虫 API 服务",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CrawlerTaskRequest(BaseModel):
    """爬虫任务请求模型"""
    keywords: str = Field(..., description="关键词")
    star_count: int = Field(default=50, description="星级")


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy"}

@app.post("/api/v1/crawler/task",  tags=["爬虫任务"])
async def create_crawler_task(
    request: CrawlerTaskRequest,
):
    """创建爬虫任务"""
    star_count = request.star_count 
    keywords = request.keywords

    print(f"star_count: {star_count}, keywords: {keywords}")

    # 创建爬虫任务  
    
    return {"status": "ok", "message": "爬虫任务创建成功"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
