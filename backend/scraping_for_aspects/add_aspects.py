import json
import pandas as pd
import re

# ontology TO USE : https://gpc-browser.gs1.org/   -- http://www.gs1.org/gpc/[GPCcode]

# path_aspects = 'E:\\master\\anul1\\sem22\\sw\\proiect\\ontology_creation\\emag_with_aspects.json'
# path_products = 'E:\\master\\anul1\\sem22\\sw\\proiect\\ontology_creation\\emag.json'

# path_aspects = 'E:\\master\\anul1\\sem22\\sw\\proiect\\ontology_creation\\decathlon_aspects.json'
# path_products = 'E:\\master\\anul1\\sem22\\sw\\proiect\\ontology_creation\\decathlon_products.json'

path_aspects = 'E:\\master\\anul1\\sem22\\sw\\proiect\\ontology_creation\\altex_with_aspects.json'
path_products = 'E:\\master\\anul1\\sem22\\sw\\proiect\\ontology_creation\\altex_reviews_all.json'

saved_aspects = []

with open(path_products,encoding='utf-8') as f:
    items = json.loads(f.read())

with open(path_aspects,encoding='utf-8') as f:
    items_with_aspects = json.loads(f.read())

df_aspects =  pd.DataFrame.from_records(items_with_aspects)
df_aspects.drop_duplicates(inplace=True)

df_items = pd.DataFrame.from_records(items)
df_items.drop_duplicates(inplace=True)

df_merged = pd.merge(df_items, df_aspects, how ='inner', on =['product_code'])
df_merged.dropna(subset=['aspects'], inplace=True)
df_merged.drop_duplicates(subset=['product_code'], inplace=True)
print(df_merged)
df_merged.to_csv('dummy.csv')
assert len(df_merged['aspects'])==len(df_merged)

def generate_instance_name_aspect_list(aspect_list):
    aspects = aspect_list.split('|')
    aspects = [a.strip().split(' ') for a in aspects]
    aspects = ['_'.join(a) for a in aspects]
    aspects = ['Aspect_'+ a.lower() for a in aspects]
    aspects = [a for a in aspects if a not in saved_aspects]
    return aspects


def get_triplet_for_product_aspects(row):
    aspects_name = generate_instance_name_aspect_list(row['aspects'])
    if len(aspects_name)> 1:
        saved_aspects.extend(aspects_name)
    
    product_code = str(row['product_code'])
    if '&' in str(product_code):
        product_code = re.sub('&','',product_code)
    product_instance ='Product'+product_code 
    
    template_aspects = ""
    for a in aspects_name:
        template_aspects += f":{a} rdf:type owl:NamedIndividual ,\n\
                            :Aspect .\n"
    
    template_product = f":{product_instance}    marl:DescribesFeature"
    original_aspect_list = row['aspects']
    original_aspect_list = original_aspect_list.split('|')
    original_aspect_list = [a.strip().split(' ') for a in original_aspect_list]
    original_aspect_list = ['_'.join(a) for a in original_aspect_list]
    
    for a in original_aspect_list:
        template_product += " :" + 'Aspect_'+ a.lower() + " ,"
    
    template_product = template_product[:-2]
    template_product += ' .\n'
    return template_aspects, template_product


def get_all_triplets(df):
    aspects = []
    products = []
    for _, row in df.iterrows():
        aspect, product = get_triplet_for_product_aspects(row)
        if len(aspect) > 1:
            aspects.append(aspect)
        if len(product) > 1:
            products.extend(product) 
        print('Added: ', product)
        
    return aspects, products


def write_aspects_to_file(filename, aspects):
    with open(filename,'w', encoding='utf-8') as f:
        for a in aspects:
            f.write(a)
            f.write("\n\n")


def write_products_to_file(filename,products):
    with open(filename,'w', encoding='utf-8') as f:
        for prod in products:
            f.write(prod)


all_aspects, all_products = get_all_triplets(df_merged)
print(all_aspects[0])
print("*"*80)
print(all_products[0])

write_aspects_to_file('aspects_altex.txt', all_aspects)
write_products_to_file('products_altex_with_aspects.txt',all_products)
