import scrapy
import json
from urllib.parse import urljoin
import os

class TreesSpider(scrapy.Spider):
    name = "uktrees_scraper"
    start_urls = ['https://www.treeguideuk.co.uk/index-of-tree-species/']
    
    # Directory to save images
    images_dir = '../../WhatPlant\data\UKtrees_images'
    
    # Path to the output.json file
    data_file = 'output.json'

    def parse(self, response):
        # Extract tree categories and species names
        broadleaf_trees = response.xpath('//ul[@id="menu-broadleaf-trees"]/li/a/text()').getall()
        exotic_trees = response.xpath('//ul[@id="menu-exotic-trees"]/li/a/text()').getall()
        conifers = response.xpath('//ul[@id="menu-conifers"]/li/a/text()').getall()

        # Store species names in output.json
        tree_data = {
            'broadleaf_trees': broadleaf_trees,
            'exotic_trees': exotic_trees,
            'conifers': conifers,
        }
        with open(self.data_file, 'w') as file:
            json.dump(tree_data, file)

        # Call a method to scrape each species
        yield from self.scrape_species(tree_data)

    def scrape_species(self, tree_data):
        # Loop through the species in output.json
        for category, species_list in tree_data.items():
            for species in species_list:
                species_url = urljoin('https://www.treeguideuk.co.uk/', species.lower() + '/')
                yield scrapy.Request(species_url, callback=self.parse_species, meta={'species_name': species})

    def parse_species(self, response):
        species_name = response.meta['species_name']
        
        # Create a directory for images if it doesn't exist
        if not os.path.exists(self.images_dir):
            os.makedirs(self.images_dir)

        # Scrape the scientific name (only once per page)
        scientific_name = response.css('span.Scientific_Name::text').get()
        
        # Extract image URLs (supports .png, .jpeg, .jpg)
        image_urls = response.css('img::attr(src)').getall()

        for index, img_url in enumerate(image_urls):
            # Make the image URL absolute if it's relative
            img_url = urljoin(response.url, img_url)
            
            # Extract the image extension and filter for allowed formats
            ext = os.path.splitext(img_url)[-1].lower()
            if ext in ['.png', '.jpg', '.jpeg']:
                # Name the image based on the scientific name if available, otherwise the species name
                if scientific_name:
                    image_name = f"{scientific_name}_{index+1}{ext}"
                else:
                    image_name = f"{species_name}_{index+1}{ext}"
                
                image_path = os.path.join(self.images_dir, image_name)
                
                # Yield request to download the image
                yield scrapy.Request(img_url, callback=self.save_image, meta={'image_path': image_path})

    def save_image(self, response):
        image_path = response.meta['image_path']
        with open(image_path, 'wb') as f:
            f.write(response.body)
        print(f"Saved image: {image_path}")
