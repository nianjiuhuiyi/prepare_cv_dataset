import json


"""
# 这是工具台的
trans_dict = dict(
    圆柱滚子轴承="YZGZZC1",
    圆柱滚子轴承内圈="YZGZZCNQ",
    圆锥滚子轴承="YZGZZC",
    圆锥滚子轴承外圈="YZGZZCWQ",
    油封="YF",
    轴封="ZF",
    电动扳手套筒="DDBSTT",
    轴头螺母="ZTLM",
    波形弹簧圈="BXTHQ",
    调整垫片="TZDP",
    紧固胶="JGJ",
    厌氧胶="YYJ",
    密封胶="MFJ",
    内六角扳手="NLJBS",
    开口扳手="KKBS",
    扭矩扳手="NJBS",
    塞尺="SC",
    橡皮锤="XPC",
    铜棒="TB",
    铁锤="TC",
    M6螺栓="M6LS",
    M8螺栓="M8LS",
    SKF冲击筒="SKFCJT",
    阴阳转子="YYZZ",
    前端盖="QDG",
    排气端端盖="PQDDG",
    排气端轴承座端面="PQDZCZDM",
    导向套="DXT",
    定位销="DWX",
    SKF冲击环="SKFCJH",
    电动扳手="DDBS",
    润滑油="RHY",
    美孚润滑脂="MFRHZ"
)
"""

trans_dict = dict(
    手="HAND",
    排气端轴承座正面="PQDZCZ01",
    排气端轴承座反面="PQDZCZ02",
    排气端轴承座侧面="PQDZCZ03",
    圆锥滚子轴承="YZGZZC",
    阴阳转子="YYZZ",
    隔热手套="GRST",
    电动扳手="DDBS",
    紧固胶="JGJ",
    前端盖正面="QDG01",
    前端盖反面="QDG02",
    美孚润滑脂="MFRHZ",
    SKF冲击筒="SKFCJT",
    橡皮锤="XPC",
    铁锤="TC",
    自制冲击筒="ZZCJT",
    厌氧胶="YYJ",
    密封胶="MFJ",
    圆柱滚子轴承内圈="YZGZZCNQ",
    新隔热手套="XGRST"
)

with open("./annotations.json", 'r', encoding="utf-8") as fp:
    data = json.load(fp)
print(data.keys())
categories = data.get("categories")

for cate in categories:
    name = cate["name"]
    cate["name"] = trans_dict.get(name)
    cate["supercategory"] = trans_dict.get(name)
data["categories"] = categories

with open("./new_annotations.json", 'w', encoding="utf-8") as fp:
    json.dump(data, fp)
print("Done!")
