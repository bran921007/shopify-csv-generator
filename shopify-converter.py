import json
import csv

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
    variant_images = []  # Track images used for variants
    
    # First pass: Create main product row with all images
    first_row = base_row.copy()
    first_variant = product['variants'][0]
    
    # Add variant-specific information for first variant
    first_row.extend([
        first_variant.get('option1', 'Default Title'),  # Option1 Value
        '',  # Option2 Name
        '',  # Option2 Value
        '',  # Option3 Name
        '',  # Option3 Value
        first_variant.get('sku', ''),  # Variant SKU
        first_variant.get('grams', 0),  # Variant Grams
        'shopify',  # Variant Inventory Tracker
        '0',  # Variant Inventory Qty
        'deny',  # Variant Inventory Policy
        'manual',  # Variant Fulfillment Service
        first_variant.get('price', ''),  # Variant Price
        first_variant.get('compare_at_price', ''),  # Variant Compare At Price
        'TRUE',  # Variant Requires Shipping
        'TRUE',  # Variant Taxable
        first_variant.get('barcode', ''),  # Variant Barcode
    ])
    
    # Add first image information
    if product_images:
        first_image = product_images[0]
        first_row.extend([
            first_image['src'],  # Image Src
            '1',  # Image Position
            first_image.get('alt', ''),  # Image Alt Text
        ])
    else:
        first_row.extend(['', '1', ''])  # Empty image fields
    
    # Add remaining fields
    first_row.extend([
        'FALSE',  # Gift Card
        '',  # SEO Title
        '',  # SEO Description
    ] + [''] * 13)  # Google Shopping fields
    
    # Add variant image for first variant
    first_variant_image = get_variant_image(first_variant, product_images)
    if first_variant_image:
        variant_images.append(first_variant_image['src'])
        first_row.extend([
            first_variant_image['src'],  # Variant Image
        ])
    else:
        first_row.extend([''])  # Empty variant image
    
    # Add remaining fields
    first_row.extend([
        first_variant.get('weight_unit', 'g'),  # Variant Weight Unit
        '',  # Variant Tax Code
        '',  # Cost per item
        '',  # Price / International
        '',  # Compare At Price / International
        'active'  # Status
    ])
    
    all_rows.append(first_row)
    
    # Second pass: Create rows for additional variants with their images
    for variant in product['variants'][1:]:
        variant_row = [''] * len(base_row)
        variant_row[0] = product['handle']  # Keep handle
        
        # Add variant-specific information
        variant_row.extend([
            variant.get('option1', ''),  # Option1 Value
            '',  # Option2 Name
            '',  # Option2 Value
            '',  # Option3 Name
            '',  # Option3 Value
            variant.get('sku', ''),  # Variant SKU
            variant.get('grams', 0),  # Variant Grams
            'shopify',  # Variant Inventory Tracker
            '0',  # Variant Inventory Qty
            'deny',  # Variant Inventory Policy
            'manual',  # Variant Fulfillment Service
            variant.get('price', ''),  # Variant Price
            variant.get('compare_at_price', ''),  # Variant Compare At Price
            'TRUE',  # Variant Requires Shipping
            'TRUE',  # Variant Taxable
            variant.get('barcode', ''),  # Variant Barcode
        ])
        
        # Get variant-specific image
        variant_image = get_variant_image(variant, product_images)
        if variant_image:
            variant_images.append(variant_image['src'])
            # Add image information
            variant_row.extend([
                variant_image['src'],  # Image Src
                str(len(variant_images)),  # Image Position
                variant_image.get('alt', ''),  # Image Alt Text
            ])
            # Add remaining fields
            variant_row.extend([
                'FALSE',  # Gift Card
                '',  # SEO Title
                '',  # SEO Description
            ] + [''] * 13)  # Google Shopping fields
            
            # Add variant image
            variant_row.append(variant_image['src'])  # Variant Image
        else:
            # Add empty image fields
            variant_row.extend(['', '', ''] + [''] * 16)  # Empty image and additional fields
        
        # Add remaining fields
        variant_row.extend([
            variant.get('weight_unit', 'g'),  # Variant Weight Unit
            '',  # Variant Tax Code
            '',  # Cost per item
            '',  # Price / International
            '',  # Compare At Price / International
            ''  # Status
        ])
        
        all_rows.append(variant_row)
    
    return all_rows, variant_images

def create_additional_image_rows(product, used_images):
    """Create additional rows for product images that haven't been used as variant images."""
    image_rows = []
    position_counter = len(used_images) + 1
    
    for image in product['images']:
        # Skip if this image was already used for a variant
        if image['src'] in used_images:
            continue
            
        # Create new row for additional image
        image_row = [''] * len(fields)
        image_row[0] = product['handle']  # Handle
        image_row[25] = image['src']  # Image Src
        image_row[26] = str(position_counter)  # Image Position
        image_row[27] = image.get('alt', '')  # Image Alt Text
        image_rows.append(image_row)
        position_counter += 1
    
    return image_rows

def main():
    rows = []
    
    # Set to true if you are running first time and testing
    test = False
    
    with open('./products.json') as f:
        data = json.load(f)
        
        for product in data['products']:
            # Create the base row
            base_row = create_base_row(product)
            
            # Create variant rows and get used images
            variant_rows, used_images = create_variant_rows(product, base_row)
            
            # Create rows for any additional images
            additional_image_rows = create_additional_image_rows(product, set(used_images))
            
            # Add all rows
            rows.extend(variant_rows)
            rows.extend(additional_image_rows)
            
            if test:
                break
    
    filename = "products_generated.csv"
    # writing to csv file
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow(fields)
        csvwriter.writerows(rows)

if __name__ == "__main__":
    main()
