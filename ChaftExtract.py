import requests,json
from bs4 import BeautifulSoup



def produit_table(produit):
    """
    Gets back Product Table Row.

    :param produit: Product to form on Table Mode.
    :return: Product Row.
    """
    global produit_id

    if produit["category"] == "LEVIERS":
        categ_id = 281
    elif 'ECHAPPEMENTS' in  produit["category"]:
        categ_id = 173
    elif 'OUTILLAGE' in produit["category"]:
        categ_id = 222
    elif 'BEQUILLES' in produit["category"]:
        categ_id = 147
    elif 'ELECTRIQUES' in produit["category"]:
        categ_id = 172
    elif 'PILOTE' in produit["category"]:
        categ_id = 243
    elif "ACCESSOIRES DIVERS MOTOS/AUTO" == produit["category"]:
        categ_id = 160
    elif 'ANTIVOLS U' in produit["category"]:
        categ_id = 214
    elif 'CHARGEUR' in produit["category"]:
        categ_id = 223
    elif 'CLIGNOTANTS' in produit["category"]:
        categ_id = 153
    elif 'RETROVISEURS' in produit["category"]:
        categ_id = 161
    else:
        categ_id = 10


    name = produit["title"]
    slug = produit["title"].replace(" ","-").lower()
    description = produit["description"]
    #categ_id = get_categoriesId(produit["categories"][-1][1])
    marque_id = 152
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


def variante_table(variante,file_variant):
    """
    Gets back Variant Row.

    :param vairiante: Variante to Model
    :return: Product Variante Table Row in JSON.
    """
    #print(variante)
    couleur = file_variant["Couleur"]
    if couleur is None:
        couleur = ""
    try:
        taille = file_variant["Taille"]
        if taille is None:
            taille = ""
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


def DownloadImage(url):
    response = requests.get(url)
    mainfolder = "images_chaft/"
    name = url.split("/")[-2].replace("/","-") +"-"+ url.split("/")[-1].replace("/","-")
    file = open(mainfolder+name, "wb")
    file.write(response.content)
    file.close()
    return mainfolder+name


def fetch_photo(photo):
    try:
        n = DownloadImage(photo)
    except Exception as e:
        print(photo["photo"], e)
    print(photo)
    return ("produit_variante_photos/Tester/"+n.replace("images_chaft/",""))


def variante_photo_table(variante):
    """
    Gets back Variant Photo Row.

    :param variante: Product Variante to Model.
    :return: Product Variante Photo Model Row in JSON Format.
    """
    global variante_photo_id
    photos_list = []
    couleur = variante["Couleur"]
    for photo in variante["images"]:
        if photo == variante["images"][0]:
            _principal_holder = 1
        else:
            _principal_holder = 0
        created_at = ""
        updated_at = ""
        photos_list.append({
            "id": variante_photo_id,
            "produit_id": variante["produit_id"],
            "couleur": couleur,
            "photo": fetch_photo(photo),
            "principale": _principal_holder,
            "created_at": created_at,
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
    with open("data/{}.json".format(file_name), "w", encoding="utf-8") as jsonfile:
        json.dump(data, jsonfile, ensure_ascii=False)


if __name__ == '__main__':

    variante_id = 20000
    produit_id = 20000
    variante_photo_id = 20000

    product_rows = []
    variantes_rows = []
    variantes_photos_rows = []
    options_rows = []
    options_product_rows = []

    data = csv_tulple("/Users/mac/Downloads/DafyExtract/ExtractAllProducts/input/20210724-NOUVEL-ARRIVAGE-CHAFT.csv")

    for item in data:
        if item["site dafy"] == "KO":
            soup = get_page_content(item["site chaft"])
            title = soup.find("h1",{'itemprop':'name'}).text
            description = soup.find('div',{'id':"producttab-description"})
            #print(title)
            #print(description)
            images_header = soup.find('ul',{'id':'thumbs_list_frame'})
            images = images_header.find_all('img')
            category = item["Catégorie"]
            images_list = []
            for image in images:
                images_list.append(image["src"].replace("-cart","-thickbox"))

            product = {
                "id":produit_id,
                "title":title,
                "description":description,
                "avec_piece":1,
                "category":category,
                "images":images_list,
                "Couleur":item["Couleur"]
            }

            product_rows.append(produit_table(product))
            product["variante_id"] = variante_id
            product["produit_id"] = product['id']

            variantes_rows.append(variante_table(product,item))
            [variantes_photos_rows.append(variante_photo) for variante_photo in variante_photo_table(product)]

            print(produit_table(product))
            print(variante_photo_table(product))
            variante_id += 1
            produit_id += 1
    save_data_json(product_rows, "chaft_products")
    save_data_json(variantes_rows, "chaft_variantes")
    save_data_json(variantes_photos_rows, "chaft_variantes_photos")
