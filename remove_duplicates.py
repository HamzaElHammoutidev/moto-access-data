import pandas as pd
import json



def read_json(json_link):
    """
    This function retrieves data from JSON file.

    :param json_link: JSON File Path.
    :return: Dictionary List.
    """
    with open(json_link,mode='r',encoding='utf-8') as jsonfile:
        return json.load(jsonfile)


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


def save_data_json(data,file_name):
    """
    Helps with saving dict list on json file.

    :param data: Dictionary List.
    :param file_name: Json Filename.
    :return: None.
    """
    with open("data/{}.json".format(file_name), "w", encoding="utf-8") as jsonfile:
        json.dump(data, jsonfile, ensure_ascii=False)


def collect_duplicates_ids(clean_dataset, dataset):
    """
    This funciton helps with collecting duplicates IDs.

    :param clean_dataset: Clean Dataset to fetch products to compare from.
    :param dataset: Dataset to collect duplicates IDs from.
    :return: dictionary with name of duplicate and its IDs.
    """
    total_list = []
    for clean_product in clean_dataset:
        product_list = []
        for product in dataset:
            if clean_product["name"] == product["name"]:
                product_list.append(product["id"])
        total_list.append({
            "product_name":clean_product["name"],
            "product_id": clean_product["id"],
            "products_ids": product_list
        })

    return total_list


def transform_dataset(ids_dataset,input_dataset,key):
    """
    This function helps with transformation duplicates IDs to uniques Id

    :param ids_dataset: Dataset with collected IDs of a single product
    :param input_dataset: Dataset to clean.
    :return: clean dataset.
    """
    new_list = []
    for item in input_dataset:
        for product in ids_dataset:
            for id in product["products_ids"]:
                if item["produit_id"] == id:
                    item[key] = product["product_id"]
                    new_list.append(item)
                    # break
        else:
            new_list.append(item)
    return new_list

def read_csv(csv_link):
    """
    This function retrieves data from CSV file.

    :param csv_link: CSV File Path.
    :return: Dictionary List.
    """
    df = pd.read_csv(csv_link,delimiter=',')
    return df.to_dict('records')


def setup_couleur(dataset):
    """
    This function helps with editing colors col.
    
    :param dataset: Dataset to update.
    :return: clean dataset.
    """
    new_dataset = []
    for variante in dataset:
        try:
            variante["couleur"] = variante["couleur"].replace("/",",")
        except Exception as e:
            variante["couleur"] = variante["couleur"]
        new_dataset.append(variante)

    return new_dataset

if __name__ == '__main__':
    """
    products = read_json("link-data/products.json")
    variantes = read_json("data/update_variantes_list.json")
    variantes_photos = read_json("link-data/variantes_photos.json")
    option_products = read_json("link-data/options_products.json")
    print(len(products))
    new_products = remove_duplicates(products,"name")
    print("products : {}".format(len(new_products)))
    collected_duplicates = collect_duplicates_ids(new_products,products)

    save_data_json(new_products,"new_products")

    new_option_products = transform_dataset(collected_duplicates,option_products,"produit_id")
    print(len(new_option_products))
    new_option_products = remove_duplicates(new_option_products,["produit_id","option_id"])
    print("products options {}".format(str(len(new_option_products))))

    save_data_json(new_option_products,"new_option_products")

    new_variantes = transform_dataset(collected_duplicates,variantes,"produit_id")
    print(len(new_variantes))
    new_variantes = remove_duplicates(new_variantes, ["produit_id","couleur","taille"])
    print("variantes {}".format(len(new_variantes)))
    
    new_variantes = setup_couleur(new_variantes)

    save_data_json(new_variantes,"new_variantes")

    new_variantes_photos = transform_dataset(collected_duplicates, variantes_photos, "produit_id")
    print(len(new_variantes_photos))
    new_variantes_photos = remove_duplicates(new_variantes_photos, ["produit_id","couleur","photo"])
    print("variantes photos  {}".format(len(new_variantes_photos)))

    new_variantes_photos = setup_couleur(new_variantes_photos)


    save_data_json(new_variantes_photos,"new_variantes_photos")

    """
    variantes = read_json("data/new_variantes.json")
    dafy_data = read_csv("input/dafy_withlinks.csv")
    new_list = []
    for variante in variantes:
        for prod in dafy_data:
           if variante["ref"] in prod["Code barre"]:
               variante["prix_vente"] = int(float(prod["Prix T.T.C."].replace("Dh","").replace(",","").strip()))
               print(variante["prix_vente"])
               new_list.append(variante)
               
    save_data_json(new_list,"upd_variantes")      

