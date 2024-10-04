import scrapy
import os
import re
from urllib.parse import urljoin

class FirstNatureSpider(scrapy.Spider):
    name = "first_nature"
    start_urls = ['https://first-nature.com/flowers/index.php']

    def parse(self, response):
        # Loop through all <a> tags inside <em> tags and extract the href
        species_links = response.xpath('//em/a[@href]/@href').getall()

        for link in species_links:
            absolute_url = urljoin(response.url, link)
            yield scrapy.Request(absolute_url, callback=self.parse_species_page)

    def parse_species_page(self, response):
        # Handle h1 with em or i tags for scientific name and rest of text for English name
        h1_element = response.xpath('//h1').get()
        scientific_name = ''
        english_name = ''

        if response.xpath('//h1/em/text()').get():
            scientific_name = response.xpath('//h1/em/text()').get().strip()
            english_name = re.sub(r'<.*?>', '', h1_element).strip()  # remove any tags from the rest of h1
        elif response.xpath('//h1/i/text()').get():
            scientific_name = response.xpath('//h1/i/text()').get().strip()
            english_name = re.sub(r'<.*?>', '', h1_element).strip()  # remove any tags from the rest of h1
        else:
            scientific_name = response.xpath('//h1/text()').get().strip()

        # Scrape the first <p> element following the h1 for classification info
        classification_info = response.xpath('//h1/following-sibling::p[1]/text()').get()
        if classification_info:
            phylum = re.search(r'Phylum:\s*(\w+)', classification_info).group(1) if re.search(r'Phylum:\s*(\w+)', classification_info) else ''
            class_name = re.search(r'Class:\s*(\w+)', classification_info).group(1) if re.search(r'Class:\s*(\w+)', classification_info) else ''
            order = re.search(r'Order:\s*(\w+)', classification_info).group(1) if re.search(r'Order:\s*(\w+)', classification_info) else ''
            family = re.search(r'Family:\s*(\w+)', classification_info).group(1) if re.search(r'Family:\s*(\w+)', classification_info) else ''
        else:
            phylum = class_name = order = family = ''

        # Find all img URLs inside p elements
        image_urls = response.xpath('//p//img/@src').getall()
        image_paths = []

        # Create the directory for images if it doesn't exist
        images_dir = 'first_nature_images'
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)

        for idx, image_url in enumerate(image_urls, start=1):
            image_name = f"{scientific_name.replace(' ', '_')}_{idx}.jpg"
            image_path = os.path.join(images_dir, image_name)

            # Store the image path for the table
            image_paths.append(image_name)

            # Download the image
            absolute_image_url = urljoin(response.url, image_url)
            yield scrapy.Request(
                absolute_image_url, 
                callback=self.save_image,
                meta={'image_path': image_path}
            )

        # Scrape all the text from remaining <p> elements until the next <div> element
        details_text = ' '.join(response.xpath('//h1/following-sibling::p[position()>1 and following-sibling::div[1]]/text()').getall()).strip()

        # Yield the species data for the table
        yield {
            'Phylum': phylum,
            'Class': class_name,
            'Order': order,
            'Family': family,
            'Scientific Name': scientific_name,
            'English Name': english_name if english_name != scientific_name else '',
            'Images': image_paths,
            'Details': details_text
        }

    def save_image(self, response):
        # Save the image to the local folder
        image_path = response.meta['image_path']
        with open(image_path, 'wb') as f:
            f.write(response.body)
