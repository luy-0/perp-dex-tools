source ./env/bin/activate
# python runbot.py --exchange aster --ticker BTC --quantity 0.001 --take-profit 0.02 --max-orders 40 --wait-time 450
# python runbot.py --exchange aster --ticker BTC --direction sell --quantity 0.001 --take-profit 0.02 --max-orders 15 --wait-time 450

python runbot.py --exchange grvt --ticker BTC --quantity 0.005 --grid-step 0.05 --take-profit 0.02 --max-orders 40 --wait-time 450
# 121964 * (1-(40*0.03/100))