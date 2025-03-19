import asyncio
import json, html


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
        context = await browser.new_context()
        page = await context.new_page()
        

        # print(f"Navigating to {start_url}")
        await page.goto(start_url)

        
        restaurant_title = await page.text_content("h1")
        print("Restaurant Title:", restaurant_title)

        # Get list of Playwright locator objects that are of <script type="application/ld+json">
        json_txt = await page.locator("script[type='application/ld+json']").all()
        i = 1

        items = []

        for js in json_txt:
            raw_str = await js.text_content() # extract the inner text
            data_obj = json.loads(raw_str)
            

            if "hasMenu" in data_obj:

                # Save information as a json file
                # with open(f"info.json", "w", encoding="utf-8") as f:
                #     json.dump(data_obj, f, indent=2, ensure_ascii=False)


                menu_obj = data_obj["hasMenu"]
                sections_list = menu_obj["hasMenuSection"]

                for section_group in sections_list:
                    for section in section_group:
                        items_list = section.get("hasMenuItem", [])
                        for item in items_list:
                            name = item.get("name", "Unknown Item")
                            offers = item.get("offers", {})
                            price = offers.get("price", "N/A")

                            items.append({
                                'name': name,
                                'price': price
                            })


        await context.close()
        await browser.close()
    
    j = 1;
    for i in items:
        print(f"-----Item #{j}-----")
        for key, value in i.items():
            print(f"{key}: {value}")
        j += 1
        print();

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