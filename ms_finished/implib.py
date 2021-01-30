from sip import *

df=stocks_in_play()
print(df)

df.to_csv('/Users/estefhanymorenovega/Market_Scanner/ms_finished/sip.csv', index= False)

