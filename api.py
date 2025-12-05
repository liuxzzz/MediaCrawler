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

import asyncio
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware

import config
from database import db
from database.db_session import get_async_engine, create_tables
from base.base_crawler import AbstractCrawler
from media_platform.xhs import XiaoHongShuCrawler
from var import crawler_type_var, min_star_count_var

app = FastAPI(
    title="MediaCrawler API",
    description="媒体爬虫 API 服务",
    version="1.0.0"
)


@app.on_event("startup")
async def startup_event():
    """服务启动时初始化数据库连接"""
    if config.SAVE_DATA_OPTION == "pgsql":
        try:
            print(f"[API] Initializing PostgreSQL connection...")
            # 创建数据库（如果不存在）
            await db.init_db("pgsql")
            # 创建表结构
            await create_tables("pgsql")
            # 获取引擎以测试连接
            engine = get_async_engine("pgsql")
            if engine:
                from sqlalchemy import text
                async with engine.connect() as conn:
                    await conn.execute(text("SELECT 1"))
                print(f"[API] PostgreSQL connection established successfully")
        except Exception as e:
            print(f"[API] Failed to initialize PostgreSQL: {e}")
            raise

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 存储当前任务的 star_count，用于过滤
current_task_star_count: Optional[int] = None


class CrawlerTaskRequest(BaseModel):
    """爬虫任务请求模型"""
    keywords: str = Field(..., description="关键词")
    star_count: int = Field(default=50, description="星级")


class CrawlerFactory:
    """爬虫工厂类"""
    CRAWLERS = {
        "xhs": XiaoHongShuCrawler,
    }

    @staticmethod
    def create_crawler(platform: str = "xhs") -> AbstractCrawler:
        crawler_class = CrawlerFactory.CRAWLERS.get(platform)
        if not crawler_class:
            raise ValueError(f"Invalid Media Platform: {platform}")
        return crawler_class()


async def run_crawler_task(keywords: str, star_count: int):
    """运行爬虫任务的异步函数"""
    global current_task_star_count
    
    try:
        # 设置过滤条件
        current_task_star_count = star_count
        min_star_count_var.set(star_count)
        
        # 设置配置参数
        original_keywords = config.KEYWORDS
        original_platform = config.PLATFORM
        original_crawler_type = config.CRAWLER_TYPE
        original_save_data_option = config.SAVE_DATA_OPTION
        
        config.PLATFORM = "xhs"
        config.KEYWORDS = keywords
        config.CRAWLER_TYPE = "search"
        # 保持原有的数据保存选项（如果启动时配置了 pgsql，这里会保持使用 pgsql）
        config.SAVE_DATA_OPTION = original_save_data_option
        crawler_type_var.set("search")
        
        # 创建并启动爬虫
        crawler = CrawlerFactory.create_crawler(platform="xhs")
        await crawler.start()
        
        # 清理资源
        await cleanup_crawler(crawler)
        
        # 恢复原始配置
        config.KEYWORDS = original_keywords
        config.PLATFORM = original_platform
        config.CRAWLER_TYPE = original_crawler_type
        config.SAVE_DATA_OPTION = original_save_data_option
        
    except Exception as e:
        print(f"[API] Crawler task failed: {e}")
        raise
    finally:
        current_task_star_count = None
        # 重置过滤条件
        try:
            min_star_count_var.set(0)
        except Exception:
            pass


async def cleanup_crawler(crawler: AbstractCrawler):
    """清理爬虫资源"""
    try:
        # 检查并清理CDP浏览器
        if hasattr(crawler, 'cdp_manager') and crawler.cdp_manager:
            try:
                await crawler.cdp_manager.cleanup(force=True)
            except Exception as e:
                error_msg = str(e).lower()
                if "closed" not in error_msg and "disconnected" not in error_msg:
                    print(f"[API] 清理CDP浏览器时出错: {e}")
        
        # 检查并清理标准浏览器上下文
        elif hasattr(crawler, 'browser_context') and crawler.browser_context:
            try:
                if hasattr(crawler.browser_context, 'pages'):
                    await crawler.browser_context.close()
            except Exception as e:
                error_msg = str(e).lower()
                if "closed" not in error_msg and "disconnected" not in error_msg:
                    print(f"[API] 关闭浏览器上下文时出错: {e}")
        
        # 关闭数据库连接
        if config.SAVE_DATA_OPTION in ["db", "sqlite", "pgsql"]:
            await db.close()
    except Exception as e:
        print(f"[API] 清理资源时出错: {e}")


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy"}


@app.post("/api/v1/crawler/task", tags=["爬虫任务"])
async def create_crawler_task(
    request: CrawlerTaskRequest,
):
    """创建爬虫任务"""
    star_count = request.star_count
    keywords = request.keywords
    
    print(f"[API] Starting crawler task - keywords: {keywords}, star_count: {star_count}")
    
    try:
        # 同步执行爬虫任务，等待任务完成
        await run_crawler_task(keywords, star_count)
        
        return {
            "status": "ok",
            "message": "爬虫任务已完成",
            "keywords": keywords,
            "star_count": star_count
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"爬虫任务执行失败: {str(e)}",
            "keywords": keywords,
            "star_count": star_count
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
