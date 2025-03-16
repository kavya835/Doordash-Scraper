import asyncio


from scrapybara import Scrapybara
from undetected_playwright.async_api import async_playwright



async def get_scrapybara_browser():
    client = Scrapybara(api_key="scrapy-ed5543a7-f9f4-446a-969b-b9ecd34c9dcc")
    instance = client.start_browser()
    return instance


async def retrieve_menu_items(instance, start_url: str) -> list[dict]:
    cdp_url = instance.get_cdp_url().cdp_url

    
    async with async_playwright() as p:

        # print("Connecting to browser...")
        browser = await p.chromium.connect_over_cdp(cdp_url, timeout=120000)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080}) # prevent timeout error
        page = await context.new_page()
        

        # print(f"Navigating to {start_url}")
        await page.goto(start_url)
        

        # print("Waiting for menu items to load...")
        await page.wait_for_selector('[data-testid="MenuItem"]')
        

        # # Scroll to load all items (works without it)
        # print("Scrolling to load all items...")
        # grid_container = await page.query_selector('[data-testid="VirtualGridContainer"]')
        
        # if grid_container:
        #     prev_height = 0 # scroll height
        #     while True:
        #         await grid_container.evaluate('grid => grid.scrollTo(0, grid.scrollHeight)')
        #         await page.wait_for_timeout(1000)  # wait for content to load
        #         curr_height = await grid_container.evaluate('grid => grid.scrollHeight')
                
                
        #         if curr_height == prev_height:
        #             break
        #         prev_height = curr_height


        # Get all menu items using html tags
        items_elements = await page.query_selector_all('[data-testid="MenuItem"]')
        
        print(f"Found {len(items_elements)} items")
        
        items = []
        
        for i, item in enumerate(items_elements):

            # Extract item details
            name_item = await item.query_selector('h3')
            name = await name_item.text_content() if name_item else "N/A"
            
            price_item = await item.query_selector('[data-anchor-id="StoreMenuItemPrice"]')
            price = await price_item.text_content() if price_item else "N/A"
            
            tag_item = await item.query_selector('[data-testid^="most_liked_"]')
            tag = await tag_item.text_content() if tag_item else ""
            
            items.append({
                'name': name,
                'price': price,
                'tag': tag
            })
            print(f"Added item {i+1}: {name} - {price} {tag}")


        await context.close()
        await browser.close()
    
    return items


async def main():
    instance = await get_scrapybara_browser()

    try:
        await retrieve_menu_items(
            instance,
            "https://www.doordash.com/store/panda-express-san-francisco-980938/12722988/?event_type=autocomplete&pickup=false"
        )


    finally:
        instance.stop()


if __name__ == "__main__":
    asyncio.run(main())