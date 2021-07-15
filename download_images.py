import requests,json


def read_json(json_link):
    """
    This function retrieves data from JSON file.

    :param json_link: JSON File Path.
    :return: Dictionary List.
    """
    with open(json_link,mode='r') as jsonfile:
        return json.load(jsonfile)

def DownloadImage(url):
    response = requests.get(url)
    mainfolder = "images/"
    name = url.split("/")[-1]
    file = open(mainfolder+name, "wb")
    file.write(response.content)
    file.close()
    return mainfolder+name


if __name__ == '__main__':
    variantes_photos = read_json("link-data/variantes_photos.json")
    photos_list = []
    for photo in variantes_photos:
        if (photo["photo"] not in photos_list and photo["photo"] is not ""):
            try:
                link = photo["photo"].replace("produit_variante_photos/Tester/","https://www.dafy-moto.com/images/product/high/")
                print(link)
                DownloadImage(link)
                photos_list.append(photo["photo"])
            except Exception as e:
                print(photo["photo"],e)