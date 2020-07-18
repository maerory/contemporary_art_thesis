import scrapy
import re
from unidecode import unidecode

class ChristieSpider(scrapy.Spider):
    name = "christie"
    ## Put the URL of the foremost item of the auction event
    start_urls = [

    ]

    def parse(self, response):

        # Essential Data that are consistent through out all events
        next_page = response.css("#main_center_0_lnkNextLot::attr(href)").get()

        auction_name = response.css("#main_center_0_lblSaleTitle::text").get()
        location = response.css("#main_center_0_lblSaleLocation::text").get()
        date = response.css("#main_center_0_lblSaleDate::text").get()
        if '-' in date:
            date = re.sub(r'- \d+ ', '', date)

        # The description section is pretty consistent across all
        description = response.css("#main_center_0_lblLotDescription").get()
        description = re.sub("<.*?>","",description).split("\r\n")

        if re.search('\d', description[0]):
            title = re.sub("<.*>?","",description[1]).strip()
            name_tag = re.sub("<.*?>","",description[0]).strip()
        else:
            name_tag = description[0] + ' ' + description[1]
            title = description[2]


        ### Divide case for extraction
        try:

        ## HOW TO CRAWL THE ONLINE ONES?
        # name_tag = response.css("#lot-details-image-carousel > div:nth-child(2) > div.bid-panel > div:nth-child(2) > div.title::text").get()
        # name_tag = name_trag.strip("\r\n").strip()
        # sales_price_tag = response.css("#lot-details-image-carousel > div:nth-child(2) > div.bid-panel > div.biddingInformation > div.bid-updatable-info > div.price-realised.row::text").get()
        # estimate_tag = response.css("#lot-details-image-carousel > div:nth-child(2) > div.bid-panel > div.biddingInformation > div.bid-updatable-info > div.estimated.row::text").get().strip('\r\n').strip().rstrip('\r\n').split()


            sales_price_tag = response.css("#main_center_0_lblPriceRealizedPrimary::text").get().split()
            currency = sales_price_tag[0]
            sales_price = sales_price_tag[1]
            estimate_tag = response.css("#main_center_0_lblPriceEstimatedPrimary::text").get().split()
            estimate_low = estimate_tag[1]
            estimate_high = estimate_tag[-1]



            if name_tag.count("&") == 1:
                name_tag = name_tag.split("&")
                name1 = name_tag[0]
                name2 = name_tag[1]
                artist_name = name1.split("(")[0].rstrip() + ", " + name2.split(" (")[0].lstrip()
                artist_years = [name1.split("(")[1].rstrip(") ").lower(), name2.split("(")[1].rstrip(")  \r\n").lower()]
                for i in range(2):
                    if "b." in artist_years[i]:
                        artist_years[i] = artist_years[i].split()[-1].rstrip(")")
                    else:
                        artist_years[i] = artist_years[i].rstrip(")")
                if len(artist_years[0]) > 5 & len(artist_years[1]) > 5:
                    birth1 = artist_years[0].split("-")[0]
                    birth2 = artist_years[1].split("-")[0]
                    death1 = artist_years[0].split("-")[1]
                    death2 = artist_years[1].split("-")[1]
                    birth = birth1 + ", " + birth2
                    death = death1 + ", " + death2
                elif len(artist_years[0]) > 5:
                    birth1 = artist_years[0].split("-")[0]
                    death1 = artist_years[0].split("-")[1]
                    birth2 = artist_years[1].split("-")[0]
                    birth = birth1 + ", " + birth2
                    death = death1
                elif len(artist_years[1]) > 5:
                    birth1 = artist_years[0].split("-")[0]
                    death2 = artist_years[1].split("-")[1]
                    birth2 = artist_years[1].split("-")[0]
                    birth = birth1 + ", " + birth2
                    death = ", " + death2
                else:
                    birth1 = artist_years[0].split("-")[0]
                    birth2 = artist_years[1].split("-")[0]
                    birth = birth1 + ", " + birth2
                    death = ""
            # Two artists in different format
            elif name_tag.count("&") == 2:
                name_tag = name_tag.rstrip(") \r\n").split("(")
                artist_name = name_tag[0].rstrip()
                birth = name_tag[1].split()[-1]
                death = ""
            # Else Extract the year with regex
            else:
                name_tag = name_tag.rstrip(")").split("(")
                artist_name = name_tag[0].rstrip()
                ## Year might not be on the name_tag
                if len(name_tag) == 1:
                    artist_date = re.findall(r'[12]\d{3}', description[1])
                    if title is None:
                        title = description[2].lstrip("\r\n")
                else:
                    artist_date = re.findall(r'[12]\d{3}',name_tag[1])
                # Dead Artist
                if len(artist_date) > 1:
                    birth = artist_date[0]
                    death = artist_date[1]
                # Living Artist
                else:
                    birth = artist_date[0]
                    death = ""
            # Convert every foreign alphabet to English
            artist_name = unidecode(artist_name).title()

            yield {
                'date': date,
                'title': title,
                'artist': artist_name,
                'birth': birth,
                'death': death,
                'price': sales_price,
                'low': estimate_low,
                'high': estimate_high,
                'currency': currency,
                'location': location,
                'event': auction_name,
            }

            if next_page is not None:
                if "Calendar" in next_page:
                    return
                yield response.follow(next_page, callback=self.parse)
        except:
            if next_page is not None:
                if "Calendar" in next_page:
                    return
                yield response.follow(next_page, callback=self.parse)
