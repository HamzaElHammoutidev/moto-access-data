"""
This module helps with extracting data from website link directly.

"""
import requests,re, json,sys,csv,logging
from bs4 import BeautifulSoup
from retrying import retry
import pandas as pd


link_regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)


def csv_tulple(filename):
    import pandas as pd

    # Read the CSV into a pandas data frame (df)
    #   With a df you can do many things
    #   most important: visualize data with Seaborn
    df = pd.read_csv(filename, delimiter=',')

    # Or export it in many ways, e.g. a list of tuples
    tuples = [tuple(x) for x in df.values]

    # or export it as a list of dicts
    dicts = df.to_dict('records')

    return dicts



def get_page_content(url):
    """
    Helps with getring page content with BeautifulSoup.

    :param url: Product Variante Url.
    :return: Variante Page Content.
    """
    req = requests.get(url)
    soup = BeautifulSoup(req.text, "lxml")
    return soup


def get_variante_images(content):
    """
    Helps with fetchinf product images and clean it.

    :param content: Variante Page BS4.
    :return: Images Links
    """
    images_list = []
    images_header = content.find('ul', {'class':"pictures-thumbnails"})
    images = images_header.find_all('li')
    for image in images:
        if "hidden" not in image["class"][-1]:
            images_list.append(image.find('img')["src"])
    return images_list


def get_product_options(content):
    """
    Helps with fetching product options.

    :param content: Variante Content Page BS4.
    :return: options List.
    """
    options_list = []
    options = content.select(".product-article__footer__menu-content__features__tr")
    if options:
        for option in options:
            key = (option.find_all("td", {"class": "product-article__footer__menu-content__features__tr__td"})[0])
            value = (option.find_all("td", {"class": "product-article__footer__menu-content__features__tr__td"})[1])
            options_list.append([key.text.strip(), value.text.strip().replace("\n", " / ")])
    return options_list


def GetJSONCategories():
    jsonfile = open("input/categs.json", "r")
    return json.load(jsonfile)  # Read Data

def GetJSONMarques():
    jsonfile = open("input/marques.json", "r")
    return json.load(jsonfile)  # Read Data

def get_marqueId(name):
    marques = GetJSONMarques()
    for marque in marques:
        if str(marque["name"]).lower() == name.lower():
            return marque["id"]
    return 195


def get_categoriesId(category_link):
    """
    Gets back category Id from categories list.

    :param category_link: Category Link to match.
    :return: Category Id.
    """
    categories = GetJSONCategories()
    for categorie in categories:
        if categorie["link"].strip() == category_link.strip():
            return categorie["id"]
    return 326


def produit_table(produit):
    """
    Gets back Product Table Row.

    :param produit: Product to form on Table Mode.
    :return: Product Row.
    """
    global produit_id
    name = produit["title"]
    slug = produit["title"].replace(" ","-").lower()
    description = produit["description"]
    categ_id = get_categoriesId(produit["categories"][-1][1])
    marque_id = get_marqueId(produit["brand"])
    avec_piece = produit["avec_piece"]
    created_at = ""
    updated_at = ""
    visibilite = 1
    return {
        "id":produit_id,
        "name":name,
        "slug":slug,
        "description":str(description),
        "categ_id":categ_id,
        "marque_id":marque_id,
        "created_at":created_at,
        "updated_at":updated_at,
        "visibilite":visibilite,
        "avec_piece":avec_piece
    }


def fetch_product(soup,link):
    """
    Retrieves Product Table Data.

    :param soup: Product Page Content Beautiful Soup.
    :return: Product Table Row.
    """
    title_header = soup.find("h1",{"class":"product-article__title"})
    title = title_header.find('span',{'itemprop':'name'}).text
    brand = title_header.find('span',{'itemprop':'brand'}).text
    coloris = title_header.find('span',{'class':'js-current-color-title'}).text
    description = soup.find("span",{"class":"description"})

    images = get_variante_images(soup)
    options = get_product_options(soup)
    compatibility_bool = False
    compatibility = soup.find(".js-vehicle-search-form-compatibility-container")
    if compatibility:
        compatibility_bool = True
    breadcrumb = soup.find("ol", {"class": "breadcrumb"})
    categories = breadcrumb.select('li')
    categories = categories[:-1]
    categories_list = []
    for category in categories:
        link = (category.find("a")["href"])
        categories_list.append([category.text, link])
    return ({
        "title": title,
        "brand": brand,
        "coloris": coloris.replace("/",","),
        "images":images,
        "description":str(description),
        "options_list":options,
        "avec_piece":compatibility_bool,
        "categories":categories_list,
        "link":link
    })


def check_option_row(option,options_list):
    """
    Get back Option id if it exists on Option table.

    :param option: Option row to check.
    :param options_list: Options list to check into.
    :return: Id if exsits on List.
    """
    for opt in options_list:
        if opt["name"] == option[0] and option[1] == opt["valeur"]:
            return opt
    return False


def option_table(produit):
    """
    Gets back Options Table Row.

    :param produit: Product to fetch options from.
    :return: Options List.
    """
    global option_id
    global options_rows
    options_list = []
    for option in produit["options_list"]:
        opt = check_option_row(option,options_rows)
        if not opt:
            id = option_id
            name = option[0]
            valeur = option[1]
            created_at = ""
            updated_at = ""
            options_list.append({
                "id" : id ,
                "name": name,
                "valeur": valeur,
                "created_at" : created_at,
                "updated_at" : updated_at
            })
            option_id += 1
        else:
            #print("Option Exsits")
            options_list.append(opt)
    return options_list


def check_product_existance(list_exsitance,product):
    """
    Check if product already scraped or not.

    :param list_exsitance: List of scraped products.
    :param product: product to check.
    :return: if product there return it/False.
    """
    for product_ex in list_exsitance:
        if product["name"] == product_ex["name"]:
            return product_ex
    return False


def produit_option(options,produit_id):
    """
    Gets back Product Options Table Row.

    :param produit: Product to fetch options from.
    :return: Product Option Row.
    """
    global option_produit_id
    options_produit_list = []
    for option in options:
        id = option_produit_id
        produit_id = produit_id
        option_id = option["id"]
        options_produit_list.append({
            "id" : id,
            "produit_id": produit_id,
            "option_id": option_id,
        })
        option_produit_id += 1
    return options_produit_list


def variante_table(variante,file_variant):
    """
    Gets back Variant Row.

    :param vairiante: Variante to Model
    :return: Product Variante Table Row in JSON.
    """
    #print(variante)
    couleur = variante["coloris"]
    try:
        taille = file_variant["taille"]
    except Exception as e:
        taille = ""
    quantite = file_variant["Dispo"]
    try:
        prix_vente = float(file_variant["Prix T.T.C."].replace("Dh","").replace(",","").strip())
    except :
        prix_vente = 0
    prix_promo = 0
    created_at = ""
    updated_at = ""
    ref = file_variant["Code barre"]
    return {
        "id": variante["variante_id"],
        "produit_id": variante["produit_id"],
        "couleur" : couleur,
        "taille":taille,
        "quantite": quantite,
        "qualite": "",
        "prix_vente": prix_vente,
        "prix_promo": prix_promo,
        "created_at": created_at,
        "updated_at": updated_at,
        "ref":ref
    }


def remove_duplicates(dataset,key):
    """
    This function helps to remove duplicates from dataset using Pandas package.

    :param dataset: Dictionary List to remove duplicates from.
    :return: Clean Unique dictionary list.
    """
    if key is '':
        df = pd.DataFrame(dataset).drop_duplicates()
    else:
        df = pd.DataFrame(dataset).drop_duplicates(key)
    return df.to_dict('records')


def DownloadImage(url):
    response = requests.get(url)
    mainfolder = "images/"
    name = url.split("/")[-1]
    file = open(mainfolder+name, "wb")
    file.write(response.content)
    file.close()
    return mainfolder+name


def fetch_photo(photo):
    try:
        DownloadImage(photo.replace("/small/","/high/"))
    except Exception as e:
        print(photo["photo"], e)
    return photo.replace("https://www.dafy-moto.com/images/product/small/","produit_variante_photos/Tester/")

def variante_photo_table(variante):
    """
    Gets back Variant Photo Row.

    :param variante: Product Variante to Model.
    :return: Product Variante Photo Model Row in JSON Format.
    """
    global variante_photo_id
    photos_list = []
    couleur = variante["coloris"]
    for photo in variante["images"]:
        if photo == variante["images"][0]:
            _principal_holder = 1
        else:
            _principal_holder= 0
        created_at = ""
        updated_at = ""
        photos_list.append( {
            "id": variante_photo_id,
            "produit_id" : variante["produit_id"],
            "couleur": couleur,
            "photo":fetch_photo(photo),
            "principale" : _principal_holder,
            "created_at" : created_at,
            "updated_at": updated_at
        })
        variante_photo_id += 1
    return photos_list


def save_data_json(data,file_name):
    """
    Helps with saving dict list on json file.

    :param data: Dictionary List.
    :param file_name: Json Filename.
    :return: None.
    """
    with open("data_stage/{}.json".format(file_name), "w", encoding="utf-8") as jsonfile:
        json.dump(data, jsonfile, ensure_ascii=False)


if __name__ == '__main__':
    variante_id = 10000
    produit_id = 10000
    variante_photo_id = 10000
    principale_holder = False
    option_id = 10000
    option_produit_id = 10000

    product_rows = []
    variantes_rows = []
    variantes_photos_rows = []
    options_rows = []
    options_product_rows = []

    products_existance_list = []
    products_row = []
    variants_rows = csv_tulple("input/dafy_withlinks.csv")
    count = 0
    for variant_row in variants_rows:
        #if count == 30:
        #    break
        link = (variant_row["LIEN DAFY.COM"])
        if re.match(link_regex, link) is not None:
            try:
                soup = get_page_content(link)
                variante_data = fetch_product(soup,link)
                product = produit_table(variante_data)
                check_prod = check_product_existance(products_existance_list,product)
                if not check_prod:
                    product_rows.append(product)
                    products_existance_list.append(product)
                    produit_id += 1
                else:
                    product = check_prod
                options = option_table(variante_data)
                [options_rows.append(option) for option in options]
                options_rows = [i for n, i in enumerate(options_rows) if i not in options_rows[n + 1:]]

                options_produit = produit_option(options, produit_id)
                [options_product_rows.append(option_product) for option_product in options_produit]
                options_product_rows = [i for n, i in enumerate(options_product_rows) if i not in options_product_rows[n + 1:]]

                variante_data["variante_id"] = variante_id
                variante_data["produit_id"] = product['id']
                variantes_rows.append(variante_table(variante_data, variant_row))

                variante_data["variante_photo_id"] = variante_photo_id
                [variantes_photos_rows.append(variante_photo) for variante_photo in variante_photo_table(variante_data)]

                variante_id += 1

                print("Product: {}".format(json.dumps(product)))
                print("Options: {}".format(json.dumps(options)))
                print("Options Produits: {}".format(json.dumps(options_produit)))
                print("Variantes Produits: {}".format(json.dumps(variante_data)))
                print("Variantes Produits Photos: {}".format(json.dumps(variante_photo_table(variante_data))))
                print("----------------------------------------")

                #count += 1
                """
                            print("Product: {}".format(json.dumps(product_rows)))
                            print("Options: {}".format(json.dumps(options_rows)))
                            print("Options Produits: {}".format(json.dumps(options_product_rows)))
                            print("Variantes Produits: {}".format(json.dumps(variantes_rows)))
                            print("Variantes Produits Photos: {}".format(json.dumps(variantes_photos_rows)))
                            print("----------------------------------------")
                """
            except Exception as e:
                logging.error(e)
    variantes_rows = remove_duplicates(variantes_rows, ["produit_id", "couleur", "taille"])
    product_rows = remove_duplicates(product_rows, "name")
    options_product_rows = remove_duplicates(options_product_rows, ["produit_id", "option_id"])
    variantes_photos_rows = remove_duplicates(variantes_photos_rows, ["produit_id", "couleur", "photo"])

    save_data_json(product_rows, "products")
    save_data_json(variantes_rows, "variantes")
    save_data_json(variantes_photos_rows, "variantes_photos")
    save_data_json(options_rows, "options")
    save_data_json(options_product_rows, "options_products")