from fastmcp import FastMCP

from backend.services.demand_service import (
    get_total_demand,
    get_top_products,
    get_store_demand,
)

mcp = FastMCP("Supply Chain Intelligence")


@mcp.tool
def total_demand():
    """Get total recorded demand from the database."""
    return get_total_demand()


@mcp.tool
def top_products(limit: int = 10):
    """Get top products based on demand."""
    return get_top_products(limit)


@mcp.tool
def store_demand():
    """Get demand grouped by store."""
    return get_store_demand()


if __name__ == "__main__":
    mcp.run(transport="stdio", log_level="ERROR")