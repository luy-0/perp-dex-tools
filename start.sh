source ./env/bin/activate
# python runbot.py --exchange aster --ticker BTC --quantity 0.001 --take-profit 0.02 --max-orders 40 --wait-time 450
# python runbot.py --exchange aster --ticker BTC --direction sell --quantity 0.001 --take-profit 0.02 --max-orders 15 --wait-time 450

python runbot.py --exchange grvt --ticker BTC --quantity 0.005 --grid-step 0.25 --take-profit 0.02 --max-orders 40 --wait-time 450
# 当前价格 = 121964 
# 每个网格间隔价格 = 121964 * (0.25/100)  # grid-step  
# 最多持有头寸:  0.005 * 40
# 网格边界 = 121964 * ( 1 - (0.25/100) * 40)