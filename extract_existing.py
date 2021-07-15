"""
This module helps with matching existing website data with G8 with links dataset.

"""
import requests,re, json,sys,csv,logging
from bs4 import BeautifulSoup
from retrying import retry
import pandas as pd

def read_json(json_link):
    """
    This function retrieves data from JSON file.

    :param json_link: JSON File Path.
    :return: Dictionary List.
    """
    with open(json_link,mode='r',encoding='utf-8') as jsonfile:
        return json.load(jsonfile)

def read_csv(csv_link):
    """
    This function retrieves data from CSV file.

    :param csv_link: CSV File Path.
    :return: Dictionary List.
    """
    df = pd.read_csv(csv_link,delimiter=',')
    df = df[df['LIEN DAFY.COM']=="plus en ligne, conserver la fiche produit actuelle"]
    return df.to_dict('records')

def fetch_product_byid(id,product_dataset):
    """
    this function retrieves id from dataset product by id.

    :param id: Product Id.
    :return: Product Dictionary.
    """
    for product in product_dataset :
        if product["id"] == id:
            return product

def fetch_byproduct_id(id,product_dataset):
    """
    this function retrieves id from dataset variante photos by id.

    :param id: Product Id.
    :return: Variante Photo Dictionary.
    """
    for variante_photos in product_dataset :
        if variante_photos["produit_id"] == id:
            return variante_photos


def save_data_json(data,file_name):
    """
    Helps with saving dict list on json file.

    :param data: Dictionary List.
    :param file_name: Json Filename.
    :return: None.
    """
    with open("data/{}.json".format(file_name), "w", encoding="utf-8") as jsonfile:
        json.dump(data, jsonfile, ensure_ascii=False)

def update_taille(dataset):
    """
    This function helps with cleaning Taille Row.

    :param dataset: Dateset of Variantes to Clean.
    :return: Dict List of Variantes.
    """
    new_l = []
    for row in dataset:
        row["taille"] = re.sub('\(([^\)]+)\)', '',row["taille"])
        new_l.append(row)
    return new_l


if __name__ == '__main__':
    product_list = []
    variante_list = []
    variante_photos_list = []
    produit_options_list = []
    options_list= []

    product_dataset = read_json("existing-data/produits.json")
    variante_photos_dataset = read_json("existing-data/produit_variante_photos.json")
    produit_options_dataset = read_json("existing-data/produit_options.json")
    options_dataset = read_json("existing-data/options.json")
    input_data = (read_csv("input/dafy_withlinks.csv"))
    existing_data = read_json("existing-data/produit_variantes.json")
    for existing_row in existing_data:
        for input_row in input_data:
            if str(existing_row["ref"]) in str(input_row["Code barre"]):
                variante_list.append(existing_row)

                product = fetch_product_byid(existing_row["produit_id"],product_dataset)
                product_list.append(product)

                variante_photo = fetch_byproduct_id(existing_row["produit_id"],variante_photos_dataset)
                variante_photos_list.append(variante_photo)

                produit_option = fetch_byproduct_id(existing_row["produit_id"],produit_options_dataset)
                produit_options_list.append(produit_option)

                break

    exisintg_variantes = read_json("/Users/mac/Downloads/DafyExtract/ExtractAllProducts/link-data/variantes.json")
    product_list = [i for n, i in enumerate(product_list) if i not in product_list[n + 1:]]
    produit_options_list = [i for n, i in enumerate(produit_options_list) if i not in produit_options_list[n + 1:]]
    save_data_json(product_list, "products")
    save_data_json(variante_list, "variantes")
    save_data_json(variante_photos_list, "variantes_photos")
    save_data_json(produit_options_list, "options_product")
    save_data_json(update_taille(exisintg_variantes), "update_variantes_list")







