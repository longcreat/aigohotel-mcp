from mcp.server.fastmcp import FastMCP
import httpx
import os
from typing import Optional, Annotated
from datetime import datetime
from pydantic import Field

mcp = FastMCP("AigoHotel Search", json_response=True)

API_BASE_URL = "https://travelportal-api-staging.aigohotel.com/api/mcp/hotelsearch"
API_KEY = os.getenv("AIGOHOTEL_API_KEY", "")

@mcp.tool()
async def search_hotels(
    place: Annotated[str, Field(description="地点名称(支持城市、景点、酒店、交通枢纽、地标和具体地址等)")],
    placeType: Annotated[str, Field(description="地点的类型(支持以下类型: 城市、区/县、机场、景点、火车站、地铁站、酒店、具体地址)")],
    originalQuery: Annotated[Optional[str], Field(description="用户的原始问询句")] = None,
    checkIn: Annotated[Optional[str], Field(description="入住日期,如: 2025-10-01,未填写时默认为次日")] = None,
    stayNights: Annotated[int, Field(description="入住天数,未填写时默认为1天")] = 1,
    starRatings: Annotated[Optional[list[float]], Field(description="酒店星级(0.0-5.0,梯度为0.5),默认3星以上,例如[4.5, 5.0]、[0.0, 2.0]")] = None,
    adultCount: Annotated[int, Field(description="每间房入住的成人数量,默认两成人")] = 2,
    distanceInMeter: Annotated[int, Field(description="直线距离,单位(米),当地点是一个POI位置时生效,生效时默认值为5000")] = 5000,
    size: Annotated[int, Field(description="返回酒店结果数量,默认5个酒店,最大不超过10个")] = 10,
    withHotelAmenities: Annotated[bool, Field(description="是否包含酒店设施")] = True,
    withRoomAmenities: Annotated[bool, Field(description="是否包含客房设施")] = True,
    language: Annotated[str, Field(description="当前语言环境,如: zh_CN, en_US等,默认zh_CN")] = "zh_CN",
    queryParsing: Annotated[bool, Field(description="是否对用户的提问询语句进行分析得到用户的需求倾向性,默认为true")] = True
) -> dict:
    """
    查询海外酒店信息。支持按指定的地点类型查询酒店。
    
    Args:
        place: 目的地(支持城市、景点、酒店、交通枢纽、地标和具体地址等)
        placeType: 目的地类型(默认: 城市、机场、火车站、火车站、火车站、酒店、景点、区域)
        originalQuery: 用户的原始问询句
        checkIn: 期望入住时间,格式为yyyy-MM-dd,默认次日
        stayNights: 入住晚数(默认为1晚)
        starRatings: 酒店星级(0.0-5.0,梯度为0.5),默认[0.0, 5.0],例如[4.5, 5.0]、[0.0, 2.0]
        adultCount: 每间房入住的成人数量,默认两成人
        distanceInMeter: 直线距离,单位(米),当地点是一个景点位置时生效,生效时默认值为5000
        size: 返回酒店结果数量,默认10个酒店,最大不超过20个
        withHotelAmenities: 是否包含酒店设施,默认true
        withRoomAmenities: 是否包含客房设施,默认true
        language: 当前语言环境,如: zh_CN, en_US等,默认zh_CN
        queryParsing: 是否对用户的提问询语句进行分析得到用户的需求倾向性,默认为true
    
    Returns:
        符合条件的酒店列表的JSON字符串
        
    Examples:
        1. 搜索西雅图的酒店可以传入: {"place":"西雅图","placeType":"城市"}
        2. 搜索2026年1月1日金汉宫附近酒店可以传入: {"place":"白金汉宫","placeType":"景点","checkIn":"2026-01-01"}
    """
    
    params = {
        "place": place,
        "placeType": placeType,
        "stayNights": stayNights,
        "adultCount": adultCount,
        "distanceInMeter": distanceInMeter,
        "size": size,
        "withHotelAmenities": withHotelAmenities,
        "withRoomAmenities": withRoomAmenities,
        "language": language,
        "queryParsing": queryParsing
    }
    
    if originalQuery:
        params["originalQuery"] = originalQuery
    
    if checkIn:
        params["checkIn"] = checkIn
    
    if starRatings:
        params["starRatings"] = starRatings
    
    headers = {
        "Content-Type": "application/json"
    }
    
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.post(API_BASE_URL, json=params, headers=headers)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        raise Exception(f"HTTP请求失败: {str(e)}")
    except Exception as e:
        raise Exception(f"查询酒店失败: {str(e)}")

if __name__ == "__main__":
    if not API_KEY:
        print("警告: 未配置 AIGOHOTEL_API_KEY")
    elif not API_KEY.startswith("mcp_"):
        print("警告: API Key 格式错误,应以 'mcp_' 开头")
    
    mcp.run(transport="streamable-http")
