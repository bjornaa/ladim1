# import pprint
import yaml

f = open("test.yaml")

A = yaml.safe_load(f)

# pprint.pprint(A)

print(yaml.dump(A))
