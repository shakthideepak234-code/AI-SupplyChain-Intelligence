from backend.services.demand_service import get_top_products


def get_inventory_risk():
    products = get_top_products(limit=20)

    if not products:
        return []

    demands = [int(p["total_units_sold"]) for p in products]
    threshold = sum(demands) / len(demands)

    results = []

    for product in products:
        demand = int(product["total_units_sold"])

        risk = "HIGH" if demand >= threshold else "MODERATE"

        results.append({
            "item_id": product["item_id"],
            "total_demand": demand,
            "risk_level": risk
        })

    return results


if __name__ == "__main__":
    for item in get_inventory_risk():
        print(item)