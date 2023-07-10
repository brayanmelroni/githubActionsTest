import pandas as pd
states = ["A","B","C","D"]
print([
    states[3],
    states[-1],
    states[-4]
])

for state in states:
    if state == "Florida":
        print(state.text)

# file will be closed as soon as we leave with block. 
with open('test.txt','w') as file:
    file.write('data successfullt scraped')


# create a data frame using a dictioary. 
states2= ["California","Texas","Florida","New York"]
population=[39613493, 29730311, 21944577, 19299981]
dict_states = {'States': states, 'Population': population}
df_states = pd.DataFrame.from_dict(dict_states)
print(df_states)
df_states.to_csv('states.csv', index=False)

# exceptions
new_list = [2,4,6,'California']
for element in new_list:
    try:
        print(element/2)
    except:
        print("Non numeric element")

#  while loop
n=4
while n>0:
    print(n)
    if n == 2:
        break
    n=n-1








