# Shopify Product CSV Generator

This script converts a JSON product export into a Shopify-compatible CSV import file, with proper handling of variants, images, and all product attributes.

## Features

- Converts product JSON data to Shopify CSV format
- Handles multiple variants per product
- Supports variant-specific images with proper linking
- Maintains image positions and alt text
- Properly sets up variant image switching in Shopify
- Handles all required Shopify fields with appropriate defaults

## Prerequisites

- Python 3.6 or higher
- A JSON file containing product data in Shopify's export format

## Installation

1. Clone this repository or download the script:
```bash
git clone https://github.com/bran921007/shopify-csv-generator
```

2. Ensure you have your product JSON file ready (default name: `products.json`)

## Usage

1. Place your JSON file in the same directory as the script

2. Run the script:
```bash
python shopify-converter.py
```

3. The script will generate a file named `products_generated.csv`

4. Import the generated CSV file into Shopify

## Input JSON Format

Your JSON file should follow Shopify's product export format. Here's an example structure:

```json
{
  "products": [
    {
      "id": 1234567890,
      "title": "Product Title",
      "body_html": "Product Description",
      "vendor": "Vendor Name",
      "product_type": "Type",
      "handle": "product-handle",
      "variants": [
        {
          "id": 1234567890,
          "title": "Variant Title",
          "option1": "Option Value",
          "sku": "SKU123",
          "price": "99.99",
          "compare_at_price": "129.99"
        }
      ],
      "images": [
        {
          "id": 1234567890,
          "position": 1,
          "src": "https://example.com/image.jpg",
          "variant_ids": [1234567890],
          "alt": "Image Alt Text"
        }
      ]
    }
  ]
}
```

## Generated CSV Format

The script generates a CSV file with all required Shopify fields:

- Handle
- Title
- Body (HTML)
- Vendor
- Product Category
- Type
- Tags
- Published
- Option fields
- Variant fields
- Image fields
- And more...

## Image Handling

The script handles images in the following ways:

1. Main product images are assigned positions sequentially
2. Variant-specific images are properly linked to their variants
3. Image positions are maintained for proper gallery ordering
4. Alt text is preserved for SEO purposes

## Variant Handling

Variants are processed with the following considerations:

1. First variant contains all product information
2. Additional variants maintain only necessary fields
3. Each variant can have its own specific image
4. Proper option value handling for variant selection


## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License

## Author

Fran Perez
franciscoperez583@gmail.com
