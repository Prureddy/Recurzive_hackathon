import json
import requests

# Structure payload.
payload = {
    'source': 'amazon_search',
    'domain': 'in',
    'query': 'Pet Foods',
    'parse': True,
}

# Get response.
response = requests.request(
    'POST',
    'https://realtime.oxylabs.io/v1/queries',
    auth=('pruthvis_Rjyt6', '_Szp5DLwLS5Ea_J'),
    json=payload,
)

# Ensure response is successful.
if response.status_code == 200:
    product_data = response.json()
    
    # Check if 'data' key exists and has items.
    if 'data' in product_data and isinstance(product_data['data'], list) and len(product_data['data']) > 0:
        filtered_products = []

        # Filter and structure desired product data.
        for product in product_data['data']:
            # Check if all required fields are present
            if all(field in product for field in ['pos', 'url', 'asin', 'price', 'title', 'rating', 'currency', 'is_prime', 'url_image', 'best_seller', 'price_upper', 'is_sponsored', 'manufacturer', 'sales_volume', 'pricing_count', 'reviews_count', 'is_amazons_choice', 'price_strikethrough', 'shipping_information']):
                filtered_products.append(product)
        
        # Save filtered product data to a JSON file if there are filtered products.
        if filtered_products:
            with open('product_data.json', 'w', encoding='utf-8') as f:
                json.dump(filtered_products, f, ensure_ascii=False, indent=4)
            
            print("Product data saved to 'product_data.json'.")
        else:
            print("No products matching the required structure.")
    else:
        print("No 'data' key found in the response or 'data' is empty.")
else:
    print(f"Failed to retrieve data. Status code: {response.status_code}")
