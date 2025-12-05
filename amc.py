import random
import time
import pytest
from dotenv import load_dotenv

from discord_notify import send_showtimes, send_message

load_dotenv()


def random_delay(min_ms: int = 200, max_ms: int = 800) -> None:
    time.sleep(random.uniform(min_ms / 1000, max_ms / 1000))


def human_type(sb, selector: str, text: str) -> None:
    sb.click(selector)
    random_delay(100, 300)
    for char in text:
        sb.send_keys(selector, char)
        time.sleep(random.uniform(0.05, 0.15))
    random_delay(200, 500)


def human_click(sb, selector: str) -> None:
    try:
        sb.hover(selector)
        random_delay(150, 400)
    except Exception:
        pass
    sb.click(selector)
    random_delay(300, 700)


def random_scroll(sb) -> None:
    scroll_amount = random.randint(50, 200)
    direction = random.choice([1, -1])
    sb.execute_script(f"window.scrollBy(0, {scroll_amount * direction})")
    random_delay(100, 300)


def test_scrape_films(sb) -> None:
    url = "https://www.amctheatres.com/showtimes"
    sb.open(url)
    random_delay(500, 1500)
    
    human_type(sb, 'input[name="query"]', "Dallas, TX")
    random_delay(200, 500)
    sb.press_keys('input[name="query"]', "\n")
    random_delay(800, 1500)
    
    sb.wait_for_element('input[value="amc-northpark-15"]')
    random_delay(300, 600)
    human_click(sb, 'input[value="amc-northpark-15"]')
    
    sb.wait_for_element('button[type="submit"]:not([disabled])', timeout=5)
    random_delay(400, 900)
    random_scroll(sb)
    human_click(sb, '//button[contains(text(), "Continue")]')
    
    sb.wait_for_element('section[aria-label^="Showtimes for"]', timeout=15)
    random_delay(500, 1000)
    movie_sections = sb.find_elements('section[aria-label^="Showtimes for"]')
    
    theater_name = "AMC NorthPark 15"
    try:
        theater_element = sb.find_element('a[href*="/movie-theatres/"][class*="text-lg"]', timeout=5)
        if theater_element:
            theater_name = theater_element.text
    except Exception:
        pass

    results = []
    for section in movie_sections:
        try:
            title = section.find_element("css selector", "h1 a").text
            movie_data = {"title": title, "formats": {}}
            
            format_groups = section.find_elements(
                "css selector", 
                'li[role="listitem"][aria-label$=" Showtimes"]'
            )
            
            for group in format_groups:
                aria_label = group.get_attribute("aria-label")
                if not aria_label:
                    continue
                    
                format_name = aria_label.replace(" Showtimes", "")
                
                times = []
                links = group.find_elements("css selector", 'a[href^="/showtimes/"]')
                for link in links:
                    if link.text:
                        clean_time = link.text.split('\n')[0].strip()
                        times.append(clean_time)
                
                if times:
                    movie_data["formats"][format_name] = times
            
            if movie_data["formats"]:
                results.append(movie_data)
        except Exception:
            continue
    
    if results:
        send_showtimes(theater_name, results)
        print(f"✅ Sent {len(results)} movies to Discord")
    else:
        send_message("⚠️ No showtimes found - the scraper may need updating")
        print("⚠️ No showtimes found")


if __name__ == "__main__":
    pytest.main(["-s", "--headed", __file__])