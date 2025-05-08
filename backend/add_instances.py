'''
:Notino rdf:type owl:NamedIndividual ,
                 :Website .

Available classes:
VacuumCleaner,Tripod, TV,SquashRacket, Ski, Scooter,PCAudioSpeakers,Microphone,GamingHeadset, FitnessBike, DeskChair, ControllerAndSteeringWheel,Boots


'''

import json
import pandas as pd
import re

# file_path_decathlon = 'decathlon_products.json'
# file_path_emag = 'emag.json'

# file_path_altex = 'altex_reviews.json'
# file_path_altex = 'altex_reviews_gaming_headset.json'
# file_path_altex = 'altex_reviews_fitness_bike.json'
# file_path_altex = 'altex_reviews_tv.json'
# file_path_altex = 'altex_reviews_scooter.json'
file_path_altex = 'altex_reviews_controllers.json'

with open(file_path_altex,encoding='utf-8') as f:
    rev_json = json.loads(f.read())

# df_decathlon =  pd.DataFrame.from_records(rev_json)
# df_decathlon['website']='Decathlon'

df_altex =  pd.DataFrame.from_records(rev_json)
df_altex['website']='Altex'
df_altex.drop_duplicates(inplace=True)

"""
###  http://www.semanticweb.org/alina/ontologies/2023/3/reviews_ontology#Review114837_2
:Review114837_2 rdf:type owl:NamedIndividual ,
                         rev:Review ;
                rev:text "Un trepied de slaba calitate, nu recomand." ;
                :aggregatesOpinion marl:Negative ;
                :hasAuthor "Antonescu Marian" ;
                :hasRating 3 .

###  http://www.semanticweb.org/alina/ontologies/2023/3/reviews_ontology#Trepied114837
:Trepied114837 rdf:type owl:NamedIndividual ,
                        :Product ;
               :belongsTo :Tripod ;
               :hasWebsite :Altex ;
               :aggregatesRating 2.0 ;
               :hasReview :Review114837_1 , :Review114837_2 ;
               :hasTitle "Trepied foto auriu" .
{"product_code": "866425", "product_title": "Bocanci Mid ", "average_rating": 4.12, "text": "SUNT USORI SI FOARTE COMOZI", 
"rating": 5, "author": "Ruxandra", "country": "RO", "most_inner_category": "Boots"},

"""

def generate_instance_name_product(code):
    if '&' in str(code):
        code = re.sub('&','',code)
    return "Product"+str(code)

def generate_instance_name_review(code,index):
    if '&' in str(code):
        code = re.sub('&','',code)
    return "Review"+str(code)+"_"+str(index)

def get_triplet_for_review(row,instance_name):
    text = row['text']
    text = re.sub("\""," ",text)
    text = re.sub("\\n"," ",text)
    
    triplet_text = ":" + instance_name +  " rdf:type owl:NamedIndividual , rev:Review ; rev:text " 
    triplet_text += "\"" + text + "\"" +  " ;"
    triplet_text += " :hasAuthor " + "\"" + row['author'] + "\"" +" ;"
    triplet_text += " :hasRating " + str(row['rating']) + " ;"
    triplet_text += " :aggregatesOpinion "
    if int(row['rating']) < 4:
        triplet_text += "marl:Negative ."
    if int(row['rating']) == 4:
        triplet_text += "marl:Neutral ."
    if int(row['rating']) == 5:
        triplet_text += "marl:Positive ."
    
    return triplet_text
     
def get_triplet_for_product(row,reviews_instances):
    if len(reviews_instances) > 0:
        instance_name = generate_instance_name_product(row['product_code'])
        title = "\"" + row['product_title'] +  "\""
        
        template = f":{instance_name} rdf:type owl:NamedIndividual ,\n\
                            :Product ;\n\
                :hasTitle {title} ;\n\
                :belongsTo :{row['most_inner_category']} ;\n\
                :hasWebsite :{row['website']} ;\n\
                :aggregatesRating {row['average_rating']} ;" + '\n'
                
        template += "               :hasReview"
        for review in reviews_instances:
            template += " :" + review + " ,"
        
        template = template[:-2]
        template += ' .\n'
        return template
    else:
        return ""

def check_text(text):
    text_len = len(text.split(' '))
    if text_len < 3:
        return False
    if text_len > 300:
        return False
    return True

def get_reviews_for_code(df, code):
    df_current = df[df['product_code']==code]
    df_current = df_current[df_current['country']=='RO']
    reviews = []
    reviews_instances_name = []
    idx = 0
    for _, row in df_current.iterrows():
        idx += 1
        instance_name = generate_instance_name_review(row['product_code'], idx)
        text = row['text']
        if check_text(text):
            review_instance = get_triplet_for_review(row,instance_name)
            reviews.append(review_instance)
            reviews_instances_name.append(instance_name)
    return reviews, reviews_instances_name

def get_product_for_code(df, code, reviews_instances):
    df_current = df[df['product_code']==code]
    product = ""
    for _, row in df_current.iterrows():
        product = get_triplet_for_product(row, reviews_instances)
        break
    return product

def get_all_triplets(df):
    all_reviews = []
    all_products = []
    for _, row in df.iterrows():
        code = row['product_code']
        reviews, reviews_instances_name = get_reviews_for_code(df, code )
        
        for rev in reviews:
            all_reviews.append(rev)
            
        product = get_product_for_code(df,code,reviews_instances_name)
        if product:
            all_products.append(product)
        df = df[df.product_code != code]

    return all_reviews, all_products

all_reviews, all_products = get_all_triplets(df_altex)
print(all_reviews[0])
print("*"*80)
print(all_products[0])

def write_reviews_to_file(filename, reviews):
    with open(filename,'w', encoding='utf-8') as f:
        for rev in reviews:
            f.write(rev)
            f.write("\n\n")

def write_products_to_file(filename,all_products):
    with open(filename,'w', encoding='utf-8') as f:
        for prod in all_products:
            f.write(prod)
            
write_reviews_to_file('reviews_altex_controllers.txt', all_reviews)
write_products_to_file('products_altex_controllers.txt',all_products)