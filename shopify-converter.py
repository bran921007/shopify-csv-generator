import json
import csv
import requests
import os
from urllib.parse import urlparse, urljoin
import math

fields = [
    'Handle',
    'Title',
    'Body (HTML)',
    'Vendor',
    'Product Category',
    'Type',
    'Tags',
    'Published',
    'Option1 Name',
    'Option1 Value',
    'Option2 Name',
    'Option2 Value',
    'Option3 Name',
    'Option3 Value',
    'Variant SKU',
    'Variant Grams',
    'Variant Inventory Tracker',
    'Variant Inventory Qty',
    'Variant Inventory Policy',
    'Variant Fulfillment Service',
    'Variant Price',
    'Variant Compare At Price',
    'Variant Requires Shipping',
    'Variant Taxable',
    'Variant Barcode',
    'Image Src',
    'Image Position',
    'Image Alt Text',
    'Gift Card',
    'SEO Title',
    'SEO Description',
    'Google Shopping / Google Product Category',
    'Google Shopping / Gender',
    'Google Shopping / Age Group',
    'Google Shopping / MPN',
    'Google Shopping / AdWords Grouping',
    'Google Shopping / AdWords Labels',
    'Google Shopping / Condition',
    'Google Shopping / Custom Product',
    'Google Shopping / Custom Label 0',
    'Google Shopping / Custom Label 1',
    'Google Shopping / Custom Label 2',
    'Google Shopping / Custom Label 3',
    'Google Shopping / Custom Label 4',
    'Variant Image',
    'Variant Weight Unit',
    'Variant Tax Code',
    'Cost per item',
    'Price / International',
    'Compare At Price / International',
    'Status'
]

def parse_shop_url(url):
    """Parse and validate shop URL, handling both domain and collection URLs."""
    # Remove any protocol
    url = url.replace('http://', '').replace('https://', '')
    
    # Split into domain and path
    parts = url.split('/')
    domain = parts[0]
    
    # Handle collection path if present
    collection_path = ''
    if len(parts) > 1 and 'collections' in parts:
        collection_index = parts.index('collections')
        if len(parts) > collection_index + 1:
            collection_path = f"/collections/{parts[collection_index + 1]}"
    
    # Ensure domain ends with .com if not .myshopify.com
    if not domain.endswith('.myshopify.com') and not domain.endswith('.com'):
        domain += '.com'
    
    return domain, collection_path

def fetch_products(domain, page=1, collection_path=''):
    """Fetch products from Shopify store."""
    base_url = f"https://{domain}"
    
    if collection_path:
        # For collection-specific products
        url = urljoin(base_url, f"{collection_path}/products.json?limit=250&page={page}")
    else:
        # For all products
        url = urljoin(base_url, f"/products.json?limit=250&page={page}")
    
    print(f"Fetching: {url}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # Some Shopify stores might redirect to password page
        if 'password' in response.url:
            print("Error: Store is password protected")
            return None
            
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page {page}: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from page {page}: {str(e)}")
        return None

def get_total_pages(domain):
    """Get total number of pages available."""
    first_page = fetch_products(domain)
    if not first_page:
        return 0
    
    total_products = len(first_page.get('products', []))
    if total_products < 250:
        return 1
    
    page = 2
    while True:
        data = fetch_products(domain, page)
        if not data or not data.get('products'):
            return page - 1
        if len(data['products']) < 250:
            return page
        page += 1

def get_variant_image(variant, product_images):
    """Get the correct image for a variant based on various matching strategies."""
    if not product_images:
        return None
    
    # Strategy 1: Direct image_id match
    if variant.get('image_id'):
        for image in product_images:
            if image['id'] == variant['image_id']:
                return image
    
    # Strategy 2: Match by variant_ids in image
    for image in product_images:
        if 'variant_ids' in image and variant['id'] in image['variant_ids']:
            return image
    
    # Strategy 3: Try to match by option value in image alt text
    variant_option = variant.get('option1', '').lower()
    if variant_option:
        for image in product_images:
            if image.get('alt', '').lower().find(variant_option) != -1:
                return image
    
    # Strategy 4: If it's the first variant, use the first image
    if variant.get('position', 0) == 1 and product_images:
        return product_images[0]
    
    return None

def create_base_row(product):
    """Create the base row with common product information."""
    row = []
    row.append(product['handle'])  # Handle
    row.append(product['title'])  # Title
    row.append(product['body_html'])  # Body (HTML)
    row.append(product['vendor'])  # Vendor
    row.append('LEGAL SELLING CATEGORY')  # Product Category
    row.append(product['product_type'])  # Type
    
    # Join tags with spaces
    tags = ' '.join(product['tags'].split(', ') if isinstance(product['tags'], str) else product['tags'])
    row.append(tags)  # Tags
    
    row.append('TRUE')  # Published
    
    # Get the option names from the product options
    option_names = [opt['name'] for opt in product['options']]
    row.append(option_names[0] if option_names else 'Title')  # Option1 Name
    
    return row

def create_variant_rows(product, base_row):
    """Create rows for each variant, including image handling."""
    all_rows = []
    product_images = product.get('images', [])
    variant_images = []
    
    for variant_index, variant in enumerate(product['variants']):
        variant_row = base_row.copy() if variant_index == 0 else [''] * len(base_row)
        
        if variant_index > 0:
            variant_row[0] = product['handle']
        
        # Get variant-specific image
        variant_image = get_variant_image(variant, product_images)
        
        # Add variant-specific information
        variant_row.extend([
            variant.get('option1', 'Default Title'),  # Option1 Value
            '',  # Option2 Name
            '',  # Option2 Value
            '',  # Option3 Name
            '',  # Option3 Value
            variant.get('sku', ''),  # Variant SKU
            variant.get('grams', 0),  # Variant Grams
            'shopify',  # Variant Inventory Tracker
            variant.get('inventory_quantity', 0),  # Variant Inventory Qty
            'deny',  # Variant Inventory Policy
            'manual',  # Variant Fulfillment Service
            variant.get('price', ''),  # Variant Price
            variant.get('compare_at_price', ''),  # Variant Compare At Price
            'TRUE',  # Variant Requires Shipping
            'TRUE',  # Variant Taxable
            variant.get('barcode', ''),  # Variant Barcode
        ])
        
        # Add image information
        if variant_image:
            variant_images.append(variant_image['src'])
            variant_row.extend([
                variant_image['src'],  # Image Src
                str(len(variant_images)),  # Image Position
                variant_image.get('alt', ''),  # Image Alt Text
            ])
        else:
            variant_row.extend(['', '', ''])  # Empty image fields
        
        # Add remaining fields
        variant_row.extend([
            'FALSE',  # Gift Card
            '',  # SEO Title
            '',  # SEO Description
        ] + [''] * 13)  # Google Shopping fields
        
        # Add variant image and final fields
        variant_row.extend([
            variant_image['src'] if variant_image else '',  # Variant Image
            variant.get('weight_unit', 'g'),  # Variant Weight Unit
            '',  # Variant Tax Code
            '',  # Cost per item
            '',  # Price / International
            '',  # Compare At Price / International
            'active' if variant_index == 0 else ''  # Status
        ])
        
        all_rows.append(variant_row)
    
    return all_rows, variant_images

def create_additional_image_rows(product, used_images):
    """Create additional rows for product images that haven't been used as variant images."""
    image_rows = []
    position_counter = len(used_images) + 1
    
    for image in product['images']:
        if image['src'] in used_images:
            continue
            
        image_row = [''] * len(fields)
        image_row[0] = product['handle']  # Handle
        image_row[25] = image['src']  # Image Src
        image_row[26] = str(position_counter)  # Image Position
        image_row[27] = image.get('alt', '')  # Image Alt Text
        image_rows.append(image_row)
        position_counter += 1
    
    return image_rows

def process_products(products):
    """Process products and return rows for CSV."""
    all_rows = []
    
    for product in products:
        # Create the base row
        base_row = create_base_row(product)
        
        # Create variant rows and get used images
        variant_rows, used_images = create_variant_rows(product, base_row)
        
        # Create rows for any additional images
        additional_image_rows = create_additional_image_rows(product, set(used_images))
        
        # Add all rows
        all_rows.extend(variant_rows)
        all_rows.extend(additional_image_rows)
    
    return all_rows

def write_csv_file(rows, filename):
    """Write rows to a CSV file."""
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow(fields)
        csvwriter.writerows(rows)

def main():
    print("Shopify Product CSV Generator")
    print("----------------------------")
    
    # Get URL from user
    url = input("Enter your Shopify store URL (e.g., store-name.com or store-name.com/collections/collection-name): ").strip()
    
    # Parse and validate the URL
    try:
        domain, collection_path = parse_shop_url(url)
    except Exception as e:
        print(f"Error processing URL: {str(e)}")
        return
    
    if collection_path:
        print(f"\nUsing domain: {domain}")
        print(f"Fetching from collection: {collection_path}")
    else:
        print(f"\nUsing domain: {domain}")
        print("Fetching all products")
    
    # Test connection
    print("\nTesting connection to store...")
    test_data = fetch_products(domain, 1, collection_path)
    if not test_data:
        print("Error: Could not connect to the store. Please check the URL and try again.")
        return
    
    # Get total pages
    print("\nFetching total number of pages...")
    total_pages = get_total_pages(domain)
    if total_pages == 0:
        print("No products found or error accessing the store.")
        return
    
    print(f"Found {total_pages} pages of products.")
    
    # Process products in chunks
    all_rows = []
    products_per_file = 1000
    file_count = 1
    
    try:
        for page in range(1, total_pages + 1):
            print(f"\nFetching page {page} of {total_pages}...")
            data = fetch_products(domain, page, collection_path)
            if not data:
                continue
            
            print(f"Processing {len(data['products'])} products from page {page}...")
            
            # Process products from this page
            page_rows = process_products(data['products'])
            all_rows.extend(page_rows)
            
            # Check if we need to write to file
            if len(all_rows) >= products_per_file or page == total_pages:
                # Generate filename
                clean_filename = domain.replace('.', '_').replace('-', '_')
                filename = f"shopify_inventory_{clean_filename}_part_{file_count}.csv"
                
                print(f"\nWriting {len(all_rows)} rows to {filename}...")
                write_csv_file(all_rows, filename)
                
                # Reset for next file
                all_rows = []
                file_count += 1
        
        print("\nProcessing complete!")
        print(f"Generated {file_count - 1} CSV files.")
        
    except Exception as e:
        print(f"\nError during processing: {str(e)}")
        return

if __name__ == "__main__":
    main()
    
