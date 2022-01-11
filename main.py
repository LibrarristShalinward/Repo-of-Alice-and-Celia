from chart.chart_op import PoliciedChart
import argparse

def policize(chart_name, cpr_level = 2): 
    plc_chart = PoliciedChart("谱面/" + chart_name + ".json")
    plc_chart(chart_name + ".a&c", cpr_level)

if __name__ == "__main__": 
    parser = argparse.ArgumentParser("Deemo谱面指法生成器")

    parser.add_argument("-c", "--chart")
    parser.add_argument("-l", "--level", default = 2)
    args = parser.parse_args()

    policize(args.chart, args.level)