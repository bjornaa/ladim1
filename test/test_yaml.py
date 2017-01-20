import pprint
import yaml

f = open('../ladim.yaml')

A = yaml.safe_load(f)

# pprint.pprint(A)

print(yaml.dump(A))

v = A['time_control']

print(v)
print(type(v))
