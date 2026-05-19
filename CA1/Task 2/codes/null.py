import pandas as pd
df = pd.read_csv("../TB_Burden_Country.csv")
res= df.isnull().sum()
print(res)