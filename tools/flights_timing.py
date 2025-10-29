import httpx
import requests
from bs4 import BeautifulSoup, Tag


def flights_timing() -> str:
    """
    Returns a few options of flights
    """

    result = "Options for flights:\n\n"

    try:
        # Add timeout back and debug
        # limit to singapore airline first
        api_key = ""
        url = f"http://api.aviationstack.com/v1/flights?access_key={api_key}&airline_name={"Singapore Airlines"}"
        response = requests.get(url)
        data = response.json()
        response.raise_for_status()

        # soup = BeautifulSoup(response.text, "xml")
        #
        # items = soup.find_all("item", limit=10)

    #     if items:
    #         news_items = []
    #         for item in items:
    #             try:
    #                 # Ensure item is a Tag
    #                 if not isinstance(item, Tag):
    #                     continue
    #
    #                 # Extract title
    #                 title_elem = item.find("title")
    #                 title = title_elem.text.strip() if title_elem else ""
    #
    #                 # Extract description/snippet
    #                 desc_elem = item.find("description")
    #                 snippet = desc_elem.text.strip() if desc_elem else ""
    #
    #                 # Clean snippet - remove HTML if any
    #                 if snippet:
    #                     # Parse snippet to remove any HTML tags
    #                     snippet_soup = BeautifulSoup(snippet, "html.parser")
    #                     snippet = snippet_soup.get_text().strip()
    #
    #                 if title:
    #                     news_items.append({
    #                         "title": title,
    #                         "snippet": snippet
    #                     })
    #
    #             except Exception:
    #                 continue  # Skip problematic items
    #
    #         if news_items:
    #             for i, item in enumerate(news_items, 1):
    #                 result += f"{i}. {item['title']}\n"
    #                 if item['snippet']:
    #                     result += f"   {item['snippet']}\n"
    #                 result += "\n"
    #             return result.strip()
    #
    except httpx.TimeoutException:
         pass
    except httpx.HTTPError:
         pass
    except Exception:
        pass

    # Fallback news if RSS fetch fails
    return data

