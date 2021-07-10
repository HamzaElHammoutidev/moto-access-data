"""
This module helps with extracting data from website link directly.

"""
import requests,re, json,sys,csv
from bs4 import BeautifulSoup
from retrying import retry
import pandas as pd

main_website = "https://www.dafy-moto.com"
variante_id = 10000
produit_id = 10000
variante_photo_id = 10000
principale_holder = False
option_id = 10000
option_produit_id = 10000


link_regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

##----Tables----##
product_rows = []
variantes_rows = []
variantes_photos_rows = []
options_rows = []
options_product_rows = []

def progress(count, total, suffix=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', suffix))
    sys.stdout.flush()  # As suggested by Rom Ruben


def wait(attempts, delay):
    print('Attempt #%d, retrying in %d seconds' % (attempts, delay // 1000))
    return delay


def retry_if_request_error(exception):
    """Return True if we should retry (in this case when it's an IOError), False otherwise"""
    return isinstance(exception, requests.exceptions.RequestException)

@retry(wait_random_min=5, wait_random_max=10,wait_func=wait,retry_on_exception=retry_if_request_error)
def get_variant_details(pse_id):
    """
    This function retrieves variante details using a PSE ID.

    :param pse_id: variante PSE ID .
    :return: Variante Details Dictionary.
    """
    url = "https://www.dafy-moto.com/ajax/product_change_attribute_1"
    data = {"pse_id":pse_id}
    req = requests.post(url,data)
    if req.status_code == 200:
        return req.json()


@retry(wait_random_min=5, wait_random_max=10,wait_func=wait,retry_on_exception=retry_if_request_error)
def get_variants_data(pses):
    """
    This function retrieves Variant Data using PSE ID  from Variante LINK.

    :param url: Variante Link.
    :return: Variante Data.
    """

    variantes_list = []
    for pse in pses:
        variantes = get_variant_details(pse["pseId"])["countryPseCollection"]
        for variante in variantes:
            variantes_list.append(variante)
    return variantes_list

@retry(wait_random_min=5, wait_random_max=10,wait_func=wait,stop_max_attempt_number=4)
def get_variants(link):
    """
    This function retrieves variant PSE ID.

    :param link: Variant Link.
    :return: Variant PSE ID.
    """
    req = requests.get(link)
    soup = BeautifulSoup(req.text, "lxml")
    match = (re.search('var countryPseCollection = (.*?)];',str(soup)).group(1))
    json_data = (json.loads(match+"]"))
    return json_data

#@retry(wait_random_min=5, wait_random_max=10,wait_func=wait,retry_on_exception=retry_if_request_error)
def get_variants_details(variante):
    req = requests.get(main_website+variante["url"])
    soup = BeautifulSoup(req.text, "lxml")

    data_file = soup.find("div",{"class":"nosto_product js-nosto-product"})
    name = soup.find("span",{"class":"name"})
    product_id = data_file.find("span",{"class":"product_id"})
    image_url = data_file.find("span",{"class":"image_url"})
    category = data_file.find("span",{"class":"category"})
    description = data_file.find("span",{"class":"description"})
    try:
        brand = data_file.find("span",{"class":"brand"}).text
    except Exception:
        brand = ""
    try:
        alternate_image_url = data_file.find("span",{"class":"alternate_image_url"}).text
    except Exception as e:
        alternate_image_url = ""
    date_published = data_file.find("span",{"class":"date_published"})
    ## OPTIONS ##
    options_list = []
    options = soup.select(".product-article__footer__menu-content__features__tr")
    if options:
        for option in options:
            key = (option.find_all("td",{"class":"product-article__footer__menu-content__features__tr__td"})[0])
            value = (option.find_all("td", {"class": "product-article__footer__menu-content__features__tr__td"})[1])
            options_list.append([key.text.strip(),value.text.strip().replace("\n"," / ")])
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
        categories_list.append([category.text,link])
    item = {
        "product_id":product_id.text,
        "name":name.text,
        "image_url":image_url.text,
        "category":category.text,
        "description":description.text,
        "brand":brand,
        "alternate_image_url":alternate_image_url,
        "date_published":date_published.text,
        "options_list":options_list,
        "compatibility":compatibility_bool,
        "categories":categories_list
    }
    return((item))

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
    avec_piece = 0
    created_at = ""
    updated_at = ""
    visibilite = 0
    return {
        "id":produit_id,
        "name":name,
        "slug":slug,
        "description":description,
        "categ_id":categ_id,
        "marque_id":marque_id,
        "created_at":created_at,
        "updated_at":updated_at,
        "visibilite":visibilite
    }


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
        if opt == False:
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

def variante_table(variante):
    """
    Gets back Variante Row.

    :param vairiante: Variante to Model
    :return: Product Variante Table Row in JSON.
    """
    couleur = variante["attribute1"]
    try:
        taille = variante["attribute2"]["title"].replace("(Indisponible dans ce coloris)","").strip()
    except Exception as e:
        taille = ""
    quantite = 0
    prix_vente = 0
    prix_promo = 0
    created_at = ""
    updated_at = ""
    ref = ""
    return {
        "id": variante["variante_id"],
        "produit_id": variante["produit_id"],
        "couleur" : couleur["title"],
        "taille":taille,
        "quantite": quantite,
        "qualite": "",
        "prix_vente": prix_vente,
        "prix_promo": prix_promo,
        "created_at": created_at,
        "updated_at": updated_at,
        "ref":ref
    }

def variante_photo_table(variante,principale_holder):
    """
    Gets back Variante Photo Row.

    :param variante: Product Variante to Model.
    :return: Product Variante Photo Model Row in JSON Format.
    """
    couleur = variante["attribute1"]["title"]
    try:
        photo = variante["attribute1"]["url"]
    except Exception as e:
        photo = ""
    created_at = ""
    updated_at = ""
    return {
        "id": variante["variante_photo_id"],
        "produit_id" : variante["produit_id"],
        "couleur": couleur,
        "photo":photo,
        "principale" : principale_holder,
        "created_at" : created_at,
        "updated_at": updated_at
    }

def fetch_data(variante):
    """
    This function retrieves all data required for a variante and put in different tables associated to our Db Model.

    :param variante: Variante url.
    :return: None.
    """
    global variante_id
    global produit_id
    global variante_photo_id
    global product_rows  # Product Table
    global variantes_rows  # Variantes Table
    global variantes_photos_rows  # Variantes Photos Table
    global options_rows  # Options Table
    global options_product_rows  # Options Product Table

    variants = get_variants(link)
    var_data = (get_variants_data(variants))
    product_details = (get_variants_details(var_data[0]))
    product_details["title"] = link.replace("https://www.dafy-moto.com/", "").replace(".html", "").replace("-",
                                                                                                           " ").title()
    product_row = (produit_table(product_details))
    product_rows.append(product_row)
    options = option_table(product_details)
    [options_rows.append(option) for option in options]
    options_produit = produit_option(options, produit_id)
    [options_product_rows.append(option_product) for option_product in options_produit]
    list_varaintes = []
    list_variantes_photos = []

    couleur = ""
    for variante in var_data: # Tailles of variante
        if variante["attribute1"]["title"] != couleur:
            principale_holder = 1
        else:
            principale_holder = 0
        variante["variante_id"] = variante_id
        variante["produit_id"] = produit_id
        list_varaintes.append(variante_table(variante))
        variante["variante_photo_id"] = variante_photo_id
        list_variantes_photos.append(variante_photo_table(variante, principale_holder))
        couleur = variante["attribute1"]["title"]
        variante_id += 1
        variante_photo_id += 1
    [variantes_rows.append(variante) for variante in list_varaintes]
    [variantes_photos_rows.append(variante_photo) for variante_photo in list_variantes_photos]
    print("TABLE OPTIONS")
    print(json.dumps(options))
    print("TABLE OPTIONS PRODUT")
    print(json.dumps(options_produit))
    print("TABLE PRODUITS")
    print(json.dumps(product_row))
    print("TABLE VARIANTES")
    print(json.dumps(list_varaintes))
    print("TABLE VARIANTE PHOTOS")
    print(json.dumps(list_variantes_photos))
    print("--------------")

    produit_id += 1
    return var_data

def save_data_json(data,file_name):
    """
    Helps with saving dict list on json file.

    :param data: Dictionary List.
    :param file_name: Json Filename.
    :return: None.
    """
    with open("data/{}.json".format(file_name), "w", encoding="utf-8") as jsonfile:
        json.dump(data, jsonfile, ensure_ascii=False)


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

if __name__ == '__main__':
    variants_rows = csv_tulple("input/dafy_withlinks.csv")
    for variant_row in variants_rows:
        link = (variant_row["LIEN DAFY.COM"])
        if re.match(link_regex,link) is not None:
            try:
                fetch_data(link)
            except Exception as e:
                print(e)
    save_data_json(product_rows, "products")
    save_data_json(variantes_rows, "variantes")
    save_data_json(variantes_photos_rows, "variantes_photos")
    save_data_json(options_rows, "options")
    save_data_json(options_product_rows, "options_products")


