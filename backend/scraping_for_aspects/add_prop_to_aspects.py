

path = "E:\\master\\anul1\\sem22\\sw\\proiect\\ontology_creation\\all_aspects.txt"
with open(path,'r', encoding='utf-8') as f:
    content = f.readlines()
    
def retrieve_aspect_names(content):
    # :Aspect_diagonala_display rdf:type owl:NamedIndividual ,
    instances = []
    for line in content:
        if str(line).startswith(":Aspect_"):
            aspect_node = line.split(" ")
            aspect_node = aspect_node[0]
            aspect_name = aspect_node.split(':Aspect_')
            aspect_name = aspect_name[1]
            instances.append((aspect_node,aspect_name))
    return instances

def create_triplets(instances):
    template = """:isAbout rdf:type owl:ObjectProperty ;
                   rdfs:domain :Aspect .\n"""
    for aspect_node, aspect_name in instances:
        template += f"""{aspect_node} :isAbout \"{aspect_name}\" .\n"""
    return template

instances = retrieve_aspect_names(content)
triplets  = create_triplets(instances)
print(triplets)

with open("out.txt",'w', encoding='utf-8') as f:
    f.write(triplets)
