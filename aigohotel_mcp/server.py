from mcp.server.fastmcp import FastMCP
import httpx
import os
from typing import Optional, Annotated
from pydantic import Field
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

mcp = FastMCP("AigoHotel Search")

API_BASE_URL = "https://mcp.aigohotel.com/mcp/hotelsearch"
API_KEY = os.getenv("AIGOHOTEL_API_KEY", "")

@mcp.tool(name="searchHotels")
async def search_hotels(
    originQuery: Annotated[str, Field(description="用户的提问语句")],
    place: Annotated[str, Field(description="地点名称，尽可能详细，带上国家城市，例如：北京、上海浦东国际机场、迪士尼乐园等")],
    placeType: Annotated[str, Field(description="地点的类型（支持以下类型：城市、机场、景点、火车站、地铁站、酒店、区/县）")],
    queryParsing: Annotated[bool, Field(description="是否对用户的提问语句进行分析得到用户的需求倾向性")] = True,
    adultCount: Annotated[int, Field(description="每间房入住的成人数量，默认两成人")] = 2,
    checkIn: Annotated[Optional[str], Field(description="入住日期，如：2025-10-01，未填写时默认日期为次日")] = None,
    countryCode: Annotated[Optional[str], Field(description="国家三字码（例如：CHN）")] = None,
    distanceInMeter: Annotated[int, Field(description="直线距离，单位（米），当地点是一个POI位置时生效，生效时默认设定值为5000")] = 5000,
    language: Annotated[str, Field(description="当前语言环境，如：zh_CN，en_US等，默认zh_CN")] = "zh_CN",
    size: Annotated[int, Field(description="返回酒店结果数量，默认10个酒店，最大不超过20个")] = 10,
    starRatings: Annotated[Optional[list[float]], Field(description="酒店星级(0.0-5.0, 梯度为0.5)，默认[0.0, 5.0]，例如 [4.5, 5.0]，[0.0, 2.0]")] = None,
    stayNights: Annotated[int, Field(description="入住天数，未填写时默认1天")] = 1,
    withHotelAmenities: Annotated[bool, Field(description="是否包含酒店设施")] = True,
    withRoomAmenities: Annotated[bool, Field(description="是否包含房间设施")] = True
) -> dict:
    """
    该工具用于查询全球酒店信息，支持筛选条件搜索酒店。
    """
    params = {
        "place": place,
        "placeType": placeType,
        "originQuery": originQuery,
        "queryParsing": queryParsing,
        "adultCount": adultCount,
        "stayNights": stayNights,
        "distanceInMeter": distanceInMeter,
        "size": size,
        "withHotelAmenities": withHotelAmenities,
        "withRoomAmenities": withRoomAmenities,
        "language": language
    }
    
    if checkIn:
        params["checkIn"] = checkIn
    
    if countryCode:
        params["countryCode"] = countryCode
    
    if starRatings:
        params["starRatings"] = starRatings
    
    headers = {
        "Content-Type": "application/json"
    }
    
    if API_KEY:
        # 处理 API_KEY 可能已包含 Bearer 前缀的情况
        auth_value = API_KEY.strip()
        if auth_value.startswith("Bearer "):
            headers["Authorization"] = auth_value
        else:
            headers["Authorization"] = f"Bearer {auth_value}"
    
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.post(API_BASE_URL, json=params, headers=headers)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        status_code = e.response.status_code if hasattr(e, 'response') else "Unknown"
        raise Exception(f"HTTP请求失败 (状态码: {status_code}): {str(e)}")
    except Exception as e:
        raise Exception(f"查询酒店失败: {str(e)}")

def main():
    if not API_KEY:
        print("警告: 未配置 AIGOHOTEL_API_KEY")
    elif not API_KEY.startswith("mcp_"):
        print("警告: API Key 格式错误,应以 'mcp_' 开头")
    
    mcp.run(transport="streamable-http")

if __name__ == "__main__":
    main()
