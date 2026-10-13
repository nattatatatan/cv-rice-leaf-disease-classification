"""CSCI935 rice leaf disease classification (white vs field background)

Group: group3-starvenus

GENERATED FILE - DO NOT EDIT. It is built from the notebooks in notebooks/ by
tools/export_py.py. Edit the notebooks and re-run the export instead.

Run `python group3-starvenus.py --help` to list the commands.
"""

# ---- embedded:annotations/duplicate_groups.json ----
# Embedded from annotations/duplicate_groups.json by tools/export_py.py. Edit that file, not this block.
DUPLICATE_GROUPS = [
    ["bs_wb_4.jpg", "bs_wb_5.jpg"],
    ["bs_wb_55.jpg", "bs_wb_56.jpg"],
    ["bs_wb_80.jpg", "bs_wb_81.jpg"],
    ["bsf_0.jpg", "bsf_1.jpg"],
    ["bsf_2.jpg", "bsf_3.jpg"],
    ["bsf_4.jpg", "bsf_5.jpg"],
    ["bsf_7.jpg", "bsf_8.jpg"],
    ["bsf_15.jpg", "bsf_16.jpg"],
    ["ls_wb_1.jpg", "ls_wb_2.jpg"],
    ["ls_wb_85.jpg", "ls_wb_86.jpg"],
    ["ls_wb_99.jpg", "ls_wb_100.jpg"],
    ["lsf_0.jpg", "lsf_1.jpg"],
    ["lsf_6.jpg", "lsf_7.jpg"],
    ["lsf_12.jpg", "lsf_23.jpg"],
    ["lsf_34.jpg", "lsf_45.jpg"],
    ["lsf_67.jpg", "lsf_72.jpg"],
    ["rb_wb_20.jpg", "rb_wb_21.jpg"],
    ["rb_wb_91.jpg", "rb_wb_92.jpg"],
    ["rb_wb_113.jpg", "rb_wb_114.jpg"],
    ["rb_wb_146.jpg", "rb_wb_147.jpg"],
    ["rb_wb_169.jpg", "rb_wb_170.jpg"],
    ["rb_wb_180.jpg", "rb_wb_181.jpg"],
    ["rbf_1.jpg", "rbf_2.jpg"],
    ["rbf_13.jpg", "rbf_14.jpg"],
    ["rbf_21.jpg", "rbf_22.jpg"],
    ["rtf_0.jpg", "rtf_1.jpg"],
    ["rtf_5.jpg", "rtf_6.jpg"],
    ["rtf_7.jpg", "rtf_8.jpg", "rtf_9.jpg", "rtf_10.jpg"],
    ["rtf_11.jpg", "rtf_12.jpg"],
    ["rtf_17.jpg", "rtf_18.jpg", "rtf_19.jpg"],
    ["rtf_20.jpg", "rtf_21.jpg"],
    ["rtf_22.jpg", "rtf_23.jpg"],
    ["rtf_25.jpg", "rtf_26.jpg", "rtf_27.jpg"],
    ["rtf_32.jpg", "rtf_33.jpg"],
    ["sb_wb_210.jpg", "sb_wb_211.jpg"],
    ["sbf_1.jpg", "sbf_19.jpg", "sbf_47.jpg"],
]


# ---- embedded:annotations/white_rejects.json ----
# Embedded from annotations/white_rejects.json by tools/export_py.py. Edit that file, not this block.
WHITE_REJECTS = {
    "note": "T5.1 white pseudo-mask rejects: first pass by the agent, then Nattan's visual review of pseudo_mask_qc_*.png (MASK_V_MIN 20, MASK_CLOSE_KSIZE 45). 33 of 769 rejected (4.3%). A rejected leaf is never a composite source or a segmenter target. The review record is _work/results/white_mask_first_pass.txt.",
    "rejects": {
        "bs_wb_43.jpg": "train: torn, ragged leaf tip fragmented, tip lost",
        "bs_wb_48.jpg": "train: two torn leaves joined, pale lesion strip left out of the mask",
        "bs_wb_77.jpg": "test: pale yellow tip lost",
        "bs_wb_89.jpg": "val: borderline, pale strip at the lower left lost",
        "ls_wb_0.jpg": "train: dark blurred shadow/object at the lower right is included",
        "ls_wb_1.jpg": "test: two leaves and a shadow merged on greenish paper",
        "ls_wb_2.jpg": "test: cluttered close-up, fibres included",
        "ls_wb_30.jpg": "train: leaf end broken, pale lower part lost (ghost loop)",
        "ls_wb_4.jpg": "train: cluttered close-up, loose fibres included, lesion holes",
        "ls_wb_6.jpg": "val: borderline, ragged torn leaf",
        "rb_wb_1.jpg": "train: a second leaf and the dark shadow beside it are merged in",
        "rb_wb_30.jpg": "train: very ragged torn edge",
        "rb_wb_33.jpg": "train: mask loops along the torn edge, leaf split",
        "rb_wb_46.jpg": "train: Nattan, visual review",
        "rb_wb_49.jpg": "train: fibres/hairs attached to the leaf",
        "rb_wb_58.jpg": "test: fibres attached (also flagged by Nattan)",
        "rt_wb_16.jpg": "test: Nattan, visual review",
        "rt_wb_17.jpg": "train: Nattan, visual review",
        "rt_wb_18.jpg": "train: Nattan, visual review",
        "rt_wb_2.jpg": "train: straw-coloured lower tip lost",
        "rt_wb_26.jpg": "train: Nattan, visual review",
        "rt_wb_45.jpg": "train: Nattan, visual review",
        "rt_wb_46.jpg": "train: Nattan, visual review",
        "rt_wb_67.jpg": "test: straw-coloured tail lost",
        "sb_wb_111.jpg": "train: sun-bleached pale upper half lost (saturation equals paper)",
        "sb_wb_112.jpg": "train: sun-bleached pale upper half lost",
        "sb_wb_193.jpg": "train: pale upper half lost, only the lower leaf is masked",
        "sb_wb_201.jpg": "train: leaf below a lesion gap lost",
        "sb_wb_205.jpg": "test: second (crossing) leaf lost",
        "sb_wb_30.jpg": "train: pale upper strip lost",
        "sb_wb_5.jpg": "train: borderline, lesion notch at the leaf edge",
        "sb_wb_6.jpg": "train: borderline, lesion notches at the leaf edge",
        "sb_wb_70.jpg": "test: Nattan, visual review",
    },
}


# ---- embedded:annotations/field_salient_leaf.json ----
# Embedded from annotations/field_salient_leaf.json by tools/export_py.py. Edit that file, not this block.
FIELD_ANNOTATIONS = {
    "bsf_11.jpg": {
        "polygon": [
            [0.55028, 0.76525], [0.59566, 0.6865], [0.62948, 0.62292], [0.64603, 0.56474],
            [0.6733, 0.48851], [0.70182, 0.381], [0.71405, 0.28608], [0.71405, 0.27253],
            [0.75822, 0.24402], [0.81188, 0.2036], [0.91467, 0.07314], [0.92403, 0.01517],
            [0.87981, 0.06956], [0.83159, 0.1358], [0.80191, 0.15723], [0.72724, 0.22867],
            [0.68717, 0.28453], [0.64137, 0.33011], [0.60346, 0.38145], [0.53851, 0.54372],
            [0.5034, 0.64815],
        ],
        "ambiguous": True,
    },
    "bsf_25.jpg": {
        "polygon": [
            [0.53127, 0.83831], [0.55266, 0.81899], [0.51677, 0.78289], [0.47096, 0.74759],
            [0.41166, 0.67377], [0.37895, 0.6156], [0.34086, 0.56956], [0.33981, 0.51139],
            [0.34262, 0.47011], [0.32506, 0.43394], [0.3824, 0.28846], [0.45146, 0.27563],
            [0.53, 0.25952], [0.681, 0.22589], [0.51215, 0.24574], [0.43746, 0.25319],
            [0.36124, 0.26943], [0.29921, 0.29079], [0.26965, 0.31634], [0.25004, 0.36675],
            [0.24369, 0.40993], [0.24354, 0.4984], [0.25011, 0.55758], [0.26913, 0.61116],
            [0.30296, 0.64648], [0.35756, 0.71215], [0.38639, 0.75106], [0.44022, 0.78949],
        ],
        "ambiguous": False,
    },
    "bsf_35.jpg": {
        "polygon": [
            [0.383, 0.72093], [0.35363, 0.71337], [0.32025, 0.69648], [0.32025, 0.64047],
            [0.39972, 0.50867], [0.53403, 0.32364], [0.60195, 0.24827], [0.646, 0.20187],
            [0.70515, 0.14459], [0.81553, 0.00578], [0.86063, 0.00285], [0.70994, 0.27124],
            [0.69245, 0.33344], [0.65293, 0.37576], [0.59368, 0.45225], [0.53298, 0.53421],
            [0.48938, 0.62218], [0.44365, 0.68485], [0.43124, 0.71388], [0.42131, 0.72093],
        ],
        "ambiguous": False,
    },
    "bsf_41.jpg": {
        "polygon": [
            [0.45567, 0.61847], [0.50822, 0.61847], [0.54057, 0.60383], [0.5518, 0.49793],
            [0.58087, 0.37932], [0.63466, 0.18256], [0.65792, 0.10546], [0.68351, 0.06094],
            [0.7022, 0.05357], [0.64856, 0.04251], [0.60609, 0.05502], [0.58296, 0.07539],
            [0.56737, 0.09193], [0.55988, 0.12059], [0.53998, 0.15316], [0.53484, 0.18251],
            [0.53539, 0.22884], [0.5031, 0.27016], [0.5031, 0.2913], [0.49023, 0.33905],
            [0.48475, 0.37989], [0.46007, 0.49535], [0.45516, 0.56542],
        ],
        "ambiguous": False,
    },
    "bsf_46.jpg": {
        "polygon": [
            [0.45711, 0.74929], [0.68245, 0.4824], [0.77273, 0.38111], [0.84656, 0.28508],
            [0.92896, 0.18184], [1.0, 0.08533], [1.0, 0.00481], [0.87752, 0.00185],
            [0.64051, 0.36499], [0.59058, 0.46557], [0.52473, 0.57116], [0.44406, 0.71364],
        ],
        "ambiguous": False,
    },
    "bsf_5.jpg": {
        "polygon": [
            [0.50072, 0.13823], [0.54542, 0.1741], [0.62416, 0.39322], [0.64501, 0.56916],
            [0.63675, 0.70462], [0.62642, 0.78693], [0.58753, 0.77394], [0.54008, 0.45171],
            [0.49542, 0.27043], [0.45066, 0.14223],
        ],
        "ambiguous": False,
    },
    "lsf_21.jpg": {
        "polygon": [
            [0.43839, 0.99763], [0.45019, 0.86207], [0.454, 0.62964], [0.42818, 0.46593],
            [0.37404, 0.21434], [0.3429, 0.10969], [0.30633, 8e-05], [0.38984, 8e-05],
            [0.42679, 0.06998], [0.49191, 0.20871], [0.51964, 0.29086], [0.51964, 0.35804],
            [0.53925, 0.46644], [0.54888, 0.54275], [0.54694, 0.70455], [0.53334, 0.83487],
            [0.49523, 0.99548],
        ],
        "ambiguous": False,
    },
    "lsf_25.jpg": {
        "polygon": [
            [0.60946, 0.99684], [0.60694, 0.88171], [0.55464, 0.745], [0.41813, 0.44228],
            [0.34916, 0.24922], [0.30926, 0.10616], [0.28576, 0.00174], [0.44961, 0.00033],
            [0.49117, 0.10105], [0.54768, 0.25351], [0.58057, 0.35765], [0.61197, 0.46971],
            [0.66855, 0.77357], [0.67383, 0.82428], [0.6721, 0.87799], [0.66158, 0.92044],
        ],
        "ambiguous": False,
    },
    "lsf_3.jpg": {
        "polygon": [
            [0.55362, 0.67737], [0.57999, 0.66415], [0.65672, 0.51303], [0.74316, 0.37305],
            [0.76821, 0.30584], [0.78278, 0.25171], [0.78382, 0.19826], [0.81146, 0.16367],
            [0.90888, 0.16945], [0.93529, 0.16696], [0.78185, 0.15726], [0.77191, 0.16919],
            [0.76122, 0.18757], [0.74666, 0.22367], [0.73092, 0.26787], [0.7185, 0.31522],
            [0.69552, 0.35402],
        ],
        "ambiguous": True,
    },
    "lsf_49.jpg": {
        "polygon": [
            [0.54027, 0.80174], [0.53545, 0.76159], [0.51271, 0.74209], [0.48455, 0.70766],
            [0.46963, 0.67064], [0.45674, 0.58481], [0.45581, 0.55005], [0.44113, 0.50653],
            [0.4392, 0.4704], [0.44091, 0.41907], [0.44749, 0.37996], [0.44307, 0.36133],
            [0.31597, 0.04324], [0.29463, 0.00064], [0.31893, 0.00067], [0.40917, 0.23812],
            [0.48139, 0.36865], [0.49623, 0.42978], [0.51129, 0.47203], [0.51829, 0.53036],
            [0.52107, 0.58246], [0.53338, 0.638], [0.54764, 0.68689], [0.55093, 0.72596],
        ],
        "ambiguous": False,
    },
    "lsf_54.jpg": {
        "polygon": [
            [0.406, 0.66961], [0.43496, 0.61996], [0.43496, 0.58434], [0.50773, 0.43073],
            [0.57047, 0.37115], [0.60232, 0.32993], [0.62857, 0.29248], [0.67023, 0.24356],
            [0.70346, 0.19936], [0.88558, 0.00245], [0.90724, 0.00528], [0.82747, 0.08653],
            [0.67822, 0.26443], [0.65009, 0.30366], [0.64697, 0.32607], [0.61239, 0.36567],
            [0.60388, 0.40766], [0.58266, 0.43522], [0.54096, 0.5078], [0.50715, 0.54497],
            [0.45058, 0.61649],
        ],
        "ambiguous": False,
    },
    "lsf_57.jpg": {
        "polygon": [
            [0.33096, 0.69998], [0.34285, 0.63505], [0.37414, 0.621], [0.40429, 0.59328],
            [0.41441, 0.5782], [0.48497, 0.5287], [0.6142, 0.45155], [0.68589, 0.40504],
            [0.75402, 0.34643], [0.792, 0.31088], [0.83332, 0.27634], [0.93104, 0.18494],
            [0.99012, 0.10613], [0.91661, 0.21848], [0.87025, 0.27627], [0.81265, 0.31717],
            [0.79222, 0.34839], [0.71409, 0.4042], [0.66647, 0.44222], [0.62826, 0.49384],
            [0.58425, 0.5251], [0.48867, 0.60195],
        ],
        "ambiguous": False,
    },
    "rbf_0.jpg": {
        "polygon": [
            [0.44391, 0.22869], [0.42278, 0.25213], [0.41092, 0.29037], [0.40801, 0.42932],
            [0.42974, 0.49364], [0.46405, 0.64453], [0.49475, 0.73709], [0.57841, 0.92595],
            [0.60098, 0.99507], [0.70343, 0.99445], [0.68013, 0.91746], [0.64872, 0.83376],
            [0.62185, 0.7439], [0.57645, 0.61011], [0.55745, 0.53808], [0.53456, 0.48121],
            [0.51956, 0.42538], [0.49177, 0.30723], [0.46901, 0.25923],
        ],
        "ambiguous": False,
    },
    "rbf_37.jpg": {
        "polygon": [
            [0.76216, 4e-05], [0.65074, 0.00212], [0.61757, 0.0407], [0.60021, 0.07852],
            [0.55563, 0.19215], [0.4615, 0.46753], [0.42366, 0.61586], [0.33242, 0.92575],
            [0.3177, 0.9965], [0.42732, 0.85732], [0.52271, 0.66123], [0.5576, 0.56085],
            [0.59995, 0.47258], [0.71231, 0.1795], [0.7536, 0.0183],
        ],
        "ambiguous": False,
    },
    "rbf_39.jpg": {
        "polygon": [
            [0.51871, 0.9494], [0.52686, 0.75426], [0.52536, 0.57635], [0.51499, 0.44502],
            [0.50012, 0.33786], [0.50726, 0.26618], [0.52464, 0.21045], [0.52612, 0.19384],
            [0.5616, 0.2649], [0.57404, 0.33417], [0.58306, 0.43094], [0.59484, 0.49932],
            [0.60594, 0.61301], [0.61617, 0.69482], [0.61395, 0.76213], [0.60162, 0.84514],
            [0.60162, 0.88231], [0.55543, 0.93601],
        ],
        "ambiguous": False,
    },
    "rbf_50.jpg": {
        "polygon": [
            [0.21711, 0.99528], [0.21555, 0.83194], [0.26285, 0.64052], [0.31726, 0.48969],
            [0.37806, 0.35468], [0.43423, 0.24665], [0.44824, 0.24592], [0.44812, 0.23275],
            [0.49943, 0.15615], [0.60026, 0.02312], [0.62191, 0.00338], [0.66809, 0.00165],
            [0.64971, 0.0499], [0.51348, 0.37156], [0.5126, 0.38346], [0.48507, 0.37913],
            [0.45664, 0.38078], [0.44224, 0.4017], [0.43749, 0.4412], [0.43837, 0.45844],
            [0.43138, 0.49534], [0.44321, 0.51611], [0.47101, 0.53102], [0.44092, 0.6174],
            [0.40709, 0.76725], [0.39329, 0.85581], [0.37147, 0.94139], [0.37226, 0.99641],
        ],
        "ambiguous": False,
    },
    "rbf_62.jpg": {
        "polygon": [
            [0.59573, 0.00067], [0.5192, 0.00054], [0.48793, 0.06488], [0.44633, 0.20575],
            [0.39776, 0.32046], [0.39342, 0.36357], [0.37773, 0.40937], [0.36328, 0.48311],
            [0.35568, 0.55701], [0.34197, 0.61088], [0.33853, 0.6565], [0.34822, 0.76078],
            [0.35665, 0.81368], [0.37755, 0.83819], [0.37565, 0.76365], [0.4309, 0.62384],
            [0.46444, 0.56968], [0.48268, 0.50888], [0.50146, 0.42782], [0.53098, 0.36029],
            [0.54763, 0.28911], [0.55536, 0.23264], [0.55774, 0.17455], [0.56726, 0.10979],
            [0.57978, 0.04502],
        ],
        "ambiguous": False,
    },
    "rbf_70.jpg": {
        "polygon": [
            [0.49127, 0.01704], [0.51805, 0.10366], [0.51971, 0.14861], [0.50675, 0.19959],
            [0.50036, 0.23857], [0.48871, 0.36001], [0.48974, 0.40954], [0.50669, 0.45181],
            [0.53494, 0.5628], [0.54981, 0.63365], [0.58184, 0.61609], [0.55963, 0.51231],
            [0.57829, 0.44565], [0.58721, 0.35822], [0.57046, 0.26824], [0.56024, 0.22525],
            [0.54292, 0.10378],
        ],
        "ambiguous": True,
    },
    "rtf_12.jpg": {
        "polygon": [
            [0.44403, 0.70677], [0.50548, 0.61834], [0.52352, 0.57332], [0.52744, 0.50994],
            [0.52469, 0.43463], [0.51545, 0.35715], [0.48274, 0.28508], [0.36074, 0.06479],
            [0.31089, 0.00118], [0.34719, 0.00276], [0.38471, 0.06419], [0.42634, 0.1406],
            [0.46139, 0.20948], [0.51741, 0.33663], [0.55298, 0.43351], [0.55472, 0.47534],
            [0.55089, 0.52234], [0.54631, 0.55153], [0.51495, 0.62281], [0.4703, 0.6939],
        ],
        "ambiguous": True,
    },
    "rtf_24.jpg": {
        "polygon": [
            [0.42549, 0.55664], [0.5053, 0.47174], [0.64299, 0.30077], [0.67296, 0.2361],
            [0.67783, 0.19016], [0.61662, 0.08053], [0.65054, 0.11009], [0.67614, 0.15352],
            [0.7019, 0.1929], [0.69001, 0.24553], [0.66515, 0.30367], [0.63208, 0.34739],
            [0.57628, 0.41403], [0.49736, 0.49561], [0.45799, 0.54902], [0.50691, 0.55891],
        ],
        "ambiguous": False,
    },
    "rtf_31.jpg": {
        "polygon": [
            [0.4452, 0.52742], [0.40999, 0.51512], [0.59406, 0.37658], [0.71023, 0.28298],
            [0.93077, 0.03235], [0.96499, 0.00321], [0.9815, 0.00321], [0.87989, 0.11193],
            [0.76408, 0.25382], [0.69796, 0.3149], [0.61823, 0.3849], [0.52376, 0.45636],
        ],
        "ambiguous": False,
    },
    "rtf_36.jpg": {
        "polygon": [
            [0.58153, 0.99455], [0.31283, 0.99259], [0.54863, 0.69056], [0.50924, 0.33116],
            [0.49183, 0.25881], [0.10875, 0.18624], [0.0048, 0.17812], [0.0048, 0.1622],
            [0.11855, 0.16958], [0.53419, 0.24715], [0.61931, 0.66673],
        ],
        "ambiguous": False,
    },
    "rtf_4.jpg": {
        "polygon": [
            [0.54875, 0.99757], [0.52064, 0.99785], [0.49349, 0.90952], [0.49665, 0.86295],
            [0.49177, 0.73522], [0.50756, 0.64004], [0.50934, 0.57764], [0.4915, 0.47502],
            [0.4683, 0.38497], [0.44254, 0.26227], [0.42405, 0.10392], [0.39174, 0.0008],
            [0.42381, 0.00077], [0.43985, 0.08665], [0.46399, 0.23456], [0.46907, 0.30876],
            [0.4947, 0.3935], [0.51508, 0.49044], [0.52196, 0.58437], [0.5159, 0.77161],
            [0.51519, 0.89462],
        ],
        "ambiguous": True,
    },
    "rtf_64.jpg": {
        "polygon": [
            [0.60241, 0.81395], [0.56736, 0.66509], [0.48719, 0.51865], [0.44799, 0.35981],
            [0.41369, 0.26128], [0.32927, 0.09671], [0.27299, 0.00498], [0.29419, 0.00226],
            [0.36586, 0.10994], [0.45393, 0.28499], [0.53176, 0.45335], [0.58654, 0.58881],
            [0.60575, 0.69398],
        ],
        "ambiguous": False,
    },
    "sbf_14.jpg": {
        "polygon": [
            [0.33766, 0.80527], [0.39814, 0.70338], [0.47073, 0.55692], [0.56336, 0.42943],
            [0.63226, 0.317], [0.72402, 0.09915], [0.78746, 0.00536], [0.57603, 0.00251],
            [0.52985, 0.1457], [0.48542, 0.30353], [0.42168, 0.47014], [0.32624, 0.70691],
            [0.2848, 0.79784],
        ],
        "ambiguous": False,
    },
    "sbf_16.jpg": {
        "polygon": [
            [0.27726, 0.97669], [0.2354, 0.92835], [0.31338, 0.71278], [0.3981, 0.59037],
            [0.47074, 0.41021], [0.48541, 0.2661], [0.57221, 0.00105], [0.64938, 0.00301],
            [0.60818, 0.19004], [0.58112, 0.28475], [0.54054, 0.37099], [0.48442, 0.49968],
            [0.44691, 0.60682], [0.43085, 0.66458], [0.41871, 0.75259], [0.33091, 0.91798],
        ],
        "ambiguous": False,
    },
    "sbf_23.jpg": {
        "polygon": [
            [0.12873, 0.74646], [0.15277, 0.66723], [0.22684, 0.54949], [0.33198, 0.42953],
            [0.363, 0.34853], [0.41899, 0.24516], [0.49328, 0.07467], [0.53537, 0.00456],
            [0.74038, 0.00916], [0.68374, 0.11406], [0.63627, 0.22659], [0.55657, 0.3231],
            [0.47688, 0.40472], [0.43422, 0.46493], [0.39185, 0.52001], [0.31611, 0.59782],
            [0.27847, 0.6291], [0.17091, 0.73123],
        ],
        "ambiguous": False,
    },
    "sbf_29.jpg": {
        "polygon": [
            [0.56859, 0.99529], [0.4463, 0.99729], [0.42752, 0.8849], [0.42405, 0.76016],
            [0.40652, 0.64871], [0.41874, 0.52823], [0.40739, 0.39245], [0.386, 0.22709],
            [0.3631, 0.11299], [0.34349, 0.00138], [0.50856, 0.00409], [0.53074, 0.14047],
            [0.54295, 0.25224], [0.54374, 0.38091], [0.53732, 0.48095], [0.53642, 0.59276],
            [0.55196, 0.69471], [0.55299, 0.77364], [0.55107, 0.83813], [0.53565, 0.91648],
        ],
        "ambiguous": False,
    },
    "sbf_31.jpg": {
        "polygon": [
            [0.54973, 0.99678], [0.47891, 0.99258], [0.45791, 0.94763], [0.45263, 0.90877],
            [0.45504, 0.87654], [0.44236, 0.81785], [0.42374, 0.64877], [0.38888, 0.44564],
            [0.38814, 0.32294], [0.37193, 0.17538], [0.363, 0.00348], [0.63024, 0.0002],
            [0.6295, 0.15121], [0.62268, 0.27258], [0.60662, 0.46853], [0.61766, 0.56932],
            [0.61281, 0.65418], [0.57161, 0.72724], [0.57335, 0.75613], [0.5927, 0.87894],
            [0.59165, 0.92863], [0.57153, 0.96657],
        ],
        "ambiguous": False,
    },
    "sbf_43.jpg": {
        "polygon": [
            [0.39558, 0.00471], [0.48241, 0.00766], [0.50009, 0.12565], [0.5263, 0.2687],
            [0.52936, 0.32003], [0.54881, 0.39247], [0.59515, 0.45505], [0.61707, 0.47838],
            [0.63715, 0.57106], [0.63965, 0.62302], [0.58275, 0.59672], [0.58129, 0.573],
            [0.55409, 0.5406], [0.52411, 0.49426], [0.5179, 0.44749], [0.50469, 0.37491],
            [0.4906, 0.31734], [0.47872, 0.23196], [0.45506, 0.19217], [0.4481, 0.13663],
        ],
        "ambiguous": True,
    },
}


# ---- from 10_data.ipynb ----
import csv
import hashlib
import json
import multiprocessing
import os
import struct
import sys
import tempfile
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict, dataclass, replace
from pathlib import Path

import cv2
import numpy as np

IMAGE_SUFFIXES = frozenset({".jpg", ".jpeg"})
WORK_DIRNAME = "_work"  # everything the code generates lives in <data_root>/_work/

# Fixed class order, used in every confusion matrix, table and figure.
CLASS_NAMES = ("Brown Spot", "Leaf Scald", "Rice Blast", "Rice Tungro", "Sheath Blight")
DOMAINS = ("white", "field")

# (filename prefix, class, domain, exact string in the CSV `Diseases` column)
LABEL_TABLE = (
    ("bs_wb_", "Brown Spot", "white", "Brown Spot(white Background)"),
    ("ls_wb_", "Leaf Scald", "white", "Leaf Scaled(white Background)"),
    ("rb_wb_", "Rice Blast", "white", "Rice Blast(white Background)"),
    ("rt_wb_", "Rice Tungro", "white", "Rice Tungro(white Background)"),
    ("sb_wb_", "Sheath Blight", "white", "Shath Blight(white Background)"),
    ("bsf_", "Brown Spot", "field", "Browon Spot(Feild Background)"),
    ("lsf_", "Leaf Scald", "field", "Leaf Scaled(Feild Background)"),
    ("rbf_", "Rice Blast", "field", "Rice Blast(Feild Background)"),
    ("rtf_", "Rice Tungro", "field", "Rice Turgro(Feild Background)"),
    ("sbf_", "Sheath Blight", "field", "Sheath Blight(Feild Background)"),
)
# Longest prefix first, so that a prefix that extends another one always wins.
PREFIXES_LONGEST_FIRST = tuple(sorted(LABEL_TABLE, key=lambda row: -len(row[0])))
CSV_LABELS = {csv_label: (cls, domain) for _, cls, domain, csv_label in LABEL_TABLE}

# Image counts per (class, domain) established by the audit. A different dataset must fail loudly.
EXPECTED_COUNTS = {
    ("Brown Spot", "white"): 90,
    ("Leaf Scald", "white"): 143,
    ("Rice Blast", "white"): 198,
    ("Rice Tungro", "white"): 119,
    ("Sheath Blight", "white"): 219,
    ("Brown Spot", "field"): 49,
    ("Leaf Scald", "field"): 74,
    ("Rice Blast", "field"): 74,
    ("Rice Tungro", "field"): 76,
    ("Sheath Blight", "field"): 64,
}
EXPECTED_TOTAL = sum(EXPECTED_COUNTS.values())  # 1106

CSV_FILENAME = "Dhan-Shomadhan_picture_Information.csv"


class DatasetError(Exception):
    """The dataset on disk is not what the code expects. The message names the offending path."""


def warn(message: str) -> None:
    print(f"warning: {message}", file=sys.stderr)


def extended_path(absolute_path: str, windows: bool) -> str:
    """Windows silently strips trailing spaces from path components (the dataset has folders called
    'Field Background  '). The extended-length prefix switches that off. No-op elsewhere."""
    if not windows or absolute_path.startswith("\\\\?\\"):
        return absolute_path
    if absolute_path.startswith("\\\\"):  # UNC share: \\server\share -> \\?\UNC\server\share
        return "\\\\?\\UNC\\" + absolute_path[2:]
    return "\\\\?\\" + absolute_path


def fs_path(path) -> str:
    """The string to hand to open()/os functions for ``path`` (absolute, Windows-safe)."""
    return extended_path(os.path.abspath(os.fspath(path)), os.name == "nt")


def read_file_bytes(path) -> bytes:
    with open(fs_path(path), "rb") as handle:
        return handle.read()


def write_bytes_atomic(path: Path, data: bytes) -> None:
    """Write via a temp file and rename, so an interrupted run never leaves a truncated file."""
    path = Path(path)
    os.makedirs(fs_path(path.parent), exist_ok=True)
    tmp = path.with_name(path.name + f".tmp{os.getpid()}")
    with open(fs_path(tmp), "wb") as handle:
        handle.write(data)
    os.replace(fs_path(tmp), fs_path(path))


def write_text_atomic(path: Path, text: str) -> None:
    write_bytes_atomic(path, text.encode("utf-8"))  # bytes: identical files on every OS (no CRLF)


def find_images(data_root: Path) -> list[Path]:
    """All JPEGs under data_root (recursive, case-insensitive), skipping the generated _work/ folder."""
    found = []
    for dirpath, dirnames, filenames in Path(data_root).walk():
        if dirpath == Path(data_root) and WORK_DIRNAME in dirnames:
            dirnames.remove(WORK_DIRNAME)
        for filename in filenames:
            if Path(filename).suffix.lower() in IMAGE_SUFFIXES:
                found.append(dirpath / filename)
    return sorted(found)


def classify_filename(filename: str) -> tuple[str, str]:
    """(class, domain) from the filename prefix; longest prefix wins. Raises DatasetError."""
    lowered = filename.lower()
    for prefix, cls, domain, _ in PREFIXES_LONGEST_FIRST:
        if lowered.startswith(prefix):
            return cls, domain
    known = ", ".join(row[0] for row in LABEL_TABLE)
    raise DatasetError(f"{filename}: filename matches no known prefix ({known})")

def _tiff_orientation(tiff: bytes) -> int:
    """Orientation (1..8) from the TIFF block of an EXIF segment; 1 if absent."""
    if len(tiff) < 8 or tiff[:2] not in (b"II", b"MM"):
        return 1
    endian = "<" if tiff[:2] == b"II" else ">"
    if struct.unpack_from(endian + "H", tiff, 2)[0] != 42:
        return 1
    offset = struct.unpack_from(endian + "I", tiff, 4)[0]
    if offset + 2 > len(tiff):
        return 1
    (count,) = struct.unpack_from(endian + "H", tiff, offset)
    for entry in range(count):
        base = offset + 2 + 12 * entry
        if base + 12 > len(tiff):
            break
        tag, kind, n_values = struct.unpack_from(endian + "HHI", tiff, base)
        if tag == 0x0112 and kind == 3 and n_values == 1:  # SHORT, one value, stored inline
            value = struct.unpack_from(endian + "H", tiff, base + 8)[0]
            return value if 1 <= value <= 8 else 1
    return 1


def parse_exif_orientation(data: bytes) -> int:
    """EXIF orientation (1..8) of a JPEG given its bytes. 1 means upright (also when there is no tag)."""
    if data[:2] != b"\xff\xd8":
        return 1
    pos, end = 2, len(data)
    while pos + 4 <= end:
        if data[pos] != 0xFF:
            break
        marker = data[pos + 1]
        if marker == 0xFF:  # fill byte
            pos += 1
            continue
        if marker == 0x01 or 0xD0 <= marker <= 0xD8:  # markers without a length
            pos += 2
            continue
        if marker in (0xD9, 0xDA):  # end of image / start of scan: no EXIF after this
            break
        (length,) = struct.unpack_from(">H", data, pos + 2)
        if marker == 0xE1 and data[pos + 4 : pos + 10] == b"Exif\x00\x00":
            return _tiff_orientation(data[pos + 10 : pos + 2 + length])
        pos += 2 + length
    return 1

@dataclass(frozen=True)
class Record:
    filename: str  # primary key (unique across the dataset)
    rel_path: str  # path relative to the data root, '/' separated
    cls: str
    cls_idx: int
    domain: str  # "white" or "field"
    exif_orientation: int  # 1..8; 1 = upright or no tag
    sha1: str  # of the file bytes; "" when hashing was skipped (smoke only)

    @property
    def stratum(self) -> tuple[str, str]:
        return (self.cls, self.domain)


def work_dir(data_root) -> Path:
    return Path(data_root) / WORK_DIRNAME


def index_path(data_root) -> Path:
    return work_dir(data_root) / "index.json"


def read_csv_labels(csv_path: Path) -> dict[str, str]:
    """{picture name: Diseases string}. The CSV has an unnamed index column, then `pictureName` and
    `Diseases`; it may start with a UTF-8 BOM."""
    with open(fs_path(csv_path), newline="", encoding="utf-8-sig") as handle:
        reader = csv.reader(handle)
        header = [cell.strip().lower() for cell in next(reader, [])]
        try:
            name_col, label_col = header.index("picturename"), header.index("diseases")
        except ValueError:
            raise DatasetError(f"{csv_path}: expected columns 'pictureName' and 'Diseases', found {header}") from None
        labels = {}
        for row in reader:
            if len(row) <= max(name_col, label_col):
                continue
            labels[row[name_col].strip()] = row[label_col].strip()
    return labels


def find_csv(data_root: Path) -> Path | None:
    path = Path(data_root) / CSV_FILENAME
    if path.is_file():
        return path
    others = sorted(Path(data_root).glob("*.csv"))
    return others[0] if len(others) == 1 else None


def check_against_csv(records: list[Record], csv_path: Path, *, require_complete: bool) -> None:
    csv_labels = read_csv_labels(csv_path)
    for record in records:
        if record.filename not in csv_labels:
            raise DatasetError(f"{record.rel_path}: not listed in {csv_path.name}")
        csv_string = csv_labels[record.filename]
        if csv_string not in CSV_LABELS:
            raise DatasetError(f"{csv_path.name}: unknown Diseases string {csv_string!r} for {record.filename}")
        if CSV_LABELS[csv_string] != (record.cls, record.domain):
            raise DatasetError(
                f"{record.rel_path}: filename prefix says {(record.cls, record.domain)} "
                f"but {csv_path.name} says {CSV_LABELS[csv_string]} ({csv_string!r})"
            )
    if require_complete:
        missing = sorted(set(csv_labels) - {r.filename for r in records})
        if missing:
            raise DatasetError(f"{csv_path.name} lists {len(missing)} images that are not on disk, e.g. {missing[:3]}")


def check_expected_counts(records: list[Record], expected: dict[tuple[str, str], int]) -> None:
    actual = Counter(r.stratum for r in records)
    problems = [
        f"{key[0]} / {key[1]}: expected {expected.get(key, 0)}, found {actual.get(key, 0)}"
        for key in sorted(set(expected) | set(actual))
        if expected.get(key, 0) != actual.get(key, 0)
    ]
    if len(records) != sum(expected.values()):
        problems.insert(0, f"total: expected {sum(expected.values())}, found {len(records)}")
    if problems:
        raise DatasetError("this is not the expected dataset (counts differ):\n  " + "\n  ".join(problems))


EXIF_HEADER_BYTES = 128 * 1024  # the EXIF segment is at the very start of the file


def build_index(
    data_root,
    *,
    expected_counts: dict[tuple[str, str], int] | None = EXPECTED_COUNTS,
    with_sha1: bool = True,
) -> list[Record]:
    """Index every JPEG under ``data_root`` (see the section text above), sorted by filename.

    ``expected_counts=None`` skips the count assertion and the CSV completeness check. That is only
    for tiny synthetic trees in tests and for the smoke check on a partial tree; every real run
    (`prepare`) uses the default, so a different dataset fails loudly.
    ``with_sha1=False`` reads only the file headers (fast); records then have ``sha1 == ""``.
    """
    data_root = Path(data_root)
    if not data_root.is_dir():
        raise DatasetError(f"data root {data_root} is not a directory (see --data-root)")
    records, seen = [], {}
    for path in find_images(data_root):
        cls, domain = classify_filename(path.name)
        if path.name in seen:
            raise DatasetError(f"duplicate filename {path.name}: {seen[path.name]} and {path}")
        seen[path.name] = path
        with open(fs_path(path), "rb") as handle:
            data = handle.read() if with_sha1 else handle.read(EXIF_HEADER_BYTES)
        records.append(
            Record(
                filename=path.name,
                rel_path=path.relative_to(data_root).as_posix(),
                cls=cls,
                cls_idx=CLASS_NAMES.index(cls),
                domain=domain,
                exif_orientation=parse_exif_orientation(data),
                sha1=hashlib.sha1(data).hexdigest() if with_sha1 else "",
            )
        )
    records.sort(key=lambda r: r.filename)
    csv_path = find_csv(data_root)
    if csv_path is None:
        warn(f"no label CSV found in {data_root}; labels come from filename prefixes only")
    else:
        check_against_csv(records, csv_path, require_complete=expected_counts is not None)
    if expected_counts is not None:
        check_expected_counts(records, expected_counts)
    return records


def write_json(path: Path, obj, *, indent: int | None = 1) -> None:
    write_text_atomic(path, json.dumps(obj, indent=indent, sort_keys=False) + "\n")


def write_index(data_root, records: list[Record]) -> Path:
    path = index_path(data_root)
    rows = ",\n".join("  " + json.dumps(asdict(r)) for r in records)  # one record per line: readable diffs
    write_text_atomic(path, '{\n "format": 1,\n "records": [\n' + rows + "\n ]\n}\n")
    return path


def load_index(data_root) -> list[Record]:
    """The records written by `prepare`, sorted by filename."""
    path = index_path(data_root)
    if not path.is_file():
        raise DatasetError(f"{path} does not exist; run the `prepare` command first")
    payload = json.loads(read_file_bytes(path).decode("utf-8"))
    if payload.get("format") != 1:
        raise DatasetError(f"{path}: unsupported index format {payload.get('format')!r}")
    return [Record(**row) for row in payload["records"]]

def apply_orientation(rgb: np.ndarray, orientation: int) -> np.ndarray:
    """Undo an EXIF orientation tag (same conventions as PIL.ImageOps.exif_transpose)."""
    if orientation == 2:
        return rgb[:, ::-1]
    if orientation == 3:
        return np.rot90(rgb, 2)
    if orientation == 4:
        return rgb[::-1]
    if orientation == 5:  # transpose
        return rgb.transpose(1, 0, 2)
    if orientation == 6:  # stored rotated 90 degrees counter-clockwise: rotate clockwise
        return np.rot90(rgb, -1)
    if orientation == 7:  # transverse
        return np.rot90(rgb.transpose(1, 0, 2), 2)
    if orientation == 8:
        return np.rot90(rgb, 1)
    return rgb


def to_portrait(rgb: np.ndarray) -> tuple[np.ndarray, bool]:
    """Rotate a landscape image 90 degrees clockwise. Returns (image, was_rotated)."""
    if rgb.shape[1] > rgb.shape[0]:
        return np.rot90(rgb, -1), True
    return rgb, False


def decode_oriented(data: bytes, source: str = "<bytes>") -> np.ndarray:
    """JPEG bytes -> (H, W, 3) uint8 RGB with the EXIF orientation applied (not yet portrait)."""
    bgr = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR | cv2.IMREAD_IGNORE_ORIENTATION)
    if bgr is None:
        raise DatasetError(f"{source}: cannot decode image")
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    return apply_orientation(rgb, parse_exif_orientation(data))


def read_rgb(path) -> np.ndarray:
    """(H, W, 3) uint8 RGB, EXIF applied, always portrait (H >= W). Works for paths that OpenCV's own
    file reader struggles with (non-ASCII, Windows trailing-space folders) because we read the bytes."""
    rgb, _ = to_portrait(decode_oriented(read_file_bytes(path), str(path)))
    return np.ascontiguousarray(rgb)

DHASH_SIZE = (9, 8)  # width, height of the resized gray image -> 8 x 8 = 64 bits


def dhash_bits(rgb: np.ndarray) -> np.ndarray:
    """64 bits (uint8 0/1) of the difference hash of an RGB image."""
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    small = cv2.resize(gray, DHASH_SIZE, interpolation=cv2.INTER_AREA).astype(np.int16)
    return (small[:, 1:] > small[:, :-1]).ravel().astype(np.uint8)


def dhash_hex(bits: np.ndarray) -> str:
    return np.packbits(bits).tobytes().hex()


def hex_to_bits(text: str) -> np.ndarray:
    return np.unpackbits(np.frombuffer(bytes.fromhex(text), dtype=np.uint8))

CACHE_LONG_SIDE = 1280
CACHE_JPEG_QUALITY = 95
MAX_WORKERS = 8


def cache_dir(data_root) -> Path:
    return work_dir(data_root) / "cache"


def manifest_path(data_root) -> Path:
    return cache_dir(data_root) / "manifest.json"


def default_workers() -> int:
    try:
        available = len(os.sched_getaffinity(0))
    except AttributeError:  # macOS, Windows
        available = os.cpu_count() or 1
    return max(1, min(available, MAX_WORKERS))


WORKER_START_METHOD = "spawn"  # never "fork": see the section text (forked OpenCV thread-pool locks deadlock)


def worker_context():
    """The multiprocessing context of every worker process (process pools and DataLoader workers)."""
    return multiprocessing.get_context(WORKER_START_METHOD)


def pool_is_safe() -> bool:
    """True if spawned worker processes can import the functions we send them: only when this file runs as the
    main script (children re-run it as `__mp_main__`)."""
    return __name__ == "__main__"


def _pool_init() -> None:
    cv2.setNumThreads(1)  # one process per core already; avoid oversubscription


def run_parallel(func, tasks, *, workers: int, mp_context=None, chunksize: int = 4):
    """Yield ``func(task)`` for every task, in order. Uses a process pool when that is possible and
    worthwhile, otherwise runs inline. ``func`` must be a picklable top-level function."""
    tasks = list(tasks)
    use_pool = workers > 1 and len(tasks) > 1 and (mp_context is not None or pool_is_safe())
    mp_context = mp_context if mp_context is not None else worker_context()
    if not use_pool:
        for task in tasks:
            yield func(task)
        return
    with ProcessPoolExecutor(
        max_workers=min(workers, len(tasks)), mp_context=mp_context, initializer=_pool_init
    ) as executor:
        yield from executor.map(func, tasks, chunksize=chunksize)


def resize_long_side(rgb: np.ndarray, long_side: int) -> np.ndarray:
    height, width = rgb.shape[:2]
    scale = long_side / max(height, width)
    if scale >= 1.0:
        return rgb
    size = (max(1, round(width * scale)), max(1, round(height * scale)))
    return cv2.resize(rgb, size, interpolation=cv2.INTER_AREA)


def encode_jpeg(rgb: np.ndarray, quality: int) -> bytes:
    ok, buffer = cv2.imencode(".jpg", cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, quality])
    if not ok:
        raise DatasetError("JPEG encoding failed")
    return buffer.tobytes()


def _cache_one(task: tuple) -> tuple[str, dict]:
    """Worker: source file -> cached portrait JPEG. Returns (filename, manifest entry without sha1)."""
    filename, source, target, long_side, quality = task
    try:
        rgb, rotated = to_portrait(decode_oriented(read_file_bytes(source), source))
        small = resize_long_side(np.ascontiguousarray(rgb), long_side)
        write_bytes_atomic(Path(target), encode_jpeg(small, quality))
    except Exception as exc:
        raise DatasetError(f"{source}: caching failed: {exc}") from exc
    return filename, {
        "width": int(small.shape[1]),
        "height": int(small.shape[0]),
        "rotated_landscape": bool(rotated),
        "dhash": dhash_hex(dhash_bits(small)),  # of the downsized image, before JPEG encoding
    }


@dataclass
class CacheStats:
    total: int
    built: int
    reused: int
    rotated_landscape: int  # images (of `total`) that were landscape after EXIF and were turned to portrait


def load_manifest(data_root) -> dict:
    path = manifest_path(data_root)
    if not path.is_file():
        return {}
    try:
        return json.loads(read_file_bytes(path).decode("utf-8"))
    except (OSError, ValueError):
        return {}  # a damaged manifest only means "rebuild everything"


def write_manifest(data_root, manifest: dict) -> None:
    write_json(manifest_path(data_root), dict(sorted(manifest.items())))


def build_cache(
    data_root,
    records: list[Record],
    *,
    workers: int | None = None,
    mp_context=None,
    long_side: int = CACHE_LONG_SIDE,
    quality: int = CACHE_JPEG_QUALITY,
    output_root=None,
    log=None,
) -> CacheStats:
    """Cache every record (see section text). Idempotent. ``records`` need their sha1 (not the
    ``with_sha1=False`` kind). Images are read from ``data_root``; the cache is written under
    ``<output_root>/_work/cache`` (default: the same data root; the smoke check uses a temp folder)."""
    if any(not r.sha1 for r in records):
        raise DatasetError("build_cache needs records with sha1 (build_index(..., with_sha1=True))")
    data_root = Path(data_root)
    output_root = Path(output_root) if output_root is not None else data_root
    root = cache_dir(output_root)
    manifest = load_manifest(output_root)

    def current(record: Record) -> bool:
        entry = manifest.get(record.filename)
        return (
            bool(entry)
            and entry.get("sha1") == record.sha1
            and "dhash" in entry
            and (root / record.filename).is_file()
        )

    todo = [r for r in records if not current(r)]
    tasks = [(r.filename, str(data_root / r.rel_path), str(root / r.filename), long_side, quality) for r in todo]
    sha_of = {r.filename: r.sha1 for r in todo}
    done = 0
    try:
        for filename, entry in run_parallel(_cache_one, tasks, workers=workers or default_workers()):
            manifest[filename] = {"sha1": sha_of[filename], **entry}
            done += 1
            if log and done % 200 == 0:
                log(f"cache: {done}/{len(tasks)}")
    finally:
        if done:
            write_manifest(output_root, manifest)  # also after an interrupted run: finished images are kept
    rotated = sum(bool(manifest[r.filename]["rotated_landscape"]) for r in records)
    return CacheStats(total=len(records), built=len(todo), reused=len(records) - len(todo), rotated_landscape=rotated)


def read_cached_rgb(data_root, filename: str) -> np.ndarray:
    """A cached image: (H, W, 3) uint8 RGB, portrait, long side <= 1280."""
    return read_rgb(cache_dir(data_root) / filename)

NEAR_DUPLICATE_MAX_DISTANCE = 6
FEATURE_LONG_SIDE = 1000  # images are downscaled to this long side before SIFT
FEATURE_MAX_KEYPOINTS = 3000
FEATURE_CONTRAST = 0.01  # below OpenCV's 0.04 default: leaves on a plain wall have few strong corners
FEATURE_RATIO = 0.75  # Lowe ratio test
FEATURE_RANSAC_PX = 6.0
SHEET_MAX_PAIRS = 48  # pairs shown on contact sheets (the top of the ranking)
SHEET_PAIRS_PER_PAGE = 8


def hamming_matrix(bits: np.ndarray) -> np.ndarray:
    """All pairwise Hamming distances of an (N, 64) 0/1 matrix, as an (N, N) int matrix."""
    b = bits.astype(np.float32)
    return np.rint(b @ (1.0 - b).T + (1.0 - b) @ b.T).astype(np.int32)


def find_near_duplicates(bits: np.ndarray, max_distance: int = NEAR_DUPLICATE_MAX_DISTANCE) -> list[tuple[int, int, int]]:
    """(i, j, distance) with i < j and distance <= max_distance, sorted by distance then index."""
    dist = hamming_matrix(bits)
    rows, cols = np.nonzero(np.triu(dist <= max_distance, k=1))
    pairs = [(int(i), int(j), int(dist[i, j])) for i, j in zip(rows, cols)]
    return sorted(pairs, key=lambda p: (p[2], p[0], p[1]))


def sift_features(rgb: np.ndarray):
    """(keypoint coordinates (K, 2) float32, descriptors (K, 128) float32) at FEATURE_LONG_SIDE."""
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    scale = FEATURE_LONG_SIDE / max(gray.shape)
    if scale < 1.0:
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    keypoints, descriptors = cv2.SIFT_create(nfeatures=FEATURE_MAX_KEYPOINTS, contrastThreshold=FEATURE_CONTRAST).detectAndCompute(gray, None)
    points = np.float32([k.pt for k in keypoints]).reshape(-1, 2)
    return points, descriptors


def feature_inliers(features_a, features_b) -> int:
    """Number of ratio-test SIFT matches consistent with one similarity transform (RANSAC)."""
    (points_a, desc_a), (points_b, desc_b) = features_a, features_b
    if desc_a is None or desc_b is None or len(desc_a) < 8 or len(desc_b) < 8:
        return 0
    matches = cv2.BFMatcher(cv2.NORM_L2).knnMatch(desc_a, desc_b, k=2)
    good = [m[0] for m in matches if len(m) == 2 and m[0].distance < FEATURE_RATIO * m[1].distance]
    if len(good) < 8:
        return 0
    src = points_a[[m.queryIdx for m in good]]
    dst = points_b[[m.trainIdx for m in good]]
    _, mask = cv2.estimateAffinePartial2D(src, dst, method=cv2.RANSAC, ransacReprojThreshold=FEATURE_RANSAC_PX)
    return int(mask.sum()) if mask is not None else 0


@dataclass(frozen=True)
class DuplicatePair:
    pair_id: int  # review rank, 1 = most likely a duplicate
    hamming: int
    feature_inliers: int
    a: Record
    b: Record

    @property
    def scope(self) -> str:
        return "within domain" if self.a.domain == self.b.domain else "across domains"


def load_dhashes(data_root, records: list[Record]) -> np.ndarray:
    """(N, 64) uint8 matrix of the dHashes stored in the cache manifest (run build_cache first)."""
    manifest = load_manifest(data_root)
    missing = [r.filename for r in records if "dhash" not in manifest.get(r.filename, {})]
    if missing:
        raise DatasetError(f"no dHash for {len(missing)} images (e.g. {missing[:3]}); run `prepare` to build the cache")
    return np.stack([hex_to_bits(manifest[r.filename]["dhash"]) for r in records]) if records else np.zeros((0, 64), np.uint8)


def duplicate_pairs(
    data_root, records: list[Record], bits: np.ndarray, max_distance: int = NEAR_DUPLICATE_MAX_DISTANCE
) -> list[DuplicatePair]:
    """All candidate pairs, ranked: most feature inliers first, then smallest Hamming distance, then names."""
    candidates = find_near_duplicates(bits, max_distance)
    needed = sorted({i for i, j, _ in candidates} | {j for i, j, _ in candidates})
    features = {i: sift_features(read_cached_rgb(data_root, records[i].filename)) for i in needed}
    scored = [
        (-feature_inliers(features[i], features[j]), d, records[i].filename, records[j].filename, records[i], records[j])
        for i, j, d in candidates
    ]
    scored.sort(key=lambda t: t[:4])
    return [DuplicatePair(rank, d, -neg, a, b) for rank, (neg, d, _, _, a, b) in enumerate(scored, start=1)]


def duplicate_stats(pairs: list[DuplicatePair]) -> dict:
    """Counts of candidate pairs per Hamming distance and per scope (within / across domains)."""
    by_distance = Counter(p.hamming for p in pairs)
    by_scope = Counter(p.scope for p in pairs)
    inliers = [p.feature_inliers for p in pairs]
    return {
        "total": len(pairs),
        "by_distance": {d: by_distance[d] for d in sorted(by_distance)},
        "within_domain": by_scope["within domain"],
        "across_domains": by_scope["across domains"],
        "same_class": sum(p.a.cls == p.b.cls for p in pairs),
        "images_involved": len({p.a.filename for p in pairs} | {p.b.filename for p in pairs}),
        "max_feature_inliers": max(inliers, default=0),
    }


def results_dir(data_root) -> Path:
    return work_dir(data_root) / "results"


def figures_dir(data_root) -> Path:
    return work_dir(data_root) / "figures"


def write_duplicate_report(data_root, pairs: list[DuplicatePair]) -> Path:
    """`_work/results/near_duplicates.csv`: every candidate pair, in review order."""
    path = results_dir(data_root) / "near_duplicates.csv"
    lines = ["pair_id,hamming,feature_inliers,scope,file_a,file_b,class_a,class_b,domain_a,domain_b"]
    for p in pairs:
        lines.append(
            f"{p.pair_id},{p.hamming},{p.feature_inliers},{p.scope},{p.a.filename},{p.b.filename},"
            f"{p.a.cls},{p.b.cls},{p.a.domain},{p.b.domain}"
        )
    write_text_atomic(path, "\n".join(lines) + "\n")
    return path


def validate_duplicate_groups(groups, records: list[Record]) -> list[list[str]]:
    """Check the duplicate groups (the embedded ``DUPLICATE_GROUPS``) against the index and return them
    normalised: members sorted, groups sorted. Raises DatasetError unless

    * every group is a list of at least two filenames,
    * every filename exists in the index,
    * no filename appears in two groups (nor twice in one), and
    * every group lies within one class x domain stratum, because the splits stratify on it.

    Nothing is merged or repaired: a wrong group list is a bug in ``annotations/duplicate_groups.json``."""
    stratum_of = {r.filename: r.stratum for r in records}
    first_group: dict[str, int] = {}
    for number, group in enumerate(groups):
        if not isinstance(group, (list, tuple)) or len(group) < 2 or not all(isinstance(n, str) for n in group):
            raise DatasetError(f"duplicate group #{number}: expected a list of at least 2 filenames, got {group!r}")
        for name in group:
            if name not in stratum_of:
                raise DatasetError(f"duplicate group #{number}: {name} is not in the dataset index")
            if name in first_group:
                raise DatasetError(f"{name} appears in duplicate groups #{first_group[name]} and #{number}")
            first_group[name] = number
        strata = sorted({stratum_of[n] for n in group})
        if len(strata) != 1:
            raise DatasetError(f"duplicate group #{number} {list(group)} spans several class x domain strata: {strata}")
    return sorted((sorted(g) for g in groups), key=lambda g: g[0])

# Okabe-Ito colour-blind-safe palette.
OKABE_ITO = {
    "black": "#000000",
    "orange": "#E69F00",
    "sky": "#56B4E9",
    "green": "#009E73",
    "yellow": "#F0E442",
    "blue": "#0072B2",
    "vermilion": "#D55E00",
    "purple": "#CC79A7",
}
# One colour per domain (2 series: they must stay distinguishable in grayscale print as well).
DOMAIN_COLORS = {"white": OKABE_ITO["blue"], "field": OKABE_ITO["orange"]}
FIGURE_DPI = 300


def pyplot():
    """matplotlib.pyplot on the Agg backend (no display needed, also on Colab and on servers)."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def thumbnail(rgb: np.ndarray, height: int) -> np.ndarray:
    scale = height / rgb.shape[0]
    return cv2.resize(rgb, (max(1, round(rgb.shape[1] * scale)), height), interpolation=cv2.INTER_AREA)


def save_duplicate_sheets(
    data_root,
    pairs: list[DuplicatePair],
    *,
    max_pairs: int = SHEET_MAX_PAIRS,
    per_page: int = SHEET_PAIRS_PER_PAGE,
) -> list[Path]:
    """Contact sheets `near_duplicates_<n>.png` of the top-ranked pairs, side by side, labelled with
    filename, class, domain, dHash distance and feature inliers. Old pages are removed first."""
    plt = pyplot()
    out_dir = figures_dir(data_root)
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("near_duplicates*.png"):
        old.unlink()
    shown = pairs[:max_pairs]
    cols, rows = 4, max(1, per_page // 4)
    pages = [shown[i : i + per_page] for i in range(0, len(shown), per_page)]
    paths = []
    for number, chunk in enumerate(pages, start=1):
        fig = plt.figure(figsize=(20, 11.4 if rows == 2 else 6), dpi=100)
        grid = fig.add_gridspec(rows, cols, left=0.005, right=0.995, top=0.935, bottom=0.005, wspace=0.05, hspace=0.1)
        for k, pair in enumerate(chunk):
            inner = grid[k // cols, k % cols].subgridspec(2, 2, height_ratios=[0.055, 1], wspace=0.03, hspace=0.01)
            head = fig.add_subplot(inner[0, :])
            head.axis("off")
            head.text(
                0.5, 0.5,
                f"#{pair.pair_id}   dHash {pair.hamming}   inliers {pair.feature_inliers}   ({pair.scope})",
                ha="center", va="center", fontsize=11, fontweight="bold",
            )
            for side, record in enumerate((pair.a, pair.b)):
                ax = fig.add_subplot(inner[1, side])
                ax.imshow(thumbnail(read_cached_rgb(data_root, record.filename), 560))
                ax.set_xticks([])
                ax.set_yticks([])
                for spine in ax.spines.values():
                    spine.set_edgecolor(DOMAIN_COLORS[record.domain])
                    spine.set_linewidth(2.5)
                ax.set_xlabel(f"{record.filename}\n{record.cls}, {record.domain}", fontsize=9)
        first, last = chunk[0].pair_id, chunk[-1].pair_id
        fig.suptitle(
            f"Near-duplicate candidates, page {number}/{len(pages)} (pairs #{first}-#{last} of {len(pairs)}; "
            "border colour: blue = white background, orange = field)",
            fontsize=13, y=0.985,
        )
        path = out_dir / f"near_duplicates_{number:02d}.png"
        fig.savefig(path, dpi=100)
        plt.close(fig)
        paths.append(path)
    return paths

SPLIT_SEEDS = (0, 1, 2, 3, 4)
SPLIT_PERCENT = 15  # test and val each; train gets the remaining 70


def split_size(n_units: int, percent: int = SPLIT_PERCENT) -> int:
    """round(percent / 100 * n) with halves rounded up, in integer arithmetic."""
    return (percent * n_units + 50) // 100


def split_sha256(seed: int, train: list[str], val: list[str], test: list[str]) -> str:
    payload = json.dumps(
        {"seed": seed, "train": sorted(train), "val": sorted(val), "test": sorted(test)},
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def stratum_order(stratum: tuple[str, str]) -> tuple[int, int]:
    return (CLASS_NAMES.index(stratum[0]), DOMAINS.index(stratum[1]))


def build_units(records: list[Record], groups: list[list[str]]) -> dict[tuple[str, str], list[tuple[str, ...]]]:
    """{stratum: units}; a unit is a sorted tuple of filenames: a duplicate group, or a single image.
    ``groups`` is validated first (see ``validate_duplicate_groups``); ``[]`` gives one unit per image."""
    by_name = {r.filename: r for r in records}
    units: dict[tuple[str, str], list[tuple[str, ...]]] = {}
    grouped: set[str] = set()
    for group in validate_duplicate_groups(groups, records):
        members = tuple(group)
        grouped.update(members)
        units.setdefault(by_name[members[0]].stratum, []).append(members)
    for record in records:
        if record.filename not in grouped:
            units.setdefault(record.stratum, []).append((record.filename,))
    return units


def make_split(records: list[Record], groups: list[list[str]], seed: int) -> dict:
    """One split as a dict with keys seed, train, val, test (sorted filename lists) and sha256."""
    train: list[str] = []
    val: list[str] = []
    test: list[str] = []
    units_by_stratum = build_units(records, groups)
    for stratum in sorted(units_by_stratum, key=stratum_order):
        units = sorted(units_by_stratum[stratum])
        shuffled = [units[i] for i in np.random.default_rng(seed).permutation(len(units))]
        n_test = split_size(len(units))
        n_val = split_size(len(units))
        for target, chosen in (
            (test, shuffled[:n_test]),
            (val, shuffled[n_test : n_test + n_val]),
            (train, shuffled[n_test + n_val :]),
        ):
            target.extend(name for unit in chosen for name in unit)
    train, val, test = sorted(train), sorted(val), sorted(test)
    return {"seed": seed, "train": train, "val": val, "test": test, "sha256": split_sha256(seed, train, val, test)}


def splits_dir(data_root) -> Path:
    return work_dir(data_root) / "splits"


def split_path(data_root, seed: int) -> Path:
    return splits_dir(data_root) / f"split_{seed}.json"


def write_splits(data_root, records: list[Record], groups: list[list[str]], seeds=SPLIT_SEEDS) -> dict[int, str]:
    """Generate and write split_<k>.json. Returns {seed: "new" | "unchanged" | "CHANGED"} so that the
    caller can say loudly when an existing (committed) split differs from the regenerated one."""
    status = {}
    for seed in seeds:
        split = make_split(records, groups, seed)
        path = split_path(data_root, seed)
        before = None
        if path.is_file():
            try:
                before = json.loads(read_file_bytes(path).decode("utf-8")).get("sha256")
            except ValueError:
                before = ""
        status[seed] = "new" if before is None else "unchanged" if before == split["sha256"] else "CHANGED"
        if status[seed] != "unchanged":
            write_json(path, split)
    return status


def load_split(data_root, seed: int) -> dict:
    """A split written by `prepare`, with its sha256 re-computed and verified."""
    path = split_path(data_root, seed)
    if not path.is_file():
        raise DatasetError(f"{path} does not exist; run the `prepare` command first")
    split = json.loads(read_file_bytes(path).decode("utf-8"))
    expected = split_sha256(split["seed"], split["train"], split["val"], split["test"])
    if split.get("sha256") != expected:
        raise DatasetError(f"{path}: sha256 does not match its content (file edited by hand?)")
    return split


def split_counts(split: dict, records: list[Record]) -> dict:
    """{'train': {'white': n, 'field': n, 'all': n}, 'val': ..., 'test': ...}"""
    domain_of = {r.filename: r.domain for r in records}
    return {
        part: {**{d: sum(domain_of[n] == d for n in split[part]) for d in DOMAINS}, "all": len(split[part])}
        for part in ("train", "val", "test")
    }

GRID_SEED = 42
DOMAIN_LABELS = {"white": "White background", "field": "Field background"}


def class_domain_counts(records: list[Record]) -> dict[tuple[str, str], int]:
    counts = Counter(r.stratum for r in records)
    return {(c, d): counts.get((c, d), 0) for c in CLASS_NAMES for d in DOMAINS}


def dataset_counts_markdown(records: list[Record]) -> str:
    counts = class_domain_counts(records)
    lines = ["| Class | White background | Field background | Total |", "|---|---:|---:|---:|"]
    for cls in CLASS_NAMES:
        white, field = counts[(cls, "white")], counts[(cls, "field")]
        lines.append(f"| {cls} | {white} | {field} | {white + field} |")
    white_total = sum(counts[(c, "white")] for c in CLASS_NAMES)
    field_total = sum(counts[(c, "field")] for c in CLASS_NAMES)
    lines.append(f"| **Total** | **{white_total}** | **{field_total}** | **{white_total + field_total}** |")
    return "\n".join(lines) + "\n"


def write_dataset_counts(data_root, records: list[Record]) -> Path:
    path = results_dir(data_root) / "dataset_counts.md"
    write_text_atomic(path, dataset_counts_markdown(records))
    return path


def save_dataset_grid(data_root, records: list[Record], path: Path | None = None, seed: int = GRID_SEED) -> Path:
    """2 rows (white, field) x 5 classes, one random (seeded) sample each, read from the cache."""
    plt = pyplot()
    path = path or figures_dir(data_root) / "dataset_grid.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    chosen = {}
    for domain in DOMAINS:
        for cls in CLASS_NAMES:
            names = sorted(r.filename for r in records if r.stratum == (cls, domain))
            chosen[(cls, domain)] = names[int(rng.integers(len(names)))] if names else None
    with plt.rc_context({"font.size": 8.5}):
        fig = plt.figure(figsize=(5.6, 4.72))
        grid = fig.add_gridspec(2, 5, left=0.065, right=0.995, top=0.94, bottom=0.004, wspace=0.05, hspace=0.02)
        for row, domain in enumerate(DOMAINS):
            for col, cls in enumerate(CLASS_NAMES):
                ax = fig.add_subplot(grid[row, col])
                ax.set_xticks([])
                ax.set_yticks([])
                for spine in ax.spines.values():
                    spine.set_visible(False)
                name = chosen[(cls, domain)]
                if name is not None:
                    ax.imshow(thumbnail(read_cached_rgb(data_root, name), 760))
                if row == 0:
                    ax.set_title(cls, fontsize=8.5, fontweight="bold", pad=3)
                if col == 0:
                    ax.set_ylabel(DOMAIN_LABELS[domain], fontsize=8.5, fontweight="bold", labelpad=4)
        fig.savefig(path, dpi=FIGURE_DPI)
        plt.close(fig)
    return path


def save_class_domain_counts(data_root, records: list[Record], path: Path | None = None) -> Path:
    """Grouped bar chart: images per class, one bar per domain, value labels on the bars."""
    plt = pyplot()
    path = path or figures_dir(data_root) / "class_domain_counts.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    counts = class_domain_counts(records)
    x = np.arange(len(CLASS_NAMES))
    width = 0.38
    with plt.rc_context({"font.size": 9}):
        fig, ax = plt.subplots(figsize=(5.4, 3.3))
        for k, domain in enumerate(DOMAINS):
            values = [counts[(c, domain)] for c in CLASS_NAMES]
            bars = ax.bar(
                x + (k - 0.5) * width, values, width * 0.94, color=DOMAIN_COLORS[domain], label=DOMAIN_LABELS[domain]
            )
            ax.bar_label(bars, fontsize=8, padding=2)
        ax.set_xticks(x, [c.replace(" ", "\n") for c in CLASS_NAMES])
        ax.set_ylabel("Number of images")
        ax.set_ylim(0, max(counts.values(), default=1) * 1.15)
        ax.yaxis.grid(True, color="#DDDDDD", linewidth=0.6)
        ax.set_axisbelow(True)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.legend(frameon=False, loc="upper left", fontsize=8.5)
        fig.tight_layout(pad=0.6)
        fig.savefig(path, dpi=FIGURE_DPI)
        plt.close(fig)
    return path

def exif_summary(records: list[Record]) -> str:
    tagged = Counter(r.exif_orientation for r in records if r.exif_orientation != 1)
    detail = ", ".join(f"orientation {o}: {n}" for o, n in sorted(tagged.items()))
    return f"{sum(tagged.values())} images carry an EXIF rotation tag ({detail or 'none'}); all applied"


def prepare_data(
    data_root, *, expected_counts=EXPECTED_COUNTS, groups=None, workers: int | None = None, out=print
) -> dict:
    """index -> cache -> near-duplicate audit -> splits -> tables and figures. Returns a summary dict
    (also printed through ``out``). Raises DatasetError on any dataset problem.

    ``groups`` are the duplicate groups kept together in the splits; ``None`` means the embedded
    ``DUPLICATE_GROUPS``, which is what every real run uses (tests pass their own for tiny datasets)."""
    import time

    start = time.time()
    data_root = Path(data_root)
    out(f"prepare: data root {data_root.resolve()}")
    records = build_index(data_root, expected_counts=expected_counts)
    write_index(data_root, records)
    counts = Counter(r.domain for r in records)
    out(f"  index       {len(records)} images: white {counts['white']}, field {counts['field']}; {len(CLASS_NAMES)} classes")
    out(f"  exif        {exif_summary(records)}")

    t = time.time()
    cache = build_cache(data_root, records, workers=workers, log=out)
    out(
        f"  portrait    {cache.rotated_landscape} images were landscape after EXIF and were turned 90 degrees clockwise"
    )
    out(
        f"  cache       {cache.total} images, long side {CACHE_LONG_SIDE} px, JPEG q{CACHE_JPEG_QUALITY}: "
        f"built {cache.built}, already up to date {cache.reused} ({time.time() - t:.0f} s)"
    )

    t = time.time()
    pairs = duplicate_pairs(data_root, records, load_dhashes(data_root, records))
    stats = duplicate_stats(pairs)
    write_duplicate_report(data_root, pairs)
    sheets = save_duplicate_sheets(data_root, pairs)
    by_distance = " ".join(f"{d}:{n}" for d, n in stats["by_distance"].items())
    out(
        f"  duplicates  {stats['total']} dHash candidate pairs (distance <= {NEAR_DUPLICATE_MAX_DISTANCE}): "
        f"{stats['within_domain']} within domain, {stats['across_domains']} across; by distance {by_distance}"
    )
    out(
        f"              best feature-match score {stats['max_feature_inliers']} (ranking only; see tools/dup_audit); "
        f"{len(sheets)} contact sheets in {figures_dir(data_root)} ({time.time() - t:.0f} s)"
    )
    source = "embedded" if groups is None else "given"
    groups = validate_duplicate_groups(DUPLICATE_GROUPS if groups is None else groups, records)
    out(f"  groups      duplicate groups: {len(groups)} ({sum(len(g) for g in groups)} images), {source}; each is kept in one split")

    status = write_splits(data_root, records, groups)
    first = load_split(data_root, SPLIT_SEEDS[0])
    sizes = split_counts(first, records)
    out(
        f"  splits      seeds {SPLIT_SEEDS[0]}-{SPLIT_SEEDS[-1]}: train/val/test = "
        f"{sizes['train']['all']}/{sizes['val']['all']}/{sizes['test']['all']} "
        f"(test: {sizes['test']['white']} white, {sizes['test']['field']} field); "
        + ", ".join(f"{seed}: {state}" for seed, state in status.items())
    )
    if "CHANGED" in status.values():
        out("  WARNING     an existing split file differs from the regenerated one and was overwritten")
        out("              (expected only if the duplicate groups or the dataset changed; otherwise investigate before training)")
    out("              sha256 " + " ".join(load_split(data_root, s)["sha256"][:10] for s in SPLIT_SEEDS))

    write_dataset_counts(data_root, records)
    save_dataset_grid(data_root, records)
    save_class_domain_counts(data_root, records)
    out(f"  report      dataset_counts.md, dataset_grid.png, class_domain_counts.png in {work_dir(data_root)}")
    elapsed = time.time() - start
    out(f"  data        done in {elapsed:.0f} s")
    return {
        "records": len(records),
        "cache": cache,
        "duplicates": stats,
        "duplicate_groups": groups,
        "splits": status,
        "seconds": elapsed,
    }


def synthetic_records(per_stratum: int = 20) -> list[Record]:
    """Fake index entries (no files) covering every class x domain stratum; for smoke checks and tests."""
    prefix = {(cls, domain): p for p, cls, domain, _ in LABEL_TABLE}
    return [
        Record(f"{prefix[(cls, domain)]}{i}.jpg", f"x/{prefix[(cls, domain)]}{i}.jpg", cls, CLASS_NAMES.index(cls), domain, 1, "")
        for cls in CLASS_NAMES
        for domain in DOMAINS
        for i in range(per_stratum)
    ]


def pick_smoke_records(records: list[Record], n: int = 20) -> list[Record]:
    """Up to ``n`` records: first one of each EXIF orientation 3/6/8 present, then round-robin over strata."""
    chosen: list[Record] = []
    for orientation in (3, 6, 8):
        match = next((r for r in records if r.exif_orientation == orientation), None)
        if match:
            chosen.append(match)
    queues = {}
    for r in records:
        queues.setdefault(r.stratum, []).append(r)
    order = sorted(queues, key=stratum_order)
    while len(chosen) < min(n, len(records)):
        progressed = False
        for stratum in order:
            while queues[stratum] and queues[stratum][0] in chosen:
                queues[stratum].pop(0)
            if queues[stratum] and len(chosen) < n:
                chosen.append(queues[stratum].pop(0))
                progressed = True
        if not progressed:
            break
    return chosen


def smoke_require(condition: bool, message: str) -> None:
    if not condition:
        raise DatasetError(f"data smoke check failed: {message}")


def run_data_smoke(data_root, n_images: int = 20, workers: int = 2, log=print, extra_checks=None) -> None:
    """Cheap end-to-end check of the data path on ~20 real images. Writes only to a temp folder.

    ``extra_checks(tmp_root, selected_records)``, if given, runs at the end while the temp folder (with the
    cache of the selected images) still exists; later phases use it to build on the same tiny dataset."""
    data_root = Path(data_root)
    records = build_index(data_root, expected_counts=None, with_sha1=False)
    log(f"smoke: OK - index of {len(records)} images, labels match filename prefixes (and the CSV if present)")
    if class_domain_counts(records) == EXPECTED_COUNTS:
        groups = validate_duplicate_groups(DUPLICATE_GROUPS, records)
        for seed in SPLIT_SEEDS:
            split = make_split(records, groups, seed)
            where = {name: part for part in ("train", "val", "test") for name in split[part]}
            smoke_require(all(len({where[n] for n in g}) == 1 for g in groups), f"a duplicate group straddles splits (seed {seed})")
        log(f"smoke: OK - {len(groups)} embedded duplicate groups ({sum(len(g) for g in groups)} images) match the index and stay in one split")
    else:
        log("smoke: SKIPPED - embedded duplicate groups are not checked: this is not the full dataset")
    selected = [
        replace(r, sha1=hashlib.sha1(read_file_bytes(data_root / r.rel_path)).hexdigest())
        for r in pick_smoke_records(records, n_images)
    ]
    with tempfile.TemporaryDirectory(prefix="csci935-smoke-") as tmp:
        tmp_root = Path(tmp)
        stats = build_cache(data_root, selected, workers=workers, output_root=tmp_root)
        smoke_require(stats.built == len(selected), f"expected {len(selected)} cached images, built {stats.built}")
        for record in selected:
            rgb = read_cached_rgb(tmp_root, record.filename)
            smoke_require(rgb.ndim == 3 and rgb.shape[2] == 3 and rgb.dtype == np.uint8, f"{record.filename}: bad array")
            smoke_require(rgb.shape[0] >= rgb.shape[1], f"{record.filename}: cached image is not portrait")
            smoke_require(max(rgb.shape[:2]) <= CACHE_LONG_SIDE, f"{record.filename}: cached image too large")
        for record in [r for r in selected if r.exif_orientation != 1][:3]:
            full = read_rgb(data_root / record.rel_path)
            cached = read_cached_rgb(tmp_root, record.filename)
            smoke_require(full.shape[0] >= full.shape[1], f"{record.filename}: EXIF-corrected image is not portrait")
            smoke_require(abs(full.shape[1] / full.shape[0] - cached.shape[1] / cached.shape[0]) < 0.01, f"{record.filename}: aspect changed")
        again = build_cache(data_root, selected, workers=workers, output_root=tmp_root)
        smoke_require(again.built == 0, "second cache run is not idempotent")
        log(f"smoke: OK - read and cached {len(selected)} images (EXIF orientations {sorted({r.exif_orientation for r in selected})}), idempotent")

        bits = load_dhashes(tmp_root, selected)
        smoke_require(bits.shape == (len(selected), 64), "dHash matrix has the wrong shape")
        smoke_require(int(np.trace(hamming_matrix(bits))) == 0, "dHash distance to itself is not 0")
        log("smoke: OK - dHash computed")

        fake = synthetic_records()
        names = {r.filename for r in fake}
        for seed in SPLIT_SEEDS:
            split = make_split(fake, [], seed)
            parts = [set(split[k]) for k in ("train", "val", "test")]
            smoke_require(sum(len(p) for p in parts) == len(names) and set.union(*parts) == names, "split does not partition")
            smoke_require(split == make_split(fake, [], seed), "split is not deterministic")
        log("smoke: OK - splits are deterministic partitions")

        write_dataset_counts(tmp_root, selected)
        save_class_domain_counts(tmp_root, selected)
        save_dataset_grid(tmp_root, selected)
        smoke_require(
            all((figures_dir(tmp_root) / f).stat().st_size > 1000 for f in ("class_domain_counts.png", "dataset_grid.png")),
            "figures were not written",
        )
        log("smoke: OK - tables and figures")
        if extra_checks is not None:
            extra_checks(tmp_root, selected)

# ---- from 20_classifier.ipynb ----
import gc
import math
import platform
import random
import re
import time
from urllib.parse import urlparse

import torch
import torch.nn.functional as F
import torchvision
from sklearn.metrics import confusion_matrix, f1_score, precision_recall_fscore_support

NUM_CLASSES = len(CLASS_NAMES)
BACKBONES = ("resnet50", "convnext_tiny", "swin_t")
INPUT_MODES = ("squash", "pad", "rect")
# (height, width) of the network input at an equal pixel budget (~100k px): E0 compares geometry, not resolution.
INPUT_SIZES = {"squash": (320, 320), "pad": (320, 320), "rect": (448, 224)}
SUBSETS = ("white", "field", "mixed")
KINDS = ("classifier", "segmenter", "analysis")


class ExperimentError(Exception):
    """Base class of errors that the CLI reports as one clean line (no traceback)."""


class UnknownExperimentError(ExperimentError):
    pass


class ChoicesError(ExperimentError):
    """A value that a gate should have written to choices.json is missing."""


class NotReadyError(ExperimentError):
    """The experiment needs a later phase that is not implemented yet."""


@dataclass(frozen=True)
class ExperimentConfig:
    exp_id: str
    backbone: str | None  # None: the winning backbone of gate G1 (choices.json "backbone")
    train_domains: tuple[str, ...]
    select_domains: tuple[str, ...]  # must equal train_domains
    test_subsets: tuple[str, ...]  # which test subsets the report uses (all three are always evaluated)
    input_mode: str | None  # None: the winning input mode of gate G0 (choices.json "input_mode")
    use_composites: bool = False  # Method A: extra training samples from CompositeSource (phase 05)
    seg_crop: bool = False  # Method B: input_hook crops to the segmenter box (phase 06)
    kind: str = "classifier"  # "segmenter" / "analysis" rows exist in the matrix but are not run here
    alias_of_winner: str = ""  # "E0": this row is the winning E0 row (same run folder, no retraining)
    # Recipe (section 6.1 of the report). Defaults are the T3.4 table.
    stage1_epochs: int = 2  # linear probe: backbone frozen, head only
    stage1_lr: float = 1e-3
    epochs: int = 30  # stage 2: fine-tune everything
    lr: float | None = None  # None: choices.json lr[backbone] (split-0 sweep over SWEEP_LRS)
    weight_decay: float = 0.05
    warmup_epochs: int = 1
    label_smoothing: float = 0.1
    batch_size: int = 32
    grad_accum: int = 1
    clip_norm: float = 1.0
    patience: int = 10  # stage-2 epochs without improvement of the selection metric
    dropout: float = 0.2
    pretrained: bool = True
    size_div: int = 1  # dev/smoke only: divide the input size (448x224 -> 112x56 with 4)
    note: str = ""

    def __post_init__(self):
        if self.kind not in KINDS:
            raise ValueError(f"{self.exp_id}: kind must be one of {KINDS}, got {self.kind!r}")
        if self.backbone is not None and self.backbone not in BACKBONES and self.kind == "classifier":
            raise ValueError(f"{self.exp_id}: unknown backbone {self.backbone!r}")
        if self.kind == "segmenter" and self.backbone not in SEG_ARCHITECTURES:  # SEG_ARCHITECTURES: 40_segmentation.ipynb
            raise ValueError(f"{self.exp_id}: unknown segmenter {self.backbone!r}, expected one of {tuple(SEG_ARCHITECTURES)}")
        if self.input_mode is not None and self.input_mode not in INPUT_MODES:
            raise ValueError(f"{self.exp_id}: unknown input mode {self.input_mode!r}")
        for name in ("train_domains", "select_domains"):
            domains = getattr(self, name)
            if not domains or not set(domains) <= set(DOMAINS):
                raise ValueError(f"{self.exp_id}: {name} must be a non-empty subset of {DOMAINS}, got {domains!r}")
        if set(self.select_domains) != set(self.train_domains):
            raise ValueError(
                f"{self.exp_id}: select_domains must equal train_domains (checkpoints are chosen on the domains "
                f"the model was trained on; anything else leaks information), got {self.select_domains} vs {self.train_domains}"
            )
        if not set(self.test_subsets) <= set(SUBSETS):
            raise ValueError(f"{self.exp_id}: test_subsets must be a subset of {SUBSETS}")

    def is_resolved(self) -> bool:
        return self.backbone is not None and self.input_mode is not None and self.lr is not None

IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)
PAD_COLOR = tuple(round(m * 255) for m in IMAGENET_MEAN)  # letterbox colour: the ImageNet mean, (124, 116, 104)

AUG_CROP_AREA = (0.6, 1.0)  # fraction of the image area kept by the random crop
AUG_ROTATION_DEG = 15.0
AUG_BRIGHTNESS = 0.2
AUG_CONTRAST = 0.2
AUG_SATURATION = 0.15
AUG_HUE = 0.02  # fraction of the hue circle: +-7.2 degrees at most


def input_size(mode: str, size_div: int = 1) -> tuple[int, int]:
    """(height, width) of the network input for an input mode. ``size_div`` > 1 is for smoke tests only."""
    if mode not in INPUT_SIZES:
        raise ValueError(f"unknown input mode {mode!r}, expected one of {INPUT_MODES}")
    height, width = INPUT_SIZES[mode]
    return max(8, height // size_div), max(8, width // size_div)


def resize_exact(rgb: np.ndarray, height: int, width: int) -> np.ndarray:
    shrinking = height * width < rgb.shape[0] * rgb.shape[1]
    return cv2.resize(rgb, (width, height), interpolation=cv2.INTER_AREA if shrinking else cv2.INTER_LINEAR)


def resize_content(rgb: np.ndarray, mode: str, size: tuple[int, int]) -> np.ndarray:
    """The image content at network resolution. For `pad` this is the aspect-preserving fit inside the
    box (smaller than the box in one dimension); `letterbox` then places it on the canvas."""
    height, width = size
    if mode != "pad":
        return resize_exact(rgb, height, width)
    scale = min(height / rgb.shape[0], width / rgb.shape[1])
    return resize_exact(rgb, max(1, round(rgb.shape[0] * scale)), max(1, round(rgb.shape[1] * scale)))


def letterbox(content: np.ndarray, size: tuple[int, int]) -> np.ndarray:
    height, width = size
    if content.shape[:2] == (height, width):
        return content
    canvas = np.empty((height, width, 3), dtype=np.uint8)
    canvas[:] = PAD_COLOR
    top, left = (height - content.shape[0]) // 2, (width - content.shape[1]) // 2
    canvas[top : top + content.shape[0], left : left + content.shape[1]] = content
    return canvas


def random_crop(rgb: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Crop covering 60-100% of the area at the image's own aspect (a zoom / framing change)."""
    height, width = rgb.shape[:2]
    side = math.sqrt(rng.uniform(*AUG_CROP_AREA))
    crop_h, crop_w = max(1, round(height * side)), max(1, round(width * side))
    top = int(rng.integers(0, height - crop_h + 1))
    left = int(rng.integers(0, width - crop_w + 1))
    return rgb[top : top + crop_h, left : left + crop_w]


def random_flips(rgb: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    flip_h, flip_v = rng.random() < 0.5, rng.random() < 0.5
    if flip_h:
        rgb = rgb[:, ::-1]
    if flip_v:
        rgb = rgb[::-1]
    return np.ascontiguousarray(rgb)


def random_rotation(rgb: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    angle = rng.uniform(-AUG_ROTATION_DEG, AUG_ROTATION_DEG)
    height, width = rgb.shape[:2]
    matrix = cv2.getRotationMatrix2D((width / 2, height / 2), angle, 1.0)
    return cv2.warpAffine(rgb, matrix, (width, height), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)


def _gray(img: np.ndarray) -> np.ndarray:
    return img[..., 0] * 0.299 + img[..., 1] * 0.587 + img[..., 2] * 0.114


def color_jitter(rgb: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Brightness, contrast, saturation (multiplicative factors) and a small hue shift, in random order."""
    brightness = rng.uniform(1 - AUG_BRIGHTNESS, 1 + AUG_BRIGHTNESS)
    contrast = rng.uniform(1 - AUG_CONTRAST, 1 + AUG_CONTRAST)
    saturation = rng.uniform(1 - AUG_SATURATION, 1 + AUG_SATURATION)
    hue = rng.uniform(-AUG_HUE, AUG_HUE)
    order = rng.permutation(4)  # all draws happen up front so the stream does not depend on the order
    img = rgb.astype(np.float32) / 255.0
    for op in order:
        if op == 0:
            img = np.clip(img * brightness, 0.0, 1.0)
        elif op == 1:
            mean = float(_gray(img).mean())
            img = np.clip((img - mean) * contrast + mean, 0.0, 1.0)
        elif op == 2:
            gray = _gray(img)[..., None]
            img = np.clip((img - gray) * saturation + gray, 0.0, 1.0)
        else:
            hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)  # float32: H in [0, 360), S and V in [0, 1]
            hsv[..., 0] = (hsv[..., 0] + hue * 360.0) % 360.0
            img = np.clip(cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB), 0.0, 1.0)
    return np.clip(img * 255.0 + 0.5, 0, 255).astype(np.uint8)


@dataclass(frozen=True)
class ImageTransform:
    """uint8 RGB image -> uint8 RGB image of the network input size. ``train`` adds the augmentation (and
    needs an ``rng``); the evaluation transform is the input-mode resize only and is deterministic."""

    mode: str
    train: bool = False
    size_div: int = 1

    @property
    def size(self) -> tuple[int, int]:
        return input_size(self.mode, self.size_div)

    def __call__(self, rgb: np.ndarray, rng: np.random.Generator | None = None) -> np.ndarray:
        if self.train:
            if rng is None:
                raise ValueError("the training transform needs an rng")
            rgb = random_rotation(random_flips(random_crop(rgb, rng), rng), rng)
        content = resize_content(np.ascontiguousarray(rgb), self.mode, self.size)
        if self.train:
            content = color_jitter(content, rng)
        return letterbox(content, self.size)


def normalize_batch(images: torch.Tensor, device) -> torch.Tensor:
    """uint8 [N, 3, H, W] -> float32 on ``device``, scaled to [0, 1] and normalised with the ImageNet mean/std."""
    x = images.to(device, non_blocking=True).float().div_(255.0)
    mean = torch.tensor(IMAGENET_MEAN, device=x.device).view(1, 3, 1, 1)
    std = torch.tensor(IMAGENET_STD, device=x.device).view(1, 3, 1, 1)
    return (x - mean) / std


def select_records(records: list[Record], filenames, domains=None) -> list[Record]:
    """Records of a split part (``filenames``, e.g. split['train']) restricted to ``domains``, in split order."""
    by_name = {r.filename: r for r in records}
    missing = [name for name in filenames if name not in by_name]
    if missing:
        raise DatasetError(f"{len(missing)} split entries are not in the index, e.g. {missing[:3]}; re-run `prepare`")
    chosen = [by_name[name] for name in filenames]
    return [r for r in chosen if domains is None or r.domain in domains]


def subsample_records(records: list[Record], n: int) -> list[Record]:
    """At most ``n`` records, round-robin over the class x domain strata (deterministic). For smoke runs."""
    queues: dict = {}
    for record in records:
        queues.setdefault(record.stratum, []).append(record)
    order = sorted(queues, key=stratum_order)
    chosen: list[Record] = []
    while len(chosen) < min(n, len(records)):
        for stratum in order:
            if queues[stratum] and len(chosen) < n:
                chosen.append(queues[stratum].pop(0))
    return chosen


def _sample_seed(seed: int) -> int:
    return int(seed) & 0x7FFFFFFF


class LeafDataset:
    """Map-style dataset over cached images.

    ``dataset[i]`` and ``dataset[(i, epoch)]`` both return ``(uint8 CHW tensor, class index, i)``. The
    augmentation of a sample is a pure function of ``(seed, epoch, i)``. Indices ``0..len(records)-1`` are
    the real records; the extra sources follow.
    """

    def __init__(self, data_root, records, transform, *, seed=0, extra_sources=(), input_hook=None, epoch=0):
        self.data_root = Path(data_root)
        self.records = list(records)
        self.transform = transform
        self.seed = _sample_seed(seed)
        self.extra_sources = tuple(extra_sources)
        self.input_hook = input_hook
        self.epoch = epoch
        self._extra_offsets = np.cumsum([0, *[len(s) for s in self.extra_sources]])

    def __len__(self) -> int:
        return len(self.records) + int(self._extra_offsets[-1])

    def sample_rng(self, index: int, epoch: int) -> np.random.Generator:
        return np.random.default_rng([self.seed, int(epoch), int(index)])

    def load_raw(self, index: int, epoch: int = 0) -> tuple[np.ndarray, int, str]:
        """(uint8 RGB before the transform, class index, name) after the hook for real images."""
        if index < len(self.records):
            record = self.records[index]
            rgb = read_cached_rgb(self.data_root, record.filename)
            if self.input_hook is not None:
                if getattr(self.input_hook, "stochastic", False):  # Method B's jittered crop: a stream of its own per sample
                    rgb = self.input_hook(rgb, record, np.random.default_rng([self.seed, int(epoch), int(index), 2]))
                else:
                    rgb = self.input_hook(rgb, record)
            return rgb, record.cls_idx, record.filename
        extra = index - len(self.records)
        which = int(np.searchsorted(self._extra_offsets, extra, side="right") - 1)
        return self.extra_sources[which].load(extra - int(self._extra_offsets[which]), epoch)

    def __getitem__(self, key):
        index, epoch = key if isinstance(key, tuple) else (key, self.epoch)
        if not 0 <= index < len(self):
            raise IndexError(index)
        rgb, label, _ = self.load_raw(index, epoch)
        rng = self.sample_rng(index, epoch) if self.transform.train else None
        image = self.transform(rgb, rng)
        return torch.from_numpy(np.ascontiguousarray(image.transpose(2, 0, 1))), int(label), index


class EpochSampler(torch.utils.data.Sampler):
    """Shuffled ``(index, epoch)`` pairs; the order is a function of (seed, epoch) only."""

    def __init__(self, n: int, seed: int):
        self.n, self.seed, self.epoch = n, _sample_seed(seed), 0

    def set_epoch(self, epoch: int) -> None:
        self.epoch = epoch

    def __len__(self) -> int:
        return self.n

    def __iter__(self):
        order = np.random.default_rng([self.seed, self.epoch]).permutation(self.n)
        return iter([(int(i), self.epoch) for i in order])


def _worker_init(worker_id: int) -> None:
    cv2.setNumThreads(0)  # OpenCV's own thread pool would fight with the DataLoader workers
    torch.set_num_threads(1)


def default_num_workers() -> int:
    """Data-loading processes, at most 4. Decoding and augmenting one image costs ~30 ms of CPU, so on a 2-vCPU
    Colab machine the workers, not the GPU, set the speed; the main process mostly waits for the GPU there, so
    every core gets a worker. From 3 cores up, one core is left to the main process."""
    try:
        cores = len(os.sched_getaffinity(0))
    except AttributeError:
        cores = os.cpu_count() or 1
    return max(1, min(4, cores if cores <= 2 else cores - 1))


def usable_workers(requested: int) -> int:
    """Workers that can really start: spawned workers re-import this file, which only works when it runs
    as the main script (the same rule as the cache's process pool)."""
    return requested if requested > 0 and pool_is_safe() else 0


def make_loader(dataset, batch_size, *, sampler=None, num_workers=0, drop_last=False, pin_memory=False, mp_context=None):
    num_workers = usable_workers(num_workers) if mp_context is None else num_workers
    mp_context = mp_context if mp_context is not None else worker_context()  # spawn, never fork (phase 02)
    kwargs = {}
    if num_workers > 0:
        kwargs.update(
            persistent_workers=True, worker_init_fn=_worker_init, multiprocessing_context=mp_context, prefetch_factor=4
        )
    return torch.utils.data.DataLoader(
        dataset,
        batch_size=batch_size,
        sampler=sampler,
        shuffle=False,
        num_workers=num_workers,
        drop_last=drop_last,
        pin_memory=pin_memory,
        **kwargs,
    )


@dataclass
class EvalSet:
    """A fully materialised evaluation set: the deterministic eval transform applied once, kept as uint8."""

    images: torch.Tensor  # [N, 3, H, W] uint8
    labels: np.ndarray  # [N] int64
    names: list[str]
    domains: list[str]

    def __len__(self) -> int:
        return len(self.names)


def materialize(dataset: LeafDataset, *, num_workers: int = 0, batch_size: int = 32) -> EvalSet:
    """Run the (deterministic) eval transform over a dataset once. Per-epoch validation then costs only the
    forward pass instead of decoding JPEGs every epoch."""
    if len(dataset) != len(dataset.records):
        raise ValueError("materialize() is for real records only (no extra_sources)")
    loader = make_loader(dataset, batch_size, num_workers=num_workers)
    batches = [images for images, _, _ in loader]
    images = torch.cat(batches) if batches else torch.empty(0, 3, *dataset.transform.size, dtype=torch.uint8)
    return EvalSet(
        images,
        np.array([r.cls_idx for r in dataset.records], dtype=np.int64),
        [r.filename for r in dataset.records],
        [r.domain for r in dataset.records],
    )

from torch import nn


@dataclass(frozen=True)
class BackboneSpec:
    builder: str  # function in torchvision.models
    weights: str  # "<Weights enum>.<member>", resolved with torchvision.models.get_weight


BACKBONE_SPECS = {
    "resnet50": BackboneSpec("resnet50", "ResNet50_Weights.IMAGENET1K_V2"),
    "convnext_tiny": BackboneSpec("convnext_tiny", "ConvNeXt_Tiny_Weights.IMAGENET1K_V1"),
    "swin_t": BackboneSpec("swin_t", "Swin_T_Weights.IMAGENET1K_V1"),
}
# Weights that `download-weights` fetches: (name, weights enum member, what it is for).
SEGMENTER_WEIGHTS = "LRASPP_MobileNet_V3_Large_Weights.COCO_WITH_VOC_LABELS_V1"
WEIGHT_TABLE = (
    ("resnet50", BACKBONE_SPECS["resnet50"].weights, "ResNet50 classifier (E0, E1)"),
    ("convnext_tiny", BACKBONE_SPECS["convnext_tiny"].weights, "ConvNeXt-Tiny classifier (E2)"),
    ("swin_t", BACKBONE_SPECS["swin_t"].weights, "Swin-Tiny classifier (E2)"),
    ("lraspp_mobilenet_v3_large", SEGMENTER_WEIGHTS, "leaf segmenter (phase 06)"),
)


def backbone_weights(backbone: str):
    return torchvision.models.get_weight(BACKBONE_SPECS[backbone].weights)


def backbone_of(model: nn.Module) -> str:
    models = torchvision.models
    for name, cls in (("resnet50", models.ResNet), ("convnext_tiny", models.ConvNeXt), ("swin_t", models.SwinTransformer)):
        if isinstance(model, cls):
            return name
    raise ValueError(f"not one of our backbones: {type(model).__name__}")


def build_model(backbone: str, num_classes: int = NUM_CLASSES, *, pretrained: bool = True, dropout: float = 0.2, data_root=None):
    """torchvision backbone with the final layer replaced by Dropout + Linear. ``pretrained=False`` (tests,
    ``predict``) builds the same architecture with random weights and downloads nothing. With ``data_root``
    the weights are read from, and downloaded to, ``<data_root>/_work/weights``."""
    if backbone not in BACKBONE_SPECS:
        raise ValueError(f"unknown backbone {backbone!r}, expected one of {BACKBONES}")
    if data_root is not None and pretrained:
        set_torch_home(data_root)
    spec = BACKBONE_SPECS[backbone]
    model = getattr(torchvision.models, spec.builder)(weights=backbone_weights(backbone) if pretrained else None)
    if backbone == "resnet50":
        model.fc = nn.Sequential(nn.Dropout(dropout), nn.Linear(model.fc.in_features, num_classes))
    elif backbone == "convnext_tiny":
        model.classifier[2] = nn.Sequential(nn.Dropout(dropout), nn.Linear(model.classifier[2].in_features, num_classes))
    else:
        model.head = nn.Sequential(nn.Dropout(dropout), nn.Linear(model.head.in_features, num_classes))
    return model


def head_module(model: nn.Module) -> nn.Module:
    return {"resnet50": lambda m: m.fc, "convnext_tiny": lambda m: m.classifier[2], "swin_t": lambda m: m.head}[
        backbone_of(model)
    ](model)


def head_parameters(model: nn.Module) -> list[nn.Parameter]:
    return list(head_module(model).parameters())


def backbone_parameters(model: nn.Module) -> list[nn.Parameter]:
    head_ids = {id(p) for p in head_parameters(model)}
    return [p for p in model.parameters() if id(p) not in head_ids]


def gradcam_target_layer(model: nn.Module) -> nn.Module:
    """Layer whose activations Grad-CAM uses. Swin's output is NHWC: pass it through `cam_to_nchw`."""
    return model.layer4 if backbone_of(model) == "resnet50" else model.features[-1]


def cam_to_nchw(activation: torch.Tensor, model: nn.Module) -> torch.Tensor:
    return activation.permute(0, 3, 1, 2) if backbone_of(model) == "swin_t" else activation


def count_parameters(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters())

def weights_dir(data_root) -> Path:
    return work_dir(data_root) / "weights"


def set_torch_home(data_root, create: bool = True) -> Path:
    """Point torch's download cache at <data_root>/_work/weights (documented location of the pretrained weights)."""
    path = weights_dir(data_root)
    if create:
        path.mkdir(parents=True, exist_ok=True)
    os.environ["TORCH_HOME"] = str(path)
    return path


def weight_checkpoint_path(weights) -> Path:
    """Where torch stores the file of a torchvision weights enum member (under the current TORCH_HOME)."""
    return Path(torch.hub.get_dir()) / "checkpoints" / Path(urlparse(weights.url).path).name


def weight_file_ok(path: Path) -> bool:
    """The file exists and, when its name carries a sha256 prefix (resnet50-11ad3fa6.pth), matches it."""
    if not path.is_file() or path.stat().st_size == 0:
        return False
    match = re.search(r"-([0-9a-f]{8})\.pth$", path.name)
    if not match:
        return True
    digest = hashlib.sha256()
    with open(fs_path(path), "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().startswith(match.group(1))


def download_weights(data_root, out=print) -> list[dict]:
    """Fetch every pretrained weight file into <data_root>/_work/weights. Safe to call repeatedly."""
    home = set_torch_home(data_root)
    out(f"download-weights: TORCH_HOME = {home}")
    rows = []
    for name, member, purpose in WEIGHT_TABLE:
        weights = torchvision.models.get_weight(member)
        path = weight_checkpoint_path(weights)
        state = "already present"
        if not weight_file_ok(path):
            if path.exists():
                path.unlink()
                state = "re-downloaded (the stored file was damaged)"
            else:
                state = "downloaded"
            weights.get_state_dict(progress=True, check_hash=True)
            if not weight_file_ok(path):
                raise ExperimentError(f"{member}: the downloaded file {path} fails its checksum")
        size = path.stat().st_size / 1e6
        out(f"  {member}: {state}\n    purpose  {purpose}\n    url      {weights.url}\n    stored   {path} ({size:.1f} MB)")
        rows.append({"name": name, "weights": member, "url": weights.url, "path": str(path), "bytes": path.stat().st_size, "state": state})
    return rows

def classification_metrics(y_true, y_pred) -> dict:
    """Accuracy, macro-F1, per-class precision / recall / F1 / support and the 5x5 confusion matrix
    (rows = true class, columns = predicted class, in CLASS_NAMES order)."""
    y_true, y_pred = np.asarray(y_true, dtype=np.int64), np.asarray(y_pred, dtype=np.int64)
    n = int(len(y_true))
    if n == 0:
        return {"n": 0, "accuracy": None, "macro_f1": None, "per_class": {}, "confusion_matrix": []}
    labels = list(range(NUM_CLASSES))
    precision, recall, f1, support = precision_recall_fscore_support(y_true, y_pred, labels=labels, zero_division=0)
    present = sorted(set(y_true.tolist()) | set(y_pred.tolist()))
    return {
        "n": n,
        "accuracy": float((y_true == y_pred).mean()),
        "macro_f1": float(f1_score(y_true, y_pred, labels=present, average="macro", zero_division=0)),
        "per_class": {
            name: {"precision": float(precision[i]), "recall": float(recall[i]), "f1": float(f1[i]), "support": int(support[i])}
            for i, name in enumerate(CLASS_NAMES)
        },
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=labels).tolist(),
    }


def subset_mask(domains, subset: str) -> np.ndarray:
    domains = np.asarray(domains)
    return np.ones(len(domains), dtype=bool) if subset == "mixed" else domains == subset


def subset_metrics(probs: np.ndarray, labels, domains) -> dict:
    """{"white": ..., "field": ..., "mixed": ..., "domain_balanced": {"accuracy", "macro_f1"}} for one split part."""
    preds = probs.argmax(axis=1)
    result = {s: classification_metrics(labels[m], preds[m]) for s in SUBSETS for m in [subset_mask(domains, s)]}
    balanced = {}
    for key in ("accuracy", "macro_f1"):
        values = [result[s][key] for s in DOMAINS]
        balanced[key] = None if any(v is None for v in values) else float(np.mean(values))
    result["domain_balanced"] = balanced
    return result


def macro_f1(labels, preds) -> float:
    return classification_metrics(labels, preds)["macro_f1"] if len(labels) else float("nan")


@torch.no_grad()
def predict_probs(model: nn.Module, images: torch.Tensor, device, *, batch_size: int = 64, amp: bool = False) -> np.ndarray:
    """Softmax probabilities [N, 5] (float32, numpy) for a uint8 image tensor."""
    model.eval()
    out = []
    for start in range(0, len(images), batch_size):
        x = normalize_batch(images[start : start + batch_size], device)
        with torch.autocast(device_type="cuda", dtype=torch.float16, enabled=amp):
            logits = model(x)
        out.append(torch.softmax(logits.float(), dim=1).cpu())
    return torch.cat(out).numpy() if out else np.zeros((0, NUM_CLASSES), dtype=np.float32)


def evaluate_model(model: nn.Module, eval_set: EvalSet, device, *, amp: bool = False) -> tuple[dict, np.ndarray]:
    """(metrics for white / field / mixed / domain_balanced, probabilities) of a model on an EvalSet."""
    probs = predict_probs(model, eval_set.images, device, amp=amp)
    return subset_metrics(probs, eval_set.labels, eval_set.domains), probs

import contextlib

FALLBACK_BATCH = 16


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed % (2**32))
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def lr_at_step(step: int, *, base_lr: float, warmup_steps: int, total_steps: int) -> float:
    """Linear warmup over ``warmup_steps`` optimiser steps, then cosine decay to 0 at ``total_steps``."""
    if warmup_steps > 0 and step < warmup_steps:
        return base_lr * (step + 1) / warmup_steps
    progress = (step - warmup_steps) / max(1, total_steps - warmup_steps)
    return base_lr * 0.5 * (1.0 + math.cos(math.pi * min(1.0, max(0.0, progress))))


class CheckpointSelector:
    """Remembers the best state by the selection metric and decides when to stop early. Only epochs that are
    passed with ``counts_for_patience=True`` (stage 2) can run the patience out."""

    def __init__(self, patience: int):
        self.patience, self.stale = patience, 0
        self.best_score, self.best_epoch, self.best_state = -math.inf, 0, None

    def update(self, score: float, epoch: int, snapshot, *, counts_for_patience: bool) -> bool:
        """Record an epoch. ``snapshot`` is a function returning the state to keep. True if it is the new best."""
        if score > self.best_score:
            self.best_score, self.best_epoch, self.best_state, self.stale = score, epoch, snapshot(), 0
            return True
        if counts_for_patience:
            self.stale += 1
        return False

    @property
    def should_stop(self) -> bool:
        return self.stale >= self.patience


def is_out_of_memory(exc: BaseException) -> bool:
    return isinstance(exc, torch.cuda.OutOfMemoryError) or (
        isinstance(exc, RuntimeError) and "out of memory" in str(exc).lower()
    )


def free_device_memory(device: str) -> None:
    gc.collect()
    if device == "cuda":
        torch.cuda.empty_cache()
    elif device == "mps":
        torch.mps.empty_cache()


def cpu_state_dict(model: nn.Module) -> dict:
    return {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}


@dataclass
class TrainOutcome:
    best_state: dict
    best_epoch: int
    best_score: float
    history: list[dict]
    stopped_early: bool
    seconds: float


def train_classifier(cfg: ExperimentConfig, model: nn.Module, train_ds: LeafDataset, val_set: EvalSet, device: str, *,
                     seed: int, num_workers: int = 0, mp_context=None, log=print) -> TrainOutcome:
    """The two-stage LP-FT loop. Returns the best checkpoint (by validation macro-F1 on cfg.select_domains)."""
    started = time.time()
    amp = device == "cuda"
    sampler = EpochSampler(len(train_ds), seed)
    drop_last = len(train_ds) % cfg.batch_size == 1  # a final batch of one sample breaks BatchNorm
    loader = make_loader(train_ds, cfg.batch_size, sampler=sampler, num_workers=num_workers, drop_last=drop_last,
                         pin_memory=device == "cuda", mp_context=mp_context)
    micro_steps = len(loader)
    steps_per_epoch = math.ceil(micro_steps / cfg.grad_accum)
    select_mask = np.isin(np.asarray(val_set.domains), cfg.select_domains)
    if not select_mask.any():
        raise ExperimentError(f"{cfg.exp_id}: the validation part has no images of the domains {cfg.select_domains}")
    scaler = torch.amp.GradScaler("cuda", enabled=amp)
    selector = CheckpointSelector(cfg.patience)
    history: list[dict] = []
    epoch = 0
    stopped_early = False
    head_params = head_parameters(model)

    for stage, n_epochs in (("lp", cfg.stage1_epochs), ("ft", cfg.epochs)):
        if n_epochs <= 0:
            continue
        trainable = head_params if stage == "lp" else list(model.parameters())
        for p in model.parameters():
            p.requires_grad_(False)
        for p in trainable:
            p.requires_grad_(True)
        base_lr = cfg.stage1_lr if stage == "lp" else cfg.lr
        optimizer = torch.optim.AdamW(trainable, lr=base_lr, weight_decay=cfg.weight_decay)
        total_steps = n_epochs * steps_per_epoch
        warmup_steps = cfg.warmup_epochs * steps_per_epoch if stage == "ft" else 0
        step = 0
        for _ in range(n_epochs):
            epoch += 1
            epoch_started = time.time()
            sampler.set_epoch(epoch - 1)
            train_ds.epoch = epoch - 1
            model.train() if stage == "ft" else model.eval()  # LP: frozen backbone incl. BatchNorm statistics
            if stage == "lp":
                head_module(model).train()
            loss_sum, seen, lr_now = 0.0, 0, base_lr
            optimizer.zero_grad(set_to_none=True)
            for i, (images, labels, _) in enumerate(loader):
                x = normalize_batch(images, device)
                y = labels.to(device)
                with torch.autocast(device_type="cuda", dtype=torch.float16, enabled=amp):
                    loss = F.cross_entropy(model(x), y, label_smoothing=cfg.label_smoothing)
                loss_value = loss.item()
                if not math.isfinite(loss_value):
                    raise ExperimentError(f"{cfg.exp_id}: the training loss became {loss_value} (diverged); try a lower lr")
                scaler.scale(loss / cfg.grad_accum).backward()
                loss_sum += loss_value * len(y)
                seen += len(y)
                if (i + 1) % cfg.grad_accum == 0 or i + 1 == micro_steps:
                    lr_now = base_lr if stage == "lp" else lr_at_step(step, base_lr=base_lr, warmup_steps=warmup_steps,
                                                                    total_steps=total_steps)
                    for group in optimizer.param_groups:
                        group["lr"] = lr_now
                    scaler.unscale_(optimizer)
                    torch.nn.utils.clip_grad_norm_(trainable, cfg.clip_norm)
                    scaler.step(optimizer)
                    scaler.update()
                    optimizer.zero_grad(set_to_none=True)
                    step += 1
            probs = predict_probs(model, val_set.images, device, amp=amp)
            preds, labels_np = probs.argmax(axis=1), val_set.labels
            domains = np.asarray(val_set.domains)
            score = macro_f1(labels_np[select_mask], preds[select_mask])
            improved = selector.update(score, epoch, lambda: cpu_state_dict(model), counts_for_patience=stage == "ft")
            row = {
                "epoch": epoch, "stage": stage, "lr": lr_now, "train_loss": loss_sum / max(1, seen),
                "val_loss": float(-np.log(np.clip(probs[np.arange(len(labels_np)), labels_np], 1e-8, 1.0)).mean()),
                "val_macro_f1": score,
                "val_accuracy": float((preds[select_mask] == labels_np[select_mask]).mean()),
                "val_f1_white": macro_f1(labels_np[domains == "white"], preds[domains == "white"]),
                "val_f1_field": macro_f1(labels_np[domains == "field"], preds[domains == "field"]),
                "val_f1_mixed": macro_f1(labels_np, preds),
                "best": int(improved), "seconds": time.time() - epoch_started,
            }
            history.append(row)
            log(f"  epoch {epoch:2d}/{cfg.stage1_epochs + cfg.epochs} {stage}  lr {lr_now:.2e}  loss {row['train_loss']:.3f}  "
                f"val F1 {score:.3f}{' *' if improved else '  '} (white {row['val_f1_white']:.3f} field {row['val_f1_field']:.3f})  "
                f"{row['seconds']:.1f}s")
            if stage == "ft" and selector.should_stop:
                stopped_early = True
                log(f"  early stop: no improvement for {cfg.patience} fine-tuning epochs (best epoch {selector.best_epoch})")
                break
    return TrainOutcome(selector.best_state, selector.best_epoch, selector.best_score, history, stopped_early,
                        time.time() - started)

import io

RUN_FORMAT = 1
FINGERPRINT_IGNORED = ("batch_size", "grad_accum")
RUN_FILES = ("config.json", "env.json", "history.csv", "predictions_val.csv", "predictions_test.csv", "metrics.json")


def runs_dir(data_root) -> Path:
    return work_dir(data_root) / "runs"


def sweep_dir(data_root) -> Path:
    return runs_dir(data_root) / "sweep"


def scratch_dir(data_root) -> Path:
    return runs_dir(data_root) / "scratch"


def lr_tag(lr: float) -> str:
    """1e-4 -> '1e-4', 3e-4 -> '3e-4' (used in sweep folder names)."""
    return f"{lr:.0e}".replace("e-0", "e-").replace("e+0", "e+")


def sweep_run_name(exp_id: str, lr: float) -> str:
    return f"{exp_id}_lr{lr_tag(lr)}"


def split_dir(root: Path, split_seed: int) -> Path:
    return Path(root) / f"split_{split_seed}"


def config_fingerprint(cfg: ExperimentConfig, extra: dict | None = None) -> str:
    payload = {k: v for k, v in asdict(cfg).items() if k not in FINGERPRINT_IGNORED}
    payload.update(extra or {})
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()


def environment_record(device: str) -> dict:
    import numpy
    import sklearn

    info = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "torch": torch.__version__,
        "torchvision": torchvision.__version__,
        "opencv": cv2.__version__,
        "numpy": numpy.__version__,
        "sklearn": sklearn.__version__,
        "device": device,
        "cpu_count": os.cpu_count(),
        "torch_home": os.environ.get("TORCH_HOME", ""),
        "gpu": None,
        "cuda": torch.version.cuda,
    }
    if device == "cuda":
        info["gpu"] = torch.cuda.get_device_name(0)
    elif device == "mps":
        info["gpu"] = "Apple MPS"
    return info


def fmt3(value) -> str:
    return "n/a" if value is None else f"{value:.3f}"


def csv_text(header: list[str], rows) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(header)
    writer.writerows(rows)
    return buffer.getvalue()


HISTORY_COLUMNS = ["epoch", "stage", "lr", "train_loss", "val_loss", "val_macro_f1", "val_accuracy",
                   "val_f1_white", "val_f1_field", "val_f1_mixed", "best", "seconds"]


def history_csv(history: list[dict]) -> str:
    return csv_text(HISTORY_COLUMNS, [[f"{row[c]:.6g}" if isinstance(row[c], float) else row[c] for c in HISTORY_COLUMNS] for row in history])


def predictions_csv(eval_set: EvalSet, probs: np.ndarray) -> str:
    preds = probs.argmax(axis=1)
    rows = [
        [name, domain, CLASS_NAMES[int(true)], CLASS_NAMES[int(pred)], *[f"{p:.6f}" for p in row]]
        for name, domain, true, pred, row in zip(eval_set.names, eval_set.domains, eval_set.labels, preds, probs)
    ]
    return csv_text(["filename", "domain", "true", "pred", *[f"p{i}" for i in range(NUM_CLASSES)]], rows)


def save_torch_atomic(obj, path: Path) -> None:
    path = Path(path)
    os.makedirs(fs_path(path.parent), exist_ok=True)
    tmp = path.with_name(path.name + f".tmp{os.getpid()}")
    with open(fs_path(tmp), "wb") as handle:
        torch.save(obj, handle)
    os.replace(fs_path(tmp), fs_path(path))


def read_metrics(run_dir: Path) -> dict | None:
    path = Path(run_dir) / "metrics.json"
    if not path.is_file():
        return None
    try:
        return json.loads(read_file_bytes(path).decode("utf-8"))
    except ValueError:
        return None  # atomic writes make this impossible in practice; treat as "not done"


def result_state(run_dir: Path, split_sha256: str, fingerprint: str) -> tuple[str, str]:
    """('fresh' | 'stale' | 'missing', reason) for the metrics.json of a run folder."""
    metrics = read_metrics(run_dir)
    if metrics is None:
        return "missing", "no metrics.json"
    if metrics.get("split_sha256") != split_sha256:
        return "stale", "the split changed since this run (split sha256 differs)"
    if metrics.get("config_fingerprint") != fingerprint:
        return "stale", "the experiment config changed since this run (config fingerprint differs)"
    return "fresh", "metrics.json is current"


def make_extra_sources(cfg: ExperimentConfig, data_root, split_seed: int, seed: int, *, n_factor: float = 1.0,
                       limit: int | None = None) -> tuple:
    """Extra training samples: ``(CompositeSource,)`` for the Method A experiments (``cfg.use_composites``), else ``()``.
    ``n_factor`` scales the composites per epoch (x the white training count, chosen by `choose-composites`);
    ``limit`` caps them for --fast. See `build_composite_source` in 30_copy_paste.ipynb."""
    if not cfg.use_composites:
        return ()
    return (build_composite_source(data_root, split_seed, seed, n_factor=n_factor, limit=limit),)


def make_input_hook(cfg: ExperimentConfig, data_root, split_seed: int, *, train: bool = False, seg_dir=None):
    """``hook(image, record) -> image`` applied before the transforms: ``None``, or for Method B (``cfg.seg_crop``) the
    `SegCropHook` that crops to the stored box of the split-``k`` segmenter (``_work/runs/S-seg/split_<k>/boxes.json`` unless
    ``seg_dir`` names another S-seg runs folder), jittered by +-5% when ``train`` and exact otherwise. Raises ExperimentError
    when the boxes do not exist. ``record`` is None for ad-hoc images (the predict command, which uses `LiveCropHook`)."""
    if not cfg.seg_crop:
        return None
    return SegCropHook(load_boxes(data_root, split_seed, seg_dir), classifier_aspect(cfg.input_mode, cfg.size_div), SEG_JITTER if train else 0.0)


def check_cache_complete(data_root, records: list[Record]) -> None:
    missing = [r.filename for r in records if not (cache_dir(data_root) / r.filename).is_file()]
    if missing:
        raise DatasetError(f"{len(missing)} cached images are missing under {cache_dir(data_root)}, e.g. {missing[:3]}; run `prepare`")

@dataclass(frozen=True)
class RunOptions:
    """How to run (as opposed to what to run): nothing here changes the experiment's result definition."""

    device: str = "cpu"
    seed_offset: int = 0
    num_workers: int | None = None  # None: default_num_workers()
    force: bool = False
    limit: int | None = None  # --fast: at most this many images per split part
    overrides: tuple = ()  # (name, value) pairs applied on top of the registry, recorded in config.json
    weights_root: Path | None = None  # where the pretrained weights live (default: the data root)
    mp_context: str | None = None  # tests only: force the worker start method
    seg_dir: Path | None = None  # Method B: the S-seg runs folder to read boxes.json from (default: _work/runs/S-seg)


def train_with_fallback(cfg, train_ds, val_set, options: RunOptions, seed: int, log):
    """Build a fresh model and train it; on out-of-memory retry once with batch 16 and accumulation x2
    (same effective batch). Returns (model, outcome, cfg actually used)."""
    workers = default_num_workers() if options.num_workers is None else options.num_workers
    while True:
        try:
            seed_everything(seed)
            model = build_model(cfg.backbone, pretrained=cfg.pretrained, dropout=cfg.dropout,
                                data_root=options.weights_root).to(options.device)
            outcome = train_classifier(cfg, model, train_ds, val_set, options.device, seed=seed, num_workers=workers,
                                       mp_context=options.mp_context, log=log)
            return model, outcome, cfg
        except Exception as exc:
            if not (is_out_of_memory(exc) and cfg.batch_size > FALLBACK_BATCH):
                raise
            model = None
            log(f"  out of memory at batch {cfg.batch_size}: retrying with batch {FALLBACK_BATCH} and gradient accumulation "
                f"{cfg.grad_accum * cfg.batch_size // FALLBACK_BATCH}")
            cfg = replace(cfg, batch_size=FALLBACK_BATCH, grad_accum=cfg.grad_accum * cfg.batch_size // FALLBACK_BATCH)
        free_device_memory(options.device)


def run_split(resolved: "ResolvedExperiment", split_seed: int, *, data_root, out_dir: Path, options: RunOptions,
              log=print) -> dict:
    """Train and evaluate one experiment on one split and write the run folder (see the table above).

    Returns {"status": "skipped" | "done", "metrics": dict, "out_dir": Path}."""
    data_root, out_dir = Path(data_root), Path(out_dir)
    cfg = resolved.config
    split = load_split(data_root, split_seed)  # verifies the sha256
    fingerprint = config_fingerprint(cfg, {"seed_offset": options.seed_offset, "limit": options.limit,
                                           **composite_fingerprint_extra(cfg, resolved.composite_factor), **seg_fingerprint_extra(cfg)})
    boxes_sha = None
    if cfg.seg_crop:  # Method B: fail clearly, before anything is skipped or trained, if the segmenter's boxes are missing
        load_boxes(data_root, split_seed, options.seg_dir)
        boxes_sha = file_sha256(boxes_path(data_root, split_seed, options.seg_dir))
    state, reason = result_state(out_dir, split["sha256"], fingerprint)
    if state == "fresh" and boxes_sha is not None and read_metrics(out_dir).get("seg_boxes_sha256") != boxes_sha:
        state, reason = "stale", "the S-seg boxes of this split changed since this run (boxes.json sha256 differs)"
    if state == "fresh" and not options.force:
        log(f"[{resolved.requested} split {split_seed}] skipped: {out_dir / 'metrics.json'} exists and is current (--force to retrain)")
        return {"status": "skipped", "metrics": read_metrics(out_dir), "out_dir": out_dir}
    if state == "stale":
        log(f"[{resolved.requested} split {split_seed}] existing result is stale: {reason}; retraining")
    (out_dir / "metrics.json").unlink(missing_ok=True)  # a half-finished retrain must not look complete

    started = time.time()
    seed = split_seed + options.seed_offset
    records = load_index(data_root)
    train_recs = select_records(records, split["train"], cfg.train_domains)
    val_recs = select_records(records, split["val"])
    test_recs = select_records(records, split["test"])
    if options.limit:
        train_recs, val_recs, test_recs = (subsample_records(r, options.limit) for r in (train_recs, val_recs, test_recs))
    check_cache_complete(data_root, [*train_recs, *val_recs, *test_recs])

    extra_sources = make_extra_sources(cfg, data_root, split_seed, seed, n_factor=resolved.composite_factor or 1.0,
                                       limit=options.limit)
    input_hook = make_input_hook(cfg, data_root, split_seed, seg_dir=options.seg_dir)
    train_hook = make_input_hook(cfg, data_root, split_seed, train=True, seg_dir=options.seg_dir)
    train_tf = ImageTransform(cfg.input_mode, train=True, size_div=cfg.size_div)
    eval_tf = ImageTransform(cfg.input_mode, train=False, size_div=cfg.size_div)
    train_ds = LeafDataset(data_root, train_recs, train_tf, seed=seed, extra_sources=extra_sources, input_hook=train_hook)
    workers = default_num_workers() if options.num_workers is None else options.num_workers
    val_set = materialize(LeafDataset(data_root, val_recs, eval_tf, input_hook=input_hook), num_workers=workers)

    log(f"[{resolved.requested} split {split_seed}] {cfg.exp_id}: {cfg.backbone} / {cfg.input_mode}  lr {cfg.lr:g}  "
        f"train {len(train_ds)} ({'+'.join(cfg.train_domains)}), val {len(val_set)}, test {len(test_recs)}  "
        f"device {options.device}, batch {cfg.batch_size}x{cfg.grad_accum}, workers {usable_workers(workers)}")
    write_json(out_dir / "config.json", {
        "format": RUN_FORMAT, "requested_exp_id": resolved.requested, "experiment": asdict(cfg),
        "split": split_seed, "seed": seed, "seed_offset": options.seed_offset, "limit": options.limit,
        "choices_used": resolved.choices_used, "notes": list(resolved.notes), "overrides": dict(options.overrides),
        "seg_boxes_sha256": boxes_sha,
        "weights": BACKBONE_SPECS[cfg.backbone].weights if cfg.pretrained else None,
        "input_size": list(input_size(cfg.input_mode, cfg.size_div)), "config_fingerprint": fingerprint,
    })
    write_json(out_dir / "env.json", environment_record(options.device))

    model, outcome, used_cfg = train_with_fallback(cfg, train_ds, val_set, options, seed, log)
    model.load_state_dict(outcome.best_state)
    amp = options.device == "cuda"
    val_metrics, val_probs = evaluate_model(model, val_set, options.device, amp=amp)
    test_set = materialize(LeafDataset(data_root, test_recs, eval_tf, input_hook=input_hook), num_workers=workers)
    test_metrics, test_probs = evaluate_model(model, test_set, options.device, amp=amp)

    write_text_atomic(out_dir / "history.csv", history_csv(outcome.history))
    write_text_atomic(out_dir / "predictions_val.csv", predictions_csv(val_set, val_probs))
    write_text_atomic(out_dir / "predictions_test.csv", predictions_csv(test_set, test_probs))
    save_torch_atomic({
        "format": RUN_FORMAT, "state_dict": outcome.best_state, "backbone": cfg.backbone, "input_mode": cfg.input_mode,
        "size_div": cfg.size_div, "dropout": cfg.dropout, "class_names": list(CLASS_NAMES), "epoch": outcome.best_epoch,
        "val_select_macro_f1": outcome.best_score, "exp_id": cfg.exp_id, "split": split_seed, "config": asdict(cfg),
    }, out_dir / "best.pt")
    epoch_seconds = [row["seconds"] for row in outcome.history]
    metrics = {
        "format": RUN_FORMAT, "exp_id": cfg.exp_id, "requested_exp_id": resolved.requested, "split": split_seed,
        "seed": seed, "split_sha256": split["sha256"], "config_fingerprint": fingerprint,
        "wall_time_s": round(time.time() - started, 2), "train_time_s": round(outcome.seconds, 2),
        "seconds_per_epoch": round(float(np.mean(epoch_seconds)), 3) if epoch_seconds else None,
        "device": options.device, "backbone": cfg.backbone, "input_mode": cfg.input_mode, "lr": cfg.lr,
        "parameters": count_parameters(model), "train_domains": list(cfg.train_domains),
        "select_domains": list(cfg.select_domains), "test_subsets": list(cfg.test_subsets),
        "n_train": len(train_ds), "n_val": len(val_set), "n_test": len(test_set),
        "epochs_run": len(outcome.history), "best_epoch": outcome.best_epoch,
        "best_val_select_macro_f1": outcome.best_score, "stopped_early": outcome.stopped_early,
        "batch_size": used_cfg.batch_size, "grad_accum": used_cfg.grad_accum,
        "oom_fallback": used_cfg.batch_size != cfg.batch_size, "fast": options.limit is not None,
        "overrides": dict(options.overrides), "val": val_metrics, "test": test_metrics,
    }
    if cfg.use_composites:
        metrics["composites"] = {"n_factor": resolved.composite_factor or 1.0, "n_per_epoch": len(extra_sources[0]),
                                 "recipe": COMPOSITE_RECIPE, "scale": extra_sources[0].scale}
    if cfg.seg_crop:
        metrics["seg_boxes_sha256"] = boxes_sha
    write_json(out_dir / "metrics.json", metrics, indent=1)  # last: its presence marks the run as complete
    log(f"[{resolved.requested} split {split_seed}] done in {metrics['wall_time_s']:.0f}s  best epoch {outcome.best_epoch}  "
        f"val mixed F1 {fmt3(val_metrics['mixed']['macro_f1'])}  test F1 mixed {fmt3(test_metrics['mixed']['macro_f1'])} "
        f"white {fmt3(test_metrics['white']['macro_f1'])} field {fmt3(test_metrics['field']['macro_f1'])}")
    return {"status": "done", "metrics": metrics, "out_dir": out_dir}

def load_run_model(run_dir, device: str = "cpu") -> tuple[nn.Module, dict]:
    """(model in eval mode on ``device``, checkpoint dict) from <run_dir>/best.pt."""
    path = Path(run_dir) / "best.pt"
    if not path.is_file():
        raise ExperimentError(
            f"{path} does not exist. Checkpoints are not synced back from Colab by default "
            "(*.pt is excluded): re-run the batch with keep_checkpoints=True, or copy best.pt from the Colab session."
        )
    checkpoint = torch.load(fs_path(path), map_location="cpu", weights_only=True)
    model = build_model(checkpoint["backbone"], pretrained=False, dropout=checkpoint["dropout"])
    model.load_state_dict(checkpoint["state_dict"])
    return model.to(device).eval(), checkpoint


def read_image_like_the_cache(path) -> np.ndarray:
    """An arbitrary JPEG as the classifier saw its training images: EXIF applied, portrait, long side <= 1280."""
    return resize_long_side(read_rgb(path), CACHE_LONG_SIDE)


def classify_rgb(model: nn.Module, checkpoint: dict, rgb: np.ndarray, device: str, input_hook=None) -> np.ndarray:
    """Class probabilities [5] of one RGB image under the evaluation pipeline of the checkpoint's experiment."""
    if input_hook is not None:
        rgb = input_hook(rgb, None)
    transform = ImageTransform(checkpoint["input_mode"], train=False, size_div=checkpoint["size_div"])
    batch = torch.from_numpy(np.ascontiguousarray(transform(rgb).transpose(2, 0, 1)))[None]
    return predict_probs(model, batch, device)[0]


def format_prediction(image, probs: np.ndarray, label: str) -> str:
    order = np.argsort(-probs)
    lines = [f"image       {image}", f"model       {label}", f"prediction  {CLASS_NAMES[order[0]]} ({100 * probs[order[0]]:.1f}%)", "probabilities"]
    lines += [f"  {CLASS_NAMES[i]:<14}{100 * probs[i]:5.1f}%  {'#' * round(40 * probs[i])}" for i in order]
    return "\n".join(lines)


def live_crop_hook(run_dir, cfg: ExperimentConfig, split_seed: int, device: str, seg_dir=None) -> "LiveCropHook":
    """Method B for a new image: the hook that runs the split-``k`` segmenter (its ``best.pt`` in the S-seg folder next to the
    experiment's folder, or ``seg_dir``) and crops to its box."""
    seg_run = split_dir(Path(seg_dir) if seg_dir is not None else Path(run_dir).parent.parent / "S-seg", split_seed)
    model, checkpoint = load_seg_run_model(seg_run, device)
    return LiveCropHook(model, device, classifier_aspect(cfg.input_mode, cfg.size_div), checkpoint.get("size_div", 1))


def predict_image(run_dir, image, device: str, data_root=None, out=print, seg_dir=None) -> np.ndarray:
    """Class probabilities of one image. For a Method B experiment (``seg_crop``) the image is first segmented by the
    split's segmenter and cropped to the leaf box, then classified."""
    model, checkpoint = load_run_model(run_dir, device)
    cfg = ExperimentConfig(**checkpoint["config"])
    hook = live_crop_hook(run_dir, cfg, checkpoint["split"], device, seg_dir) if cfg.seg_crop else None
    probs = classify_rgb(model, checkpoint, read_image_like_the_cache(image), device, hook)
    out(format_prediction(image, probs, f"{checkpoint['exp_id']} split {checkpoint['split']} ({Path(run_dir) / 'best.pt'})"))
    if hook is not None and hook.last is not None:
        x0, y0, x1, y1 = hook.last["crop"]
        out(f"segmenter   crop box x {x0}-{x1}, y {y0}-{y1}" + ("  (no leaf found: whole image)" if hook.last["fallback"] else f"  (leaf covers {100 * hook.last['area']:.0f}% of the image)"))
    return probs

# ---- from 30_copy_paste.ipynb ----
import math
import time

MASK_BLUR_KSIZE = 5  # Gaussian blur before the HSV conversion (pixels, odd)
MASK_V_MIN = 20  # minimum brightness (V, 0-255) of a leaf pixel; only near-black pixels are dropped
MASK_CLOSE_KSIZE = 45  # elliptical closing kernel (px at the 1280 px cache scale): fills pale lesions
MASK_OPEN_KSIZE = 7  # elliptical opening kernel: removes specks
MASK_RECIPE_VERSION = 1  # bump when the algorithm (not a constant) changes
MASK_CONSTANTS = {
    "version": MASK_RECIPE_VERSION, "blur": MASK_BLUR_KSIZE, "v_min": MASK_V_MIN,
    "close": MASK_CLOSE_KSIZE, "open": MASK_OPEN_KSIZE,
}
MASK_RECIPE = hashlib.sha1(json.dumps(MASK_CONSTANTS, sort_keys=True).encode()).hexdigest()[:12]


def fill_holes(mask: np.ndarray) -> np.ndarray:
    """``mask`` (uint8 0/255) with every background region that does not touch the border filled in
    (scipy-free: flood fill the outside of a 1 px padded copy with cv2.floodFill)."""
    padded = cv2.copyMakeBorder(mask, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)
    flooded = padded.copy()
    cv2.floodFill(flooded, np.zeros((padded.shape[0] + 2, padded.shape[1] + 2), np.uint8), (0, 0), 255)
    holes = cv2.bitwise_not(flooded)[1:-1, 1:-1]
    return mask | holes


def largest_component(mask: np.ndarray) -> np.ndarray:
    """uint8 0/255 mask reduced to its largest 8-connected component (an empty mask stays empty)."""
    count, labels, stats, _ = cv2.connectedComponentsWithStats((mask > 0).astype(np.uint8), connectivity=8)
    if count <= 1:
        return np.zeros_like(mask)
    keep = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    return ((labels == keep) * 255).astype(np.uint8)


def white_pseudo_mask(rgb: np.ndarray) -> np.ndarray:
    """Leaf mask (uint8 0/255, same height and width) of a white-background image; see the section text."""
    hsv = cv2.cvtColor(cv2.GaussianBlur(rgb, (MASK_BLUR_KSIZE, MASK_BLUR_KSIZE), 0), cv2.COLOR_RGB2HSV)
    saturation, value = hsv[..., 1], hsv[..., 2]
    threshold, _ = cv2.threshold(saturation, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    mask = (((saturation > threshold) & (value > MASK_V_MIN)).astype(np.uint8)) * 255
    ellipse = lambda size: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (size, size))  # noqa: E731
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, ellipse(MASK_CLOSE_KSIZE))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, ellipse(MASK_OPEN_KSIZE))
    return largest_component(fill_holes(mask))


def white_masks_dir(data_root) -> Path:
    return work_dir(data_root) / "masks" / "white"


def white_mask_path(data_root, filename: str) -> Path:
    return white_masks_dir(data_root) / f"{filename}.png"


def white_rejects_path(data_root) -> Path:
    return work_dir(data_root) / "masks" / "white_rejects.txt"


def read_mask_file(path) -> np.ndarray:
    mask = cv2.imdecode(np.frombuffer(read_file_bytes(path), np.uint8), cv2.IMREAD_GRAYSCALE)
    if mask is None:
        raise DatasetError(f"{path}: cannot decode mask")
    return mask


def read_white_mask(data_root, filename: str) -> np.ndarray:
    """The stored pseudo-mask (uint8 0/255) of a white image."""
    path = white_mask_path(data_root, filename)
    if not path.is_file():
        raise DatasetError(f"{path} does not exist; run `prepare` (or `run`, which builds the masks it needs)")
    return read_mask_file(path)


def _mask_one(task: tuple) -> tuple[str, float]:
    """Worker: cached image -> mask PNG. Returns (filename, mask area as a fraction of the image)."""
    filename, source, target = task
    mask = white_pseudo_mask(read_rgb(source))
    ok, buffer = cv2.imencode(".png", mask)
    if not ok:
        raise DatasetError(f"{filename}: PNG encoding failed")
    write_bytes_atomic(Path(target), buffer.tobytes())
    return filename, float((mask > 0).mean())


@dataclass
class MaskStats:
    total: int
    built: int
    reused: int


def white_masks_manifest_path(data_root) -> Path:
    return white_masks_dir(data_root) / "manifest.json"


def load_white_mask_manifest(data_root) -> dict:
    path = white_masks_manifest_path(data_root)
    if path.is_file():
        try:
            manifest = json.loads(read_file_bytes(path).decode("utf-8"))
            if manifest.get("recipe") == MASK_RECIPE:
                return manifest
        except (OSError, ValueError):
            pass
    return {"recipe": MASK_RECIPE, "files": {}}  # damaged, or made by another recipe: rebuild everything


def build_white_masks(data_root, records: list[Record], *, workers: int | None = None, log=None) -> MaskStats:
    """Pseudo-masks of the white images among ``records`` (idempotent: an up-to-date mask is kept). A mask is up to
    date when its file exists, the manifest was written by this recipe and the source sha1 is unchanged."""
    data_root = Path(data_root)
    manifest = load_white_mask_manifest(data_root)
    files = manifest["files"]
    white = [r for r in records if r.domain == "white"]

    def current(record: Record) -> bool:
        entry = files.get(record.filename)
        return bool(entry) and entry.get("sha1") == record.sha1 and white_mask_path(data_root, record.filename).is_file()

    todo = [r for r in white if not current(r)]
    sha_of = {r.filename: r.sha1 for r in todo}
    tasks = [(r.filename, str(cache_dir(data_root) / r.filename), str(white_mask_path(data_root, r.filename))) for r in todo]
    for task in tasks:
        if not Path(task[1]).is_file():
            raise DatasetError(f"{task[1]} is missing; run `prepare` to build the cache")
    done = 0
    try:
        for filename, area in run_parallel(_mask_one, tasks, workers=workers or default_workers()):
            files[filename] = {"sha1": sha_of[filename], "area": area}
            done += 1
            if log and done % 200 == 0:
                log(f"masks: {done}/{len(tasks)}")
    finally:
        if done:
            write_json(white_masks_manifest_path(data_root), {"recipe": MASK_RECIPE, "files": dict(sorted(files.items()))})
    return MaskStats(total=len(white), built=len(todo), reused=len(white) - len(todo))


def white_rejects_source(records: list[Record]) -> str:
    """Where `load_white_rejects` takes the list from, for log lines."""
    return "embedded WHITE_REJECTS" if class_domain_counts(records) == EXPECTED_COUNTS else "_work/masks/white_rejects.txt"


def embedded_white_rejects(records: list[Record]) -> set[str]:
    """The embedded ``WHITE_REJECTS`` names, each checked to be a white image of the index."""
    known = {r.filename for r in records if r.domain == "white"}
    names = set(WHITE_REJECTS["rejects"])
    unknown = sorted(names - known)
    if unknown:
        raise DatasetError(f"WHITE_REJECTS (annotations/white_rejects.json) names images that are not white images of the index: {unknown}")
    return names


def load_white_rejects(data_root, records: list[Record] | None = None) -> set[str]:
    """The rejected white pseudo-masks. On the full expected dataset: the embedded ``WHITE_REJECTS``. On any other tree
    (tests, synthetic data): the filenames in ``_work/masks/white_rejects.txt`` (one per line; blank lines and ``#``
    comments are ignored; no file, no rejects). With ``records`` every name must be a white image of the index,
    otherwise DatasetError names it. Without ``records`` the index is read when it exists."""
    if records is None and index_path(data_root).is_file():
        records = load_index(data_root)
    if records is not None and class_domain_counts(records) == EXPECTED_COUNTS:
        return embedded_white_rejects(records)
    path = white_rejects_path(data_root)
    if not path.is_file():
        return set()
    known = {r.filename for r in records if r.domain == "white"} if records is not None else None
    rejects: set[str] = set()
    for number, line in enumerate(read_file_bytes(path).decode("utf-8").splitlines(), start=1):
        name = line.split("#", 1)[0].strip()
        if not name:
            continue
        if known is not None and name not in known:
            raise DatasetError(f"{path}, line {number}: {name!r} is not a white-background image of the dataset")
        rejects.add(name)
    return rejects

QC_COLUMNS, QC_ROWS = 8, 6  # 48 tiles per sheet at most
QC_TILE = (264, 560)  # (width, height) of an image tile in pixels, the aspect of the cached images (0.47)
QC_LABEL_HEIGHT = 24
QC_GAP = 4


def mask_area_rows(records: list[Record], areas: dict[str, float], rejects: set[str]) -> list[list]:
    """Per class [class, accepted leaves, mean %, std %, median %, min %, max %] of the mask area, then an 'all' row."""
    rows, pooled = [], []
    for cls in (*CLASS_NAMES, None):
        names = [r.filename for r in records if r.domain == "white" and (cls is None or r.cls == cls)
                 and r.filename not in rejects and r.filename in areas]
        values = 100.0 * np.array([areas[n] for n in names]) if names else np.zeros(0)
        rows.append([cls or "all", len(names), *(float(f(values)) if len(values) else float("nan") for f in
                    (np.mean, lambda v: np.std(v, ddof=1) if len(v) > 1 else float("nan"), np.median, np.min, np.max))])
    return rows


def white_mask_area_markdown(records: list[Record], areas: dict[str, float], rejects: set[str]) -> str:
    rows = mask_area_rows(records, areas, rejects)
    lines = [
        "| Class | Leaves | Mean area (%) | Std (%) | Median (%) | Min (%) | Max (%) |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for name, n, mean, std, median, low, high in rows:
        cells = " | ".join("n/a" if v != v else f"{v:.1f}" for v in (mean, std, median, low, high))
        lines.append(f"| {name if name != 'all' else '**All**'} | {n} | {cells} |")
    note = (
        f"\nFraction of a white-background image covered by the pseudo-mask of the leaf, over the accepted leaves "
        f"(white images {sum(r.domain == 'white' for r in records)}, rejected: {len(rejects)}). "
        f"Std with ddof=1.\n"
    )
    return "\n".join(lines) + "\n" + note


def write_white_mask_area(data_root, records: list[Record], rejects: set[str]) -> Path:
    areas = {name: entry["area"] for name, entry in load_white_mask_manifest(data_root)["files"].items()}
    path = results_dir(data_root) / "white_mask_area.md"
    write_text_atomic(path, white_mask_area_markdown(records, areas, rejects))
    return path


def draw_outline(image: np.ndarray, mask: np.ndarray, *, color=(255, 255, 0), halo: int = 3, line: int = 1) -> np.ndarray:
    """A copy of ``image`` (RGB) with the outline of ``mask`` (uint8 0/255, same size): a ``halo`` px black line under a
    ``line`` px coloured line."""
    out = image.copy()
    contours, _ = cv2.findContours((mask > 0).astype(np.uint8), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    cv2.drawContours(out, contours, -1, (0, 0, 0), halo)
    cv2.drawContours(out, contours, -1, color, line)
    return out


def qc_tile(rgb: np.ndarray, mask: np.ndarray, label: str, right: str, rejected: bool) -> np.ndarray:
    width, height = QC_TILE
    image = cv2.resize(rgb, (width, height), interpolation=cv2.INTER_AREA)
    small = cv2.resize(mask, (width, height), interpolation=cv2.INTER_NEAREST)
    tile = np.full((height + QC_LABEL_HEIGHT, width, 3), 255, np.uint8)
    tile[:height] = draw_outline(image, small)
    if rejected:
        reject = tuple(int(OKABE_ITO["vermilion"][i : i + 2], 16) for i in (1, 3, 5))
        cv2.rectangle(tile, (0, 0), (width - 1, height - 1), reject, 6)
    font, scale = cv2.FONT_HERSHEY_SIMPLEX, 0.5
    cv2.putText(tile, label, (3, height + 17), font, scale, (0, 0, 0), 1, cv2.LINE_AA)
    (text_width, _), _ = cv2.getTextSize(right, font, scale, 1)
    cv2.putText(tile, right, (width - text_width - 3, height + 17), font, scale, (0, 0, 0), 1, cv2.LINE_AA)
    return tile


def qc_sheet_groups(n: int, per_sheet: int = QC_COLUMNS * QC_ROWS) -> list[tuple[int, int]]:
    """(start, stop) of each sheet: the fewest sheets that fit ``per_sheet``, filled as evenly as possible
    (769 images -> 17 sheets: 4 of 46 and 13 of 45)."""
    sheets = max(1, math.ceil(n / per_sheet))
    base, extra = divmod(n, sheets)
    groups, start = [], 0
    for k in range(sheets):
        stop = start + base + (1 if k < extra else 0)
        groups.append((start, stop))
        start = stop
    return groups


def save_mask_qc_sheets(data_root, records: list[Record], rejects: set[str] | None = None) -> list[Path]:
    """`pseudo_mask_qc_<k>.png`, k = 01.., for every white image (see the section text). Old sheets are removed."""
    rejects = rejects if rejects is not None else load_white_rejects(data_root, records)
    white = [r for r in records if r.domain == "white"]
    manifest = load_white_mask_manifest(data_root)["files"]
    out_dir = figures_dir(data_root)
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("pseudo_mask_qc_*.png"):
        old.unlink()
    paths = []
    tile_h = QC_TILE[1] + QC_LABEL_HEIGHT
    for number, (start, stop) in enumerate(qc_sheet_groups(len(white)), start=1):
        sheet = np.full((QC_ROWS * (tile_h + QC_GAP) + QC_GAP, QC_COLUMNS * (QC_TILE[0] + QC_GAP) + QC_GAP, 3), 255, np.uint8)
        for slot, record in enumerate(white[start:stop]):
            area = manifest[record.filename]["area"]
            tile = qc_tile(read_cached_rgb(data_root, record.filename), read_white_mask(data_root, record.filename),
                           record.filename, f"{100 * area:.1f}%", record.filename in rejects)
            row, col = divmod(slot, QC_COLUMNS)
            top, left = QC_GAP + row * (tile_h + QC_GAP), QC_GAP + col * (QC_TILE[0] + QC_GAP)
            sheet[top : top + tile_h, left : left + QC_TILE[0]] = tile
        path = out_dir / f"pseudo_mask_qc_{number:02d}.png"
        ok, buffer = cv2.imencode(".png", cv2.cvtColor(sheet, cv2.COLOR_RGB2BGR))
        if not ok:
            raise DatasetError(f"{path}: PNG encoding failed")
        write_bytes_atomic(path, buffer.tobytes())
        paths.append(path)
    return paths


def prepare_pseudo_masks(data_root, records: list[Record], *, workers: int | None = None, out=print) -> dict:
    """T5.1 part of `prepare`: masks of every white image (idempotent), the area table and the QC sheets."""
    started = time.time()
    if not any(r.domain == "white" for r in records):
        out("  masks       skipped: no white images")
        return {"built": 0}
    stats = build_white_masks(data_root, records, workers=workers, log=out)
    rejects = load_white_rejects(data_root, records)
    area_path = write_white_mask_area(data_root, records, rejects)
    sheets = save_mask_qc_sheets(data_root, records, rejects)
    out(
        f"  masks       {stats.total} white pseudo-masks: built {stats.built}, up to date {stats.reused}; "
        f"{len(rejects)} rejected ({white_rejects_source(records)}); {len(sheets)} QC sheets, {area_path.name} ({time.time() - started:.0f} s)"
    )
    return {"built": stats.built, "reused": stats.reused, "rejects": rejects, "sheets": sheets}

# Recipe v2 (2026-10-13, after the blind realism check of v1: 12 of 20 composites spotted, every guess right). Pixel
# constants are at the 1280 px cache scale. The section text gives the reason for each step.
COMPOSITE_EDGE_ERODE = 4  # step 2: px; the pseudo-mask edge still holds paper-coloured pixels (v1: 2, a light fringe stayed)
COMPOSITE_EDGE_BAND = 3  # step 2: px inside the eroded edge whose colour is replaced by the nearest colour deeper inside
COMPOSITE_PAPER_BAND = 12  # step 2: px from the mask edge in which paper-coloured pixels are cut away
COMPOSITE_PAPER_DELTA_E = 12.0  # step 2: a pixel within this LAB distance of the photo's paper colour is paper
COMPOSITE_CUT_FADE = 0.12  # step 2: taper length of the tip end, as a fraction of the leaf length
COMPOSITE_LEAF_LENGTH = (0.6, 1.0)  # step 3: leaf length as a fraction of the background height
COMPOSITE_BASE_X = (0.2, 0.8)  # step 3: x of the leaf base, as a fraction of the background width
COMPOSITE_BASE_Y = (1.0, 1.12)  # step 3: y of the leaf base: on or below the bottom edge, the leaf grows up into the frame
COMPOSITE_MAX_LEAN = 35.0  # step 3: degrees from vertical; the lean follows the background's leaves within this
COMPOSITE_LEAN_JITTER = 6.0  # step 3: degrees added to the lean that follows the background, uniform in +-this
COMPOSITE_LEAN_MIN_SCORE = 0.35  # step 3: below this alignment score the background gives no direction: a random lean
COMPOSITE_BEND = 0.08  # step 3: sideways shift of the tip as a fraction of the leaf length, uniform in +-this
COMPOSITE_BLUR_SIGMA = (0.0, 4.0)  # step 4: background defocus (px)
COMPOSITE_LEAF_SIGMA = (0.4, 1.4)  # step 4: leaf softening (px), the camera blur a field photo has at that size
COMPOSITE_L_BLEND = (0.7, 1.0)  # step 5: how far the leaf's L moves to the local lightness of the vegetation around it
COMPOSITE_CONTRAST = (0.65, 0.9)  # step 5: factor on the leaf's own lightness detail (white photos show the veins harder)
COMPOSITE_AB_BLEND = (0.4, 0.7)  # step 5: how far the leaf's healthy colour (a, b) and colourfulness move to that vegetation's
COMPOSITE_CHROMA_MATCH_LIMITS = (0.6, 1.25)  # step 5: bounds of the colourfulness factor
COMPOSITE_LIGHT_SIGMA = 0.06  # step 5: scale of "local" lightness, a Gaussian sigma as a fraction of the background height
COMPOSITE_WB_GAIN = 0.03  # step 5: per-channel leaf gain in 1 +- this
COMPOSITE_CHROMA_EPS = 15.0  # step 5: damping of the chroma rescaling that follows a lightness change
COMPOSITE_CHROMA_LIMITS = (0.8, 1.5)  # step 5: the chroma factor stays within these bounds
COMPOSITE_FEATHER_SIGMA = (1.5, 3.0)  # step 6: alpha blur (px)
COMPOSITE_SHADOW_P = 0.3  # step 7
COMPOSITE_SHADOW_OFFSET = (6.0, 16.0)  # step 7: px
COMPOSITE_SHADOW_SIGMA = (4.0, 9.0)  # step 7: px
COMPOSITE_SHADOW_STRENGTH = (0.25, 0.5)  # step 7
COMPOSITE_TRAIN_SCALE = 0.5  # CompositeSource composes at this fraction of the 1280 px cache (the network sees 448x224 anyway)
COMPOSITE_RECIPE_VERSION = 2
COMPOSITE_CONSTANTS = {
    "version": COMPOSITE_RECIPE_VERSION, "masks": MASK_RECIPE, "train_scale": COMPOSITE_TRAIN_SCALE,
    "rejects": hashlib.sha1("\n".join(sorted(WHITE_REJECTS["rejects"])).encode()).hexdigest()[:12],
    "erode": COMPOSITE_EDGE_ERODE, "edge_band": COMPOSITE_EDGE_BAND, "paper": (COMPOSITE_PAPER_BAND, COMPOSITE_PAPER_DELTA_E),
    "cut_fade": COMPOSITE_CUT_FADE, "length": COMPOSITE_LEAF_LENGTH, "base": (COMPOSITE_BASE_X, COMPOSITE_BASE_Y),
    "lean": (COMPOSITE_MAX_LEAN, COMPOSITE_LEAN_JITTER, COMPOSITE_LEAN_MIN_SCORE), "bend": COMPOSITE_BEND,
    "blur": COMPOSITE_BLUR_SIGMA, "leaf_sigma": COMPOSITE_LEAF_SIGMA, "l_blend": COMPOSITE_L_BLEND,
    "contrast": COMPOSITE_CONTRAST, "ab_blend": (COMPOSITE_AB_BLEND, COMPOSITE_CHROMA_MATCH_LIMITS), "light_sigma": COMPOSITE_LIGHT_SIGMA, "wb_gain": COMPOSITE_WB_GAIN,
    "chroma": (COMPOSITE_CHROMA_EPS, COMPOSITE_CHROMA_LIMITS), "feather": COMPOSITE_FEATHER_SIGMA,
    "shadow_p": COMPOSITE_SHADOW_P, "shadow_offset": COMPOSITE_SHADOW_OFFSET, "shadow_sigma": COMPOSITE_SHADOW_SIGMA,
    "shadow_strength": COMPOSITE_SHADOW_STRENGTH,
}
COMPOSITE_RECIPE = hashlib.sha1(json.dumps(COMPOSITE_CONSTANTS, sort_keys=True).encode()).hexdigest()[:12]


@dataclass(frozen=True)
class CompositeParams:
    """Every random choice of one composite (drawn up front, in this order, from one generator)."""

    length_fraction: float
    base: tuple[float, float]  # (x, y) of the leaf base as fractions of the background width and height
    lean_jitter: float  # degrees added to the lean that follows the background
    lean_fallback: float  # degrees from vertical, used when the background gives no direction
    bend: float  # sideways shift of the tip, as a fraction of the leaf length (positive: to the right)
    blur_sigma: float
    leaf_sigma: float
    l_blend: float
    contrast: float
    ab_blend: float
    gains: tuple[float, float, float]
    feather_sigma: float
    shadow: bool
    shadow_angle: float
    shadow_offset: float
    shadow_sigma: float
    shadow_strength: float


def draw_composite_params(rng: np.random.Generator) -> CompositeParams:
    u = rng.uniform
    return CompositeParams(
        length_fraction=float(u(*COMPOSITE_LEAF_LENGTH)),
        base=(float(u(*COMPOSITE_BASE_X)), float(u(*COMPOSITE_BASE_Y))),
        lean_jitter=float(u(-COMPOSITE_LEAN_JITTER, COMPOSITE_LEAN_JITTER)),
        lean_fallback=float(u(-COMPOSITE_MAX_LEAN, COMPOSITE_MAX_LEAN)),
        bend=float(u(-COMPOSITE_BEND, COMPOSITE_BEND)),
        blur_sigma=float(u(*COMPOSITE_BLUR_SIGMA)),
        leaf_sigma=float(u(*COMPOSITE_LEAF_SIGMA)),
        l_blend=float(u(*COMPOSITE_L_BLEND)),
        contrast=float(u(*COMPOSITE_CONTRAST)),
        ab_blend=float(u(*COMPOSITE_AB_BLEND)),
        gains=tuple(float(g) for g in u(1 - COMPOSITE_WB_GAIN, 1 + COMPOSITE_WB_GAIN, size=3)),
        feather_sigma=float(u(*COMPOSITE_FEATHER_SIGMA)),
        shadow=bool(rng.random() < COMPOSITE_SHADOW_P),
        shadow_angle=float(u(0.0, 2 * np.pi)),
        shadow_offset=float(u(*COMPOSITE_SHADOW_OFFSET)),
        shadow_sigma=float(u(*COMPOSITE_SHADOW_SIGMA)),
        shadow_strength=float(u(*COMPOSITE_SHADOW_STRENGTH)),
    )


def to_lab(rgb_float: np.ndarray) -> np.ndarray:
    """float32 RGB in [0, 1] -> LAB (L 0-100, a and b about -128..127)."""
    return cv2.cvtColor(np.ascontiguousarray(rgb_float, np.float32), cv2.COLOR_RGB2LAB)


def paper_colour(leaf_rgb: np.ndarray, leaf_mask: np.ndarray, gap: int) -> np.ndarray | None:
    """Median LAB colour of the paper: the pixels at least ``gap`` px away from the leaf mask (None if there are none)."""
    near = cv2.dilate(leaf_mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * gap + 1, 2 * gap + 1)))
    outside = near == 0
    if outside.sum() < 50:
        return None
    return np.median(to_lab(leaf_rgb[outside].reshape(-1, 1, 3).astype(np.float32) / 255.0).reshape(-1, 3), axis=0)


def cut_paper(rgb: np.ndarray, alpha: np.ndarray, paper_lab: np.ndarray | None, band: float, delta_e: float) -> np.ndarray:
    """``alpha`` without the paper-coloured pixels that lie within ``band`` px of its edge (then its largest component).
    Pale lesions further inside the leaf are never touched; near the edge a lesion is tan or brown, not paper grey."""
    if paper_lab is None or band < 1:
        return alpha
    inside = alpha > 0.5
    distance = cv2.distanceTransform(inside.astype(np.uint8), cv2.DIST_L2, 3)
    lab = to_lab(rgb.astype(np.float32) / 255.0)
    paper = (np.linalg.norm(lab - paper_lab, axis=2) < delta_e) & inside & (distance <= band)
    if not paper.any():
        return alpha
    kept = largest_component(((inside & ~paper) * 255).astype(np.uint8)) > 0
    return alpha * kept


def decontaminate_edge(rgb: np.ndarray, alpha: np.ndarray, band: float) -> np.ndarray:
    """``rgb`` with every leaf pixel within ``band`` px of the alpha edge (and every pixel outside the leaf) recoloured
    with the colour of the nearest pixel deeper inside: edge pixels are a mix of leaf and paper, so feathering them
    would draw a light rim. Unchanged if the leaf is too thin to have an inside."""
    if band < 1:
        return rgb
    distance = cv2.distanceTransform((alpha > 0.5).astype(np.uint8), cv2.DIST_L2, 3)
    core = distance > band
    if core.sum() < 10:
        return rgb
    # nearest core pixel of every pixel: labels number the zero pixels (the core) in raster order
    _, labels = cv2.distanceTransformWithLabels((~core).astype(np.uint8), cv2.DIST_L2, 5, labelType=cv2.DIST_LABEL_PIXEL)
    core_colours = rgb[core]
    out = core_colours[labels - 1]
    out[core] = rgb[core]
    return out


def leaf_axis_angle(alpha: np.ndarray) -> float:
    """Angle in degrees by which `rotate_patch` turns ``alpha``'s long axis upright (principal axis of its pixels)."""
    ys, xs = np.nonzero(alpha > 0.5)
    if len(xs) < 2:
        return 0.0
    cov = np.cov(np.stack([xs, ys]).astype(np.float64))
    values, vectors = np.linalg.eigh(cov)
    vx, vy = vectors[:, int(np.argmax(values))]
    if vy < 0:
        vx, vy = -vx, -vy
    return float(-np.degrees(np.arctan2(vx, vy)))  # 0 for an upright leaf; positive turns a leaf leaning right upright


def crop_to_alpha(rgb: np.ndarray, alpha: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    x, y, w, h = cv2.boundingRect((alpha > 0.02).astype(np.uint8))
    if w == 0 or h == 0:
        raise DatasetError("the leaf mask is empty")
    return np.ascontiguousarray(rgb[y : y + h, x : x + w]), np.ascontiguousarray(alpha[y : y + h, x : x + w])


def end_width(alpha: np.ndarray, top: bool, fraction: float = 0.08) -> float:
    """Mean width (px) of an upright leaf over the first (``top``) or last ``fraction`` of its rows."""
    rows = max(1, round(fraction * alpha.shape[0]))
    part = alpha[:rows] if top else alpha[-rows:]
    return float((part > 0.5).sum(axis=1).mean())


def taper_cut_ends(alpha: np.ndarray, touches: tuple[bool, bool, bool, bool], fade: float) -> np.ndarray:
    """Taper the leaf to a point over ``fade`` px at every side of the patch flagged in ``touches`` (top, bottom, left,
    right), so that a leaf the photo cut off does not end in a straight edge inside the field image. A pixel survives
    where its distance to the outside is at least ``(1 - ramp)`` times the half-width of the leaf in that row (column),
    with ``ramp`` going 1 -> 0 over ``fade`` px toward that side."""
    if fade < 1.0 or not any(touches):
        return alpha
    height, width = alpha.shape
    inside = (alpha > 0.5).astype(np.uint8)
    keep = np.ones((height, width), bool)
    top, bottom, left, right = touches
    for sides, count, along_rows in (((top, bottom), height, True), ((left, right), width, False)):
        if not any(sides):
            continue
        # distance to the leaf's own edge across the taper direction: a zero border on the two other sides, so that a
        # leaf filling the whole patch width (a straight strip) still has an edge to measure from
        pad = (0, 0, 1, 1) if along_rows else (1, 1, 0, 0)
        padded = cv2.copyMakeBorder(inside, *pad, cv2.BORDER_CONSTANT, value=0)
        distance = cv2.distanceTransform(padded, cv2.DIST_L2, 3)[pad[0] : pad[0] + height, pad[2] : pad[2] + width]
        index = np.arange(count, dtype=np.float32)
        ramp = np.ones(count, np.float32)
        if sides[0]:
            ramp = np.minimum(ramp, (index + 0.5) / fade)
        if sides[1]:
            ramp = np.minimum(ramp, (count - index - 0.5) / fade)
        ramp = np.clip(ramp, 0.0, 1.0)
        half_width = distance.max(axis=1 if along_rows else 0)
        threshold = (1.0 - ramp) * half_width
        keep &= distance >= (threshold[:, None] if along_rows else threshold[None, :])
    return alpha * keep


def rotate_patch(rgb: np.ndarray, alpha: np.ndarray, angle: float, point=None):
    """Rotate a leaf patch (uint8 RGB and float alpha) by ``angle`` degrees (counter-clockwise on screen) on a canvas
    that is large enough to hold it. Returns (rgb, alpha), plus the new position of ``point`` (x, y) when one is given."""
    height, width = alpha.shape
    radians = np.deg2rad(abs(angle))
    new_w = int(np.ceil(width * np.cos(radians) + height * np.sin(radians))) + 2
    new_h = int(np.ceil(width * np.sin(radians) + height * np.cos(radians))) + 2
    matrix = cv2.getRotationMatrix2D((width / 2, height / 2), angle, 1.0)
    matrix[0, 2] += new_w / 2 - width / 2
    matrix[1, 2] += new_h / 2 - height / 2
    rotated_rgb = cv2.warpAffine(rgb, matrix, (new_w, new_h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    rotated_alpha = cv2.warpAffine(alpha, matrix, (new_w, new_h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    if point is None:
        return rotated_rgb, rotated_alpha
    moved = matrix @ np.array([point[0], point[1], 1.0])
    return rotated_rgb, rotated_alpha, (float(moved[0]), float(moved[1]))


def bend_patch(rgb: np.ndarray, alpha: np.ndarray, bend: float) -> tuple[np.ndarray, np.ndarray, float]:
    """Bend an upright leaf (base at the bottom row): row ``r`` moves sideways by ``bend * height * t**2``, where ``t``
    goes 0 at the base to 1 at the tip. Returns (rgb, alpha, x of the base centre in the new patch)."""
    height, width = alpha.shape
    shift = bend * height
    pad = int(np.ceil(abs(shift))) + 1
    new_w = width + pad
    left = pad if shift < 0 else 0  # the patch grows on the side the tip moves to
    t = (height - 1 - np.arange(height, dtype=np.float32)) / max(1, height - 1)
    offset = left + shift * t**2  # where column 0 of row r lands
    map_x = np.arange(new_w, dtype=np.float32)[None, :] - offset[:, None]
    map_y = np.repeat(np.arange(height, dtype=np.float32)[:, None], new_w, axis=1)
    bent_rgb = cv2.remap(rgb, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    bent_alpha = cv2.remap(alpha, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    base_cols = np.nonzero(alpha[-1] > 0.5)[0]
    base_x = (float(base_cols.mean()) if len(base_cols) else width / 2) + left
    return bent_rgb, bent_alpha, base_x


def follow_background_lean(bg_rgb: np.ndarray, base: tuple[float, float], length: float, max_lean: float) -> tuple[float, float]:
    """(lean in degrees from vertical, score in [0, 1]) of the straight leaf from ``base`` (px) of ``length`` px that runs
    most nearly along the leaves of the background. A structure tensor gives the dominant edge direction and how
    clear it is (coherence) at a small scale; each candidate lean (steps of 5 degrees) is scored by the coherence-
    weighted squared cosine between its direction and those edge directions at points along it. Positive leans to the
    left (counter-clockwise), like `rotate_patch`."""
    frame_h, frame_w = bg_rgb.shape[:2]
    small_h = 160
    factor = small_h / frame_h
    grey = cv2.cvtColor(cv2.resize(bg_rgb, (max(8, round(frame_w * factor)), small_h), interpolation=cv2.INTER_AREA),
                        cv2.COLOR_RGB2GRAY).astype(np.float32)
    gx, gy = cv2.Sobel(grey, cv2.CV_32F, 1, 0), cv2.Sobel(grey, cv2.CV_32F, 0, 1)
    jxx, jyy, jxy = (cv2.GaussianBlur(v, (0, 0), 3.0) for v in (gx * gx, gy * gy, gx * gy))
    trace = jxx + jyy + 1e-6
    coherence = np.sqrt((jxx - jyy) ** 2 + 4 * jxy**2) / trace
    gradient_angle = 0.5 * np.arctan2(2 * jxy, jxx - jyy)
    edge_x, edge_y = -np.sin(gradient_angle), np.cos(gradient_angle)  # edges run across the gradient
    best = (0.0, -1.0)
    for lean in np.arange(-max_lean, max_lean + 0.1, 5.0):
        dx, dy = -np.sin(np.deg2rad(lean)), -np.cos(np.deg2rad(lean))
        t = np.linspace(0.15, 0.9, 24)
        px, py = (base[0] + t * length * dx) * factor, (base[1] + t * length * dy) * factor
        inside = (px >= 0) & (px < grey.shape[1] - 1) & (py >= 0) & (py < grey.shape[0] - 1)
        tip_x = (base[0] + 0.9 * length * dx) / frame_w
        if inside.sum() < 6 or not 0.03 <= tip_x <= 0.97:
            continue
        xi, yi = px[inside].astype(int), py[inside].astype(int)
        weight = coherence[yi, xi]
        cos2 = (edge_x[yi, xi] * dx + edge_y[yi, xi] * dy) ** 2
        score = float((weight * cos2).sum() / max(weight.sum(), 1e-6) * min(1.0, weight.mean() / 0.3))
        if score > best[1]:
            best = (float(lean), score)
    return best


def local_vegetation_lightness(bg_lab: np.ndarray, bg_rgb: np.ndarray, sigma: float) -> tuple[np.ndarray, np.ndarray]:
    """(local mean L of the vegetation around every pixel, vegetation mask). Vegetation: yellow-green to green hue with
    some saturation (leaves, not soil, water or sky). Where there is too little vegetation nearby, the local mean of
    all pixels is used."""
    hsv = cv2.cvtColor(np.ascontiguousarray(bg_rgb, np.float32), cv2.COLOR_RGB2HSV)
    veg = ((hsv[..., 0] >= 40) & (hsv[..., 0] <= 160) & (hsv[..., 1] > 0.12) & (hsv[..., 2] > 0.12)).astype(np.float32)
    lightness = bg_lab[..., 0]
    weight = cv2.GaussianBlur(veg, (0, 0), sigma)
    veg_mean = cv2.GaussianBlur(lightness * veg, (0, 0), sigma) / np.maximum(weight, 1e-6)
    all_mean = cv2.GaussianBlur(lightness, (0, 0), sigma)
    return np.where(weight > 0.05, veg_mean, all_mean), veg > 0


def composite_arrays(leaf_rgb: np.ndarray, leaf_mask: np.ndarray, bg_rgb: np.ndarray, rng: np.random.Generator,
                     params: CompositeParams | None = None, *, scale: float = 1.0) -> tuple[np.ndarray, np.ndarray]:
    """Steps 2-8 of the section above. ``leaf_rgb`` / ``leaf_mask`` are a white-background image and its pseudo-mask
    (uint8 0/255), ``bg_rgb`` the field image. Returns (composite uint8 RGB, mask uint8 0/255), both of the
    background's size. ``params`` (default: drawn from ``rng``) exists so that tests can fix single choices.

    ``scale`` is the resolution of the three inputs relative to the 1280 px cache (1.0 = cache resolution, 0.5 =
    half): every constant in pixels is multiplied by it, so a half-resolution composite is the same picture at a
    quarter of the cost. `CompositeSource` uses it for training."""
    p = params or draw_composite_params(rng)
    p = replace(p, blur_sigma=p.blur_sigma * scale, leaf_sigma=p.leaf_sigma * scale, feather_sigma=p.feather_sigma * scale,
                shadow_offset=p.shadow_offset * scale, shadow_sigma=p.shadow_sigma * scale)
    frame_h, frame_w = bg_rgb.shape[:2]
    # 2: crop the leaf, cut paper off its edge, recolour the edge from inside, pull the alpha edge inside the leaf
    x, y, w, h = cv2.boundingRect((leaf_mask > 0).astype(np.uint8))
    if w == 0 or h == 0:
        raise DatasetError("the leaf mask is empty")
    paper_lab = paper_colour(leaf_rgb, leaf_mask, max(2, round(COMPOSITE_PAPER_BAND * scale)))
    erode = max(1, round(COMPOSITE_EDGE_ERODE * scale)) if COMPOSITE_EDGE_ERODE else 0
    eroded = cv2.erode(leaf_mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * erode + 1, 2 * erode + 1))) if erode else leaf_mask
    alpha = (eroded[y : y + h, x : x + w] > 0).astype(np.float32)
    rgb = np.ascontiguousarray(leaf_rgb[y : y + h, x : x + w])
    alpha = cut_paper(rgb, alpha, paper_lab, COMPOSITE_PAPER_BAND * scale, COMPOSITE_PAPER_DELTA_E)
    if not (alpha > 0.5).any():
        raise DatasetError("the leaf mask is empty after removing the paper")
    rgb = decontaminate_edge(rgb, alpha, COMPOSITE_EDGE_BAND * scale)
    # 3: upright, base (the wider end) down, tip tapered, scaled, bent, leaned, base on or below the bottom edge
    rgb, alpha = rotate_patch(rgb, alpha, leaf_axis_angle(alpha))
    rgb, alpha = crop_to_alpha(rgb, alpha)
    if end_width(alpha, top=True) > end_width(alpha, top=False):
        rgb, alpha = np.ascontiguousarray(rgb[::-1]), np.ascontiguousarray(alpha[::-1])
    length = p.length_fraction * frame_h
    fit = length / alpha.shape[0]
    new_w, new_h = max(1, round(alpha.shape[1] * fit)), max(2, round(length))
    interpolation = cv2.INTER_AREA if fit < 1.0 else cv2.INTER_LINEAR
    rgb = cv2.resize(rgb, (new_w, new_h), interpolation=interpolation)
    alpha = cv2.resize(alpha, (new_w, new_h), interpolation=interpolation)
    alpha = taper_cut_ends(alpha, (True, False, False, False), COMPOSITE_CUT_FADE * new_h)
    rgb, alpha, base_x = bend_patch(rgb, alpha, p.bend)
    base = (p.base[0] * frame_w, p.base[1] * frame_h)
    lean, score = follow_background_lean(bg_rgb, base, length, COMPOSITE_MAX_LEAN)
    lean = float(np.clip(lean + p.lean_jitter if score >= COMPOSITE_LEAN_MIN_SCORE else p.lean_fallback, -COMPOSITE_MAX_LEAN, COMPOSITE_MAX_LEAN))
    rgb, alpha, (bx, by) = rotate_patch(rgb, alpha, lean, point=(base_x, alpha.shape[0] - 0.5))
    patch_h, patch_w = alpha.shape
    x0, y0 = round(base[0] - bx), round(base[1] - by)
    # 4: defocused background (the whole frame); the leaf gets the softness of a field photo
    bg = cv2.GaussianBlur(bg_rgb, (0, 0), p.blur_sigma) if p.blur_sigma > 0.1 else bg_rgb
    if p.leaf_sigma > 0.1:
        rgb = cv2.GaussianBlur(rgb, (0, 0), p.leaf_sigma)
    # the region that can change: the patch plus room for the feather and the shadow
    margin = int(np.ceil(3 * max(p.feather_sigma, p.shadow_sigma if p.shadow else 0) + (p.shadow_offset if p.shadow else 0))) + 1
    rx0, ry0 = max(0, x0 - margin), max(0, y0 - margin)
    rx1, ry1 = min(frame_w, x0 + patch_w + margin), min(frame_h, y0 + patch_h + margin)
    if rx1 <= rx0 or ry1 <= ry0:
        raise DatasetError("the leaf was placed outside the frame")
    roi_h, roi_w = ry1 - ry0, rx1 - rx0
    alpha_roi = np.zeros((roi_h, roi_w), np.float32)
    leaf_roi = np.zeros((roi_h, roi_w, 3), np.uint8)
    px0, py0 = max(rx0, x0), max(ry0, y0)  # overlap of the patch with the region, in frame coordinates
    px1, py1 = min(rx1, x0 + patch_w), min(ry1, y0 + patch_h)
    if px1 <= px0 or py1 <= py0:
        raise DatasetError("the leaf was placed outside the frame")
    alpha_roi[py0 - ry0 : py1 - ry0, px0 - rx0 : px1 - rx0] = alpha[py0 - y0 : py1 - y0, px0 - x0 : px1 - x0]
    leaf_roi[py0 - ry0 : py1 - ry0, px0 - rx0 : px1 - rx0] = rgb[py0 - y0 : py1 - y0, px0 - x0 : px1 - x0]
    # 6: feather
    alpha_roi = np.clip(cv2.GaussianBlur(alpha_roi, (0, 0), p.feather_sigma), 0.0, 1.0)
    bg_roi = bg[ry0:ry1, rx0:rx1].astype(np.float32) / 255.0
    # 5: harmonise the leaf with the vegetation around it: lightness follows the local light, the healthy colour moves
    # toward the vegetation's, then the white-balance gain
    leaf_f = np.clip(leaf_roi.astype(np.float32) / 255.0 * np.asarray(p.gains, np.float32), 0.0, 1.0)
    leaf_lab = to_lab(leaf_f)
    weight = alpha_roi > 0.5
    if weight.any():
        bg_lab = to_lab(bg_roi)
        light, veg = local_vegetation_lightness(bg_lab, bg_roi, max(1.0, COMPOSITE_LIGHT_SIGMA * frame_h))
        leaf_l = float(leaf_lab[..., 0][weight].mean())
        detail = p.contrast * (leaf_lab[..., 0] - leaf_l)
        lightness = np.clip(leaf_l + detail + p.l_blend * (light - leaf_l), 0.0, 100.0)
        # chroma follows lightness (a brighter leaf keeps its saturation instead of turning grey); the hue is unchanged
        chroma_scale = np.clip((lightness + COMPOSITE_CHROMA_EPS) / (leaf_lab[..., 0] + COMPOSITE_CHROMA_EPS), *COMPOSITE_CHROMA_LIMITS)
        leaf_lab[..., 1:] *= chroma_scale[..., None]
        leaf_lab[..., 0] = lightness
        healthy = weight & (leaf_lab[..., 1] < -5.0)  # green leaf tissue; lesions (a > -5) only follow the shift
        background_veg = veg & ~weight
        if healthy.sum() >= 0.25 * weight.sum() and background_veg.sum() >= 50:
            veg_ab = bg_lab[..., 1:][background_veg]
            ratio = np.linalg.norm(veg_ab, axis=1).mean() / max(1e-3, np.linalg.norm(leaf_lab[..., 1:][healthy], axis=1).mean())
            leaf_lab[..., 1:] *= float(np.clip(ratio**p.ab_blend, *COMPOSITE_CHROMA_MATCH_LIMITS))  # colourfulness, lesions too
            shift = p.ab_blend * (veg_ab.mean(axis=0) - leaf_lab[..., 1:][healthy].mean(axis=0))
            leaf_lab[..., 1:] += shift.astype(np.float32)
        leaf_f = np.clip(cv2.cvtColor(leaf_lab, cv2.COLOR_LAB2RGB), 0.0, 1.0)
    # 7: soft shadow under the leaf
    if p.shadow:
        dx, dy = p.shadow_offset * np.cos(p.shadow_angle), p.shadow_offset * np.sin(p.shadow_angle)
        shifted = cv2.warpAffine(alpha_roi, np.float32([[1, 0, dx], [0, 1, dy]]), (roi_w, roi_h), borderValue=0)
        shadow = cv2.GaussianBlur(shifted, (0, 0), p.shadow_sigma) * p.shadow_strength
        bg_roi = bg_roi * (1.0 - shadow * (1.0 - alpha_roi))[..., None]
    # 6 (blend) and 8: composite and mask
    blended = bg_roi * (1.0 - alpha_roi[..., None]) + leaf_f * alpha_roi[..., None]
    out = bg.copy()
    out[ry0:ry1, rx0:rx1] = np.clip(blended * 255.0 + 0.5, 0, 255).astype(np.uint8)
    mask = np.zeros((frame_h, frame_w), np.uint8)
    mask[ry0:ry1, rx0:rx1] = (alpha_roi > 0.5).astype(np.uint8) * 255
    if not mask.any():
        raise DatasetError("the leaf was placed outside the frame")
    return out, mask

class CompositeLeakError(DatasetError):
    """A composite source that is not allowed: a val/test image, a wrong domain or class, or an annotated image."""


def annotation_exclusion_set(records: list[Record]) -> set[str]:
    """The field images that never serve as a background: the 30 annotated images of T6.1 and their near-duplicate
    partners. Empty when the dataset has too few field images to select from (tiny test trees)."""
    try:
        selection = annotation_selection(records)
    except DatasetError:
        return set()
    return annotation_exclusions(selection, globals().get("DUPLICATE_GROUPS", []))


class CompositePool:
    """The images a split may use to build composites (step 1): leaves from the white **train** part (not rejected, with
    a background of their class available) and backgrounds from the field **train** part (same class as the leaf, not
    annotated). Every name is checked against the split, here and again at every sample."""

    def __init__(self, data_root, split_seed: int, records: list[Record] | None = None, rejects=None, exclusions=None,
                 part: str = "train"):
        self.data_root = Path(data_root)
        records = load_index(data_root) if records is None else records
        split = load_split(data_root, split_seed)
        if part not in ("train", "val"):
            raise ValueError(f"part must be 'train' or 'val', got {part!r}")
        self.split_seed, self.part = split_seed, part
        self.train = frozenset(split[part])  # the part the sources come from ("train" for training, "val" for the segmenter's checkpoint selection)
        self.held_out = frozenset(name for other in ("train", "val", "test") if other != part for name in split[other])
        self.rejects = frozenset(load_white_rejects(data_root, records) if rejects is None else rejects)
        self.exclusions = frozenset(annotation_exclusion_set(records) if exclusions is None else exclusions)
        self.white_train = [r for r in records if r.domain == "white" and r.filename in self.train]
        self.backgrounds: dict[int, list[Record]] = {}
        for r in records:
            if r.domain == "field" and r.filename in self.train and r.filename not in self.exclusions:
                self.backgrounds.setdefault(r.cls_idx, []).append(r)
        self.leaves = [r for r in self.white_train if r.filename not in self.rejects and self.backgrounds.get(r.cls_idx)]
        for r in (*self.leaves, *(b for group in self.backgrounds.values() for b in group)):
            self.check_name(r)

    def check_name(self, record: Record) -> None:
        if record.filename in self.held_out or record.filename not in self.train:
            raise CompositeLeakError(f"{record.filename} is not in the {self.part} part of split {self.split_seed}: "
                                     "a composite only uses images of that part (no validation or test image may enter training)")

    def check_pair(self, leaf: Record, background: Record) -> None:
        self.check_name(leaf)
        self.check_name(background)
        if leaf.domain != "white" or background.domain != "field":
            raise CompositeLeakError(f"a composite needs a white leaf on a field background, got {leaf.domain} on {background.domain}")
        if leaf.cls_idx != background.cls_idx:
            raise CompositeLeakError(f"{leaf.filename} ({leaf.cls}) cannot go on {background.filename} ({background.cls}): classes differ")
        if leaf.filename in self.rejects or background.filename in self.exclusions:
            raise CompositeLeakError(f"{leaf.filename} / {background.filename} is rejected or annotated")

    def sample_background(self, leaf: Record, rng: np.random.Generator) -> Record:
        group = self.backgrounds[leaf.cls_idx]
        return group[int(rng.integers(len(group)))]

    def sample(self, rng: np.random.Generator, cls_idx: int | None = None) -> tuple[Record, Record]:
        """A random (leaf, background) pair of one class (any class when ``cls_idx`` is None), checked."""
        pool = self.leaves if cls_idx is None else [r for r in self.leaves if r.cls_idx == cls_idx]
        if not pool:
            raise ExperimentError(f"no white leaves with a field background to build composites from (class {cls_idx})")
        leaf = pool[int(rng.integers(len(pool)))]
        background = self.sample_background(leaf, rng)
        self.check_pair(leaf, background)
        return leaf, background


def load_leaf(data_root, record: Record, scale: float = 1.0) -> tuple[np.ndarray, np.ndarray]:
    """(white-background image, pseudo-mask uint8 0/255) at ``scale`` times the cache resolution."""
    rgb, mask = read_cached_rgb(data_root, record.filename), read_white_mask(data_root, record.filename)
    if scale != 1.0:
        rgb = cv2.resize(rgb, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        mask = ((cv2.resize(mask, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA) > 127) * 255).astype(np.uint8)
    return rgb, mask


def load_background(data_root, record: Record, scale: float = 1.0) -> np.ndarray:
    rgb = read_cached_rgb(data_root, record.filename)
    return rgb if scale == 1.0 else cv2.resize(rgb, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)


def make_composite(leaf_rec: Record, bg_rec: Record, rng: np.random.Generator, *, data_root,
                   scale: float = 1.0) -> tuple[np.ndarray, np.ndarray, int]:
    """T5.2: (composite image, mask, label). ``leaf_rec`` is a white image (its pseudo-mask is read from
    ``_work/masks/white``), ``bg_rec`` a field image of the same class, which is also the label's class index.
    The image has the background's size at ``scale`` x the cache resolution; the mask is uint8 0/255
    (``alpha > 0.5``). All randomness comes from ``rng``. Use ``CompositePool.sample`` to choose the records: it
    guarantees train-only, same-class, non-annotated sources."""
    if leaf_rec.cls_idx != bg_rec.cls_idx:
        raise CompositeLeakError(f"{leaf_rec.filename} ({leaf_rec.cls}) and {bg_rec.filename} ({bg_rec.cls}) differ in class")
    leaf_rgb, leaf_mask = load_leaf(data_root, leaf_rec, scale)
    image, mask = composite_arrays(leaf_rgb, leaf_mask, load_background(data_root, bg_rec, scale), rng, scale=scale)
    return image, mask, bg_rec.cls_idx


class CompositeSource:
    """Method A's extra training samples (T5.3), plugged into `LeafDataset(extra_sources=...)`.

    ``source[i]`` for ``0 <= i < n_per_epoch`` is composite number ``i`` of an epoch; ``load(i, epoch)`` returns
    ``(uint8 RGB, class index, name)`` like the other sources, and the dataset passes it through the same training
    augmentation as a real image. Every epoch is new: the random generator of epoch ``e`` is ``default_rng(seed *
    1000 + e)``; it permutes the accepted white leaves (so each leaf is used about once per epoch when
    ``n_per_epoch`` is the white-train count, a subset when it is smaller), and sample ``i`` draws its background and
    all composite choices from ``default_rng([seed * 1000 + e, i])``. A sample is therefore a function of
    ``(seed, epoch, i)`` only, whatever worker process makes it.

    Composites are made at ``scale`` x the cache resolution (default `COMPOSITE_TRAIN_SCALE`): the network sees
    448x224, so half the cache resolution costs nothing in the picture and a quarter in compute. Decoded sources are
    kept in a per-process cache of at most ``cache_mb`` megabytes (reading three images would otherwise cost more than
    the composition itself)."""

    def __init__(self, data_root, split_seed: int, n_per_epoch: int | None = None, seed: int = 0, *,
                 scale: float = COMPOSITE_TRAIN_SCALE, pool: CompositePool | None = None, cache_mb: float = 900.0):
        self.data_root = Path(data_root)
        self.pool = pool if pool is not None else CompositePool(data_root, split_seed)
        if not self.pool.leaves:
            raise ExperimentError(f"split {split_seed} has no white training leaf with a same-class field background for composites")
        self.split_seed, self.seed, self.scale = split_seed, int(seed), scale
        self.n_per_epoch = len(self.pool.white_train) if n_per_epoch is None else int(n_per_epoch)
        if self.n_per_epoch < 1:
            raise ExperimentError("n_per_epoch must be at least 1")
        self.cache_bytes = int(cache_mb * 1e6)
        self._leaf_cache: dict = {}
        self._bg_cache: dict = {}
        self._cached = 0

    def __len__(self) -> int:
        return self.n_per_epoch

    def __getstate__(self) -> dict:
        state = dict(self.__dict__)
        state.update(_leaf_cache={}, _bg_cache={}, _cached=0)  # workers start with an empty cache
        return state

    def epoch_seed(self, epoch: int) -> int:
        return self.seed * 1000 + int(epoch)

    def pair(self, index: int, epoch: int) -> tuple[Record, Record]:
        """The (leaf, background) of composite ``index`` in ``epoch``; checked against the split."""
        order = np.random.default_rng(self.epoch_seed(epoch)).permutation(len(self.pool.leaves))
        leaf = self.pool.leaves[int(order[index % len(order)])]
        background = self.pool.sample_background(leaf, np.random.default_rng([self.epoch_seed(epoch), index, 1]))
        self.pool.check_pair(leaf, background)
        return leaf, background

    def _remember(self, cache: dict, key: str, value, nbytes: int):
        if self._cached + nbytes <= self.cache_bytes:
            cache[key] = value
            self._cached += nbytes
        return value

    def _leaf(self, record: Record):
        hit = self._leaf_cache.get(record.filename)
        if hit is None:
            rgb, mask = load_leaf(self.data_root, record, self.scale)
            hit = self._remember(self._leaf_cache, record.filename, (rgb, mask), rgb.nbytes + mask.nbytes)
        return hit

    def _background(self, record: Record):
        hit = self._bg_cache.get(record.filename)
        if hit is None:
            rgb = load_background(self.data_root, record, self.scale)
            hit = self._remember(self._bg_cache, record.filename, rgb, rgb.nbytes)
        return hit

    def load_with_mask(self, index: int, epoch: int = 0) -> tuple[np.ndarray, np.ndarray, int, str]:
        """``(uint8 RGB, mask uint8 0/255 of the pasted leaf, class index, name)``; the mask is what the segmenter learns."""
        if not 0 <= index < self.n_per_epoch:
            raise IndexError(index)
        leaf, background = self.pair(index, epoch)
        rng = np.random.default_rng([self.epoch_seed(epoch), index])
        leaf_rgb, leaf_mask = self._leaf(leaf)
        image, mask = composite_arrays(leaf_rgb, leaf_mask, self._background(background), rng, scale=self.scale)
        return image, mask, background.cls_idx, f"composite:{leaf.filename}+{background.filename}"

    def load(self, index: int, epoch: int = 0) -> tuple[np.ndarray, int, str]:
        image, _, label, name = self.load_with_mask(index, epoch)
        return image, label, name

    def __getitem__(self, index: int):
        return self.load(index)

COMPOSITE_FIGURE_SEED = 7
REALISM_SEED = 2  # a new seed for every recipe version, so a reviewer never judges images seen before (v1: 7)
EXAMPLES_PER_CLASS = 2
REALISM_PER_CLASS = 4  # composites per class in the realism check; the same number of real images
REALISM_ROWS, REALISM_COLUMNS = 5, 8


def composite_examples(pool: CompositePool, seed: int = COMPOSITE_FIGURE_SEED, per_class: int = EXAMPLES_PER_CLASS) -> list[dict]:
    """``per_class`` composites of every class: dicts with the two records, the composite and its source images."""
    rng = np.random.default_rng(seed)
    rows = []
    for cls_idx in range(NUM_CLASSES):
        used: set[str] = set()
        for _ in range(per_class):
            for _attempt in range(20):  # two different leaves per class, when the pool has them
                leaf, background = pool.sample(rng, cls_idx)
                if leaf.filename not in used:
                    break
            used.add(leaf.filename)
            image, mask, _ = make_composite(leaf, background, rng, data_root=pool.data_root)
            rows.append({"cls_idx": cls_idx, "leaf": leaf, "background": background, "image": image, "mask": mask})
    return rows


def save_composites_examples(data_root, split_seed: int = 0, path: Path | None = None, pool: CompositePool | None = None) -> Path:
    """`composites_examples.png`: rows = classes, 2 examples per row, each leaf | background | composite."""
    plt = pyplot()
    pool = pool or CompositePool(data_root, split_seed)
    path = path or figures_dir(data_root) / "composites_examples.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    examples = composite_examples(pool)
    headers = ("White leaf", "Field background", "Composite")
    with plt.rc_context({"font.size": 7}):
        fig = plt.figure(figsize=(5.8, 1.78 * NUM_CLASSES + 0.3))
        grid = fig.add_gridspec(NUM_CLASSES, 3 * EXAMPLES_PER_CLASS, left=0.055, right=0.998, top=0.965, bottom=0.014,
                                wspace=0.04, hspace=0.12)
        for n, example in enumerate(examples):
            row, pair = divmod(n, EXAMPLES_PER_CLASS)
            panels = (
                (example["leaf"].filename, read_cached_rgb(data_root, example["leaf"].filename)),
                (example["background"].filename, read_cached_rgb(data_root, example["background"].filename)),
                ("", example["image"]),
            )
            for k, (caption, rgb) in enumerate(panels):
                column = 3 * pair + k
                ax = fig.add_subplot(grid[row, column])
                ax.imshow(thumbnail(rgb, 560))
                ax.set_xticks([])
                ax.set_yticks([])
                for spine in ax.spines.values():
                    spine.set_visible(False)
                if caption:
                    ax.set_xlabel(caption, fontsize=5.5, labelpad=1.5)
                if row == 0:
                    ax.set_title(headers[k], fontsize=6.5, fontweight="bold", pad=2)
                if column == 0:
                    ax.set_ylabel(CLASS_NAMES[row], fontsize=7.5, fontweight="bold", labelpad=3)
        fig.savefig(path, dpi=FIGURE_DPI)
        plt.close(fig)
    return path


def realism_items(pool: CompositePool, seed: int = REALISM_SEED) -> list[dict]:
    """The 40 shuffled items of the realism check: ``REALISM_PER_CLASS`` composites and as many real field training
    images (never a background used by one of the composites) per class, in a random order."""
    rng = np.random.default_rng([seed, 99])
    items: list[dict] = []
    used: set[str] = set()
    for cls_idx in range(NUM_CLASSES):
        for _ in range(REALISM_PER_CLASS):
            leaf, background = pool.sample(rng, cls_idx)
            image, _, _ = make_composite(leaf, background, rng, data_root=pool.data_root)
            used.add(background.filename)
            items.append({"kind": "composite", "cls": CLASS_NAMES[cls_idx], "image": image,
                          "leaf": leaf.filename, "background": background.filename})
    for cls_idx in range(NUM_CLASSES):
        free = [r for r in pool.backgrounds.get(cls_idx, []) if r.filename not in used]
        for k in rng.permutation(len(free))[:REALISM_PER_CLASS]:
            items.append({"kind": "real", "cls": CLASS_NAMES[cls_idx], "image": read_cached_rgb(pool.data_root, free[int(k)].filename),
                          "filename": free[int(k)].filename})
    return [items[int(i)] for i in rng.permutation(len(items))]


def realism_key(items: list[dict], split_seed: int, seed: int) -> dict:
    rows = []
    for position, item in enumerate(items, start=1):
        row, col = divmod(position - 1, REALISM_COLUMNS)
        entry = {"position": position, "row": row + 1, "column": col + 1, "kind": item["kind"], "class": item["cls"]}
        entry.update({k: item[k] for k in ("leaf", "background", "filename") if k in item})
        rows.append(entry)
    return {
        "note": "ANSWER KEY of composites_realism_check.png. Do not open it before you have written down your guesses.",
        "grid": f"{REALISM_ROWS} rows x {REALISM_COLUMNS} columns, position = (row - 1) * {REALISM_COLUMNS} + column",
        "split": split_seed, "seed": seed, "composites": sum(i["kind"] == "composite" for i in items),
        "real": sum(i["kind"] == "real" for i in items), "items": rows,
    }


def save_realism_check(data_root, split_seed: int = 0, path: Path | None = None, key_path: Path | None = None,
                       pool: CompositePool | None = None, seed: int = REALISM_SEED) -> tuple[Path, Path]:
    """`composites_realism_check.png` (40 numbered, unlabelled images) and its answer key as JSON."""
    plt = pyplot()
    pool = pool or CompositePool(data_root, split_seed)
    path = path or figures_dir(data_root) / "composites_realism_check.png"
    key_path = key_path or results_dir(data_root) / "composites_realism_key.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    items = realism_items(pool, seed)
    with plt.rc_context({"font.size": 6}):
        fig = plt.figure(figsize=(6.4, 8.35))
        grid = fig.add_gridspec(REALISM_ROWS, REALISM_COLUMNS, left=0.004, right=0.996, top=0.997, bottom=0.003, wspace=0.03, hspace=0.02)
        for n, item in enumerate(items):
            ax = fig.add_subplot(grid[n // REALISM_COLUMNS, n % REALISM_COLUMNS])
            ax.imshow(thumbnail(item["image"], 560))
            ax.set_xticks([])
            ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_visible(False)
            ax.text(0.05, 0.985, str(n + 1), transform=ax.transAxes, ha="left", va="top", fontsize=7, fontweight="bold",
                    color="white", bbox={"boxstyle": "round,pad=0.18", "fc": "black", "ec": "none", "alpha": 0.75})
        fig.savefig(path, dpi=FIGURE_DPI)
        plt.close(fig)
    write_json(key_path, realism_key(items, split_seed, seed), indent=1)
    return path, key_path


def prepare_composites(data_root, records: list[Record], out=print) -> dict:
    """T5.2 part of `prepare`: the two composite figures from split 0. Skipped when a prerequisite is missing."""
    started = time.time()
    try:
        pool = CompositePool(data_root, SPLIT_SEEDS[0], records)
        masks = load_white_mask_manifest(data_root)["files"]
        if not pool.leaves or any(r.filename not in masks for r in pool.leaves):
            raise DatasetError("pseudo-masks are missing")
    except DatasetError as exc:
        out(f"  composites  skipped: {exc}")
        return {}
    if any(len(pool.backgrounds.get(c, [])) == 0 for c in range(NUM_CLASSES)):
        out("  composites  skipped: a class has no field training image")
        return {}
    examples = save_composites_examples(data_root, SPLIT_SEEDS[0], pool=pool)
    check, key = save_realism_check(data_root, SPLIT_SEEDS[0], pool=pool)
    out(f"  composites  {len(pool.leaves)} usable white leaves ({len(pool.white_train) - len(pool.leaves)} of {len(pool.white_train)} "
        f"train leaves rejected or without a background), {sum(len(v) for v in pool.backgrounds.values())} field backgrounds; "
        f"{examples.name}, {check.name} + key ({time.time() - started:.0f} s)")
    return {"examples": examples, "realism": check, "key": key}

COMPOSITE_N_FACTORS = (0.5, 1.0)  # candidates of the split-0 comparison of n_per_epoch (x the white training count)
COMPOSITE_DEFAULT_FACTOR = 1.0


def composite_factor_tag(factor: float) -> str:
    """0.5 -> '0.5', 1.0 -> '1' (sweep folder names)."""
    return f"{factor:g}"


def composite_sweep_run_name(exp_id: str, factor: float) -> str:
    return f"{exp_id}_n{composite_factor_tag(factor)}"


def composite_fingerprint_extra(config: ExperimentConfig, factor: float | None) -> dict:
    """What a composites experiment adds to its config fingerprint; ``{}`` for every other experiment, so their
    fingerprints are exactly what they were before Method A existed."""
    if not config.use_composites:
        return {}
    return {"composites": {"n_factor": COMPOSITE_DEFAULT_FACTOR if factor is None else float(factor), "recipe": COMPOSITE_RECIPE}}


def build_composite_source(data_root, split_seed: int, seed: int, *, n_factor: float = COMPOSITE_DEFAULT_FACTOR,
                           limit: int | None = None) -> CompositeSource:
    """The `CompositeSource` of one run (see the section text). ``limit`` (--fast) caps the composites per epoch."""
    records = load_index(data_root)
    split = load_split(data_root, split_seed)
    white_train = select_records(records, split["train"], ("white",))
    build_white_masks(data_root, white_train)
    pool = CompositePool(data_root, split_seed, records)
    check_cache_complete(data_root, [*pool.leaves, *(b for group in pool.backgrounds.values() for b in group)])
    n = max(1, round(n_factor * len(white_train)))
    return CompositeSource(data_root, split_seed, min(n, limit) if limit else n, seed, pool=pool)

# ---- from 40_segmentation.ipynb ----
ANNOTATION_SEED = 2026
ANNOTATIONS_PER_CLASS = 6
ANNOTATION_DEV_PER_CLASS = 2
ANNOTATION_FORMAT = 1


def annotations_dir(data_root) -> Path:
    return work_dir(data_root) / "annotations"


def annotation_images_dir(data_root) -> Path:
    return annotations_dir(data_root) / "images"


def selection_path(data_root) -> Path:
    return annotations_dir(data_root) / "selection.json"


def annotation_selection(index: list[Record]) -> list[dict]:
    """The 30 field images to annotate (T6.1): ``ANNOTATIONS_PER_CLASS`` per class, as a list of
    ``{"filename", "cls", "set": "dev" | "eval"}`` in CLASS_NAMES order, then dev before eval, then filename.

    Deterministic: the candidates of a class (field images, sorted by filename) are permuted by one
    ``default_rng(2026)`` stream shared by the classes in CLASS_NAMES order, and ``ANNOTATION_DEV_PER_CLASS`` of the
    chosen images become dev through a second stream, ``default_rng([2026, 1])``."""
    rng = np.random.default_rng(ANNOTATION_SEED)
    dev_rng = np.random.default_rng([ANNOTATION_SEED, 1])
    entries = []
    for cls in CLASS_NAMES:
        candidates = sorted(r.filename for r in index if r.cls == cls and r.domain == "field")
        if len(candidates) < ANNOTATIONS_PER_CLASS:
            raise DatasetError(f"{cls}: {len(candidates)} field images, need {ANNOTATIONS_PER_CLASS} to annotate")
        picked = sorted(candidates[i] for i in rng.permutation(len(candidates))[:ANNOTATIONS_PER_CLASS])
        dev = {picked[i] for i in dev_rng.permutation(ANNOTATIONS_PER_CLASS)[:ANNOTATION_DEV_PER_CLASS]}
        rows = [{"filename": name, "cls": cls, "set": "dev" if name in dev else "eval"} for name in picked]
        entries.extend(sorted(rows, key=lambda row: (row["set"] != "dev", row["filename"])))
    return entries


def annotation_exclusions(selection: list[dict], groups) -> set[str]:
    """Filenames that must never be a composite background: the annotated images and every member of their
    near-duplicate groups (a duplicate would show the annotated scene to the segmenter with the wrong target)."""
    chosen = {row["filename"] for row in selection}
    excluded = set(chosen)
    for group in groups:
        if chosen & set(group):
            excluded.update(group)
    return excluded


def selection_document(data_root, index: list[Record]) -> dict:
    """The content of selection.json: the images with their cached path (relative to the data root) and size."""
    manifest = load_manifest(data_root)
    images = []
    for row in annotation_selection(index):
        entry = dict(row, image=f"{WORK_DIRNAME}/cache/{row['filename']}")
        size = manifest.get(row["filename"], {})
        if "width" in size:
            entry.update(width=size["width"], height=size["height"])
        images.append(entry)
    return {
        "format": ANNOTATION_FORMAT, "seed": ANNOTATION_SEED, "per_class": ANNOTATIONS_PER_CLASS,
        "dev_per_class": ANNOTATION_DEV_PER_CLASS, "images": images,
    }


def load_selection(data_root) -> list[dict]:
    path = selection_path(data_root)
    if not path.is_file():
        raise DatasetError(f"{path} does not exist; run the `prepare` command first")
    return json.loads(read_file_bytes(path).decode("utf-8"))["images"]


def write_annotation_selection(data_root, index: list[Record]) -> Path:
    """Write ``_work/annotations/selection.json`` (one image per line, so that the committed file diffs well)."""
    doc = selection_document(data_root, index)
    header = ",\n".join(f" {json.dumps(key)}: {json.dumps(value)}" for key, value in doc.items() if key != "images")
    images = ",\n".join("  " + json.dumps(entry) for entry in doc["images"])
    path = selection_path(data_root)
    write_text_atomic(path, "{\n" + header + ',\n "images": [\n' + images + "\n ]\n}\n")
    return path


def copy_annotation_images(data_root, selection: list[dict]) -> int:
    """Copy the cached images to ``_work/annotations/images/`` (annotate those, not the originals). Returns how many
    were copied; files that already match (same size) are left alone, so the step is idempotent."""
    target = annotation_images_dir(data_root)
    target.mkdir(parents=True, exist_ok=True)
    copied = 0
    for row in selection:
        source, destination = cache_dir(data_root) / row["filename"], target / row["filename"]
        if not source.is_file():
            raise DatasetError(f"{source} is missing; run `prepare` to build the cache")
        if not destination.is_file() or destination.stat().st_size != source.stat().st_size:
            write_bytes_atomic(destination, read_file_bytes(source))
            copied += 1
    return copied

MAX_POLYGON_VERTICES = 60
ANNOTATION_OUTLINE = OKABE_ITO["yellow"]


def embedded_field_annotations():
    """The embedded ``FIELD_ANNOTATIONS`` constant, or None while annotations/field_salient_leaf.json does not exist."""
    return globals().get("FIELD_ANNOTATIONS")


def polygon_area(polygon) -> float:
    points = np.asarray(polygon, dtype=np.float64)
    x, y = points[:, 0], points[:, 1]
    return float(abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))) / 2.0)


def validate_field_annotations(annotations, selection: list[dict]) -> dict:
    """The annotations, checked against the selection: exactly the selected images, each with a polygon of 3 to
    ``MAX_POLYGON_VERTICES`` vertices inside [0, 1] x [0, 1] and positive area. Raises DatasetError."""
    wanted = [row["filename"] for row in selection]
    missing = sorted(set(wanted) - set(annotations))
    extra = sorted(set(annotations) - set(wanted))
    if missing or extra:
        raise DatasetError(f"annotations do not match the selection: missing {missing or 'none'}, unexpected {extra or 'none'}")
    for name in wanted:
        entry = annotations[name]
        polygon = entry.get("polygon") if isinstance(entry, dict) else None
        if not isinstance(polygon, (list, tuple)) or not 3 <= len(polygon) <= MAX_POLYGON_VERTICES:
            raise DatasetError(f"{name}: expected a polygon of 3 to {MAX_POLYGON_VERTICES} vertices")
        points = np.asarray(polygon, dtype=np.float64)
        if points.ndim != 2 or points.shape[1] != 2 or points.min() < 0.0 or points.max() > 1.0:
            raise DatasetError(f"{name}: polygon vertices must be [x, y] pairs normalised to [0, 1]")
        if polygon_area(points) <= 0.0:
            raise DatasetError(f"{name}: polygon has no area")
        if not isinstance(entry.get("ambiguous"), bool):
            raise DatasetError(f"{name}: 'ambiguous' must be true or false")
    return annotations


def save_annotation_overview(data_root, selection: list[dict], annotations: dict, path: Path | None = None) -> Path:
    """`annotations_overview.png`: the annotated images, a row per class (2 dev, then 4 eval), outlines on top."""
    plt = pyplot()
    path = path or figures_dir(data_root) / "annotations_overview.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = {cls: [r for r in selection if r["cls"] == cls] for cls in CLASS_NAMES}
    columns = max(len(v) for v in rows.values())
    with plt.rc_context({"font.size": 7}):
        fig = plt.figure(figsize=(5.8, 1.78 * len(CLASS_NAMES) + 0.25))
        grid = fig.add_gridspec(len(CLASS_NAMES), columns, left=0.055, right=0.998, top=0.965, bottom=0.014, wspace=0.04, hspace=0.12)
        for r, cls in enumerate(CLASS_NAMES):
            for c in range(columns):
                ax = fig.add_subplot(grid[r, c])
                ax.set_xticks([])
                ax.set_yticks([])
                for spine in ax.spines.values():
                    spine.set_visible(False)
                if c >= len(rows[cls]):
                    continue
                row = rows[cls][c]
                rgb = read_cached_rgb(data_root, row["filename"])
                height, width = rgb.shape[:2]
                # Downsample once, with an area filter, to the pixels the tile occupies at FIGURE_DPI, so that matplotlib
                # draws the photo 1:1 (its own 8-bit resampler is skipped). Colours are never quantised.
                box = ax.get_position()
                tile = (max(1, round(box.width * fig.get_figwidth() * FIGURE_DPI)), max(1, round(box.height * fig.get_figheight() * FIGURE_DPI)))
                ax.imshow(cv2.resize(rgb, tile, interpolation=cv2.INTER_AREA), extent=(0, width, height, 0), interpolation="none")
                entry = annotations.get(row["filename"])
                if entry is not None:
                    points = np.asarray(entry["polygon"], dtype=np.float64) * (width, height)
                    closed = np.vstack([points, points[:1]])
                    ax.plot(closed[:, 0], closed[:, 1], color="black", linewidth=1.5, solid_joinstyle="round")
                    ax.plot(closed[:, 0], closed[:, 1], color=ANNOTATION_OUTLINE, linewidth=0.7, solid_joinstyle="round")
                    if entry.get("ambiguous"):
                        ax.text(0.04, 0.97, "?", transform=ax.transAxes, ha="left", va="top", fontsize=9, fontweight="bold",
                                color="white", bbox={"boxstyle": "round,pad=0.15", "fc": OKABE_ITO["vermilion"], "ec": "none"})
                ax.set_xlim(0, width)
                ax.set_ylim(height, 0)
                ax.set_xlabel(f"{row['filename']}", fontsize=5.5, labelpad=1.5)
                if r == 0:
                    ax.set_title(row["set"], fontsize=7, fontweight="bold", pad=2,
                                 color=OKABE_ITO["blue"] if row["set"] == "dev" else "black")
                if c == 0:
                    ax.set_ylabel(cls, fontsize=7.5, fontweight="bold", labelpad=3)
        fig.savefig(path, dpi=FIGURE_DPI)
        plt.close(fig)
    return path


def prepare_annotations(data_root, records: list[Record], out=print, *, annotations=None) -> dict:
    """T6.1 part of `prepare`: selection.json, the images to annotate, and (once annotated) the checked overview
    figure. Skipped with a message when a class has fewer than 6 field images (tiny test trees).

    ``annotations`` are the polygons to validate and draw. ``None`` means the embedded ``FIELD_ANNOTATIONS``, which
    describe the real selection and are therefore only used when the index is the full expected dataset (the same rule
    as the embedded duplicate groups); tests pass their own for synthetic trees."""
    field_counts = Counter(r.cls for r in records if r.domain == "field")
    if any(field_counts[c] < ANNOTATIONS_PER_CLASS for c in CLASS_NAMES):
        out(f"  annotate    skipped: fewer than {ANNOTATIONS_PER_CLASS} field images in some class")
        return {"selected": 0}
    write_annotation_selection(data_root, records)
    selection = load_selection(data_root)
    copied = copy_annotation_images(data_root, selection)
    dev = sum(row["set"] == "dev" for row in selection)
    out(f"  annotate    {len(selection)} field images selected ({dev} dev, {len(selection) - dev} eval), {copied} copied to {annotation_images_dir(data_root)}")
    figure = None
    full_dataset = class_domain_counts(records) == EXPECTED_COUNTS
    if annotations is None and full_dataset:
        annotations = embedded_field_annotations()
    if annotations is None:
        if full_dataset:
            out("              no FIELD_ANNOTATIONS yet (annotations/field_salient_leaf.json); see docs/instructions/annotation-guide.md")
        else:
            out("              embedded FIELD_ANNOTATIONS not checked: this is not the full dataset")
    else:
        validate_field_annotations(annotations, selection)
        figure = save_annotation_overview(data_root, selection, annotations)
        out(f"              {sum(a['ambiguous'] for a in annotations.values())} ambiguous; overview figure {figure.name}")
    return {"selected": len(selection), "copied": copied, "figure": figure}

SEG_ARCHITECTURES = {
    "lraspp_mobilenet_v3_large": SEGMENTER_WEIGHTS,
    "deeplabv3_mobilenet_v3_large": "DeepLabV3_MobileNet_V3_Large_Weights.COCO_WITH_VOC_LABELS_V1",
}
SEG_INPUT_SIZE = (512, 256)  # (height, width) of the segmenter input
SEG_SAMPLES_PER_EPOCH = 1000
SEG_COMPOSITE_SHARE = 0.5  # share of composites among the training samples of an epoch
SEG_EPOCHS, SEG_BATCH_SIZE, SEG_LR, SEG_WEIGHT_DECAY = 40, 16, 3e-4, 1e-4
SEG_VAL_COMPOSITES = 200  # validation composites for the checkpoint choice
SEG_VAL_SEED = 2027  # fixed seed of the validation composites
SEG_THRESHOLD = 0.5  # sigmoid threshold of the mask
SEG_MIN_AREA = 0.02  # a component must cover at least this fraction of the image
SEG_MARGIN = 0.15  # the crop box is the mask's bounding box plus this fraction of its side on every side
SEG_JITTER = 0.05  # Method B training: scale and shift of the crop box by +-5%
# White training samples are augmented at the resolution the composites are made at (half the cache): the two kinds of
# sample then look alike in sharpness, and the augmentation costs a quarter (the network input is 512x256 anyway).
SEG_WHITE_SCALE = COMPOSITE_TRAIN_SCALE
SEG_CONSTANTS = {
    "input": SEG_INPUT_SIZE, "samples": SEG_SAMPLES_PER_EPOCH, "composite_share": SEG_COMPOSITE_SHARE,
    "val_composites": SEG_VAL_COMPOSITES, "val_seed": SEG_VAL_SEED, "threshold": SEG_THRESHOLD, "white_scale": SEG_WHITE_SCALE,
    "version": 1,
}
SEG_RECIPE = hashlib.sha1(json.dumps(SEG_CONSTANTS, sort_keys=True).encode()).hexdigest()[:12]
BOX_CONSTANTS = {"threshold": SEG_THRESHOLD, "min_area": SEG_MIN_AREA, "margin": SEG_MARGIN, "jitter": SEG_JITTER, "version": 1}
BOX_RECIPE = hashlib.sha1(json.dumps(BOX_CONSTANTS, sort_keys=True).encode()).hexdigest()[:12]
SEG_HISTORY_COLUMNS = ["epoch", "lr", "train_loss", "val_iou_composite", "val_iou_white", "val_score", "best", "seconds"]


def seg_size(size_div: int = 1) -> tuple[int, int]:
    """(height, width) of the segmenter input; ``size_div`` > 1 is for smoke tests only."""
    return max(32, SEG_INPUT_SIZE[0] // size_div), max(16, SEG_INPUT_SIZE[1] // size_div)


def build_segmenter(arch: str = "lraspp_mobilenet_v3_large", *, pretrained: bool = True, data_root=None) -> nn.Module:
    """The leaf segmenter: a torchvision segmentation model whose classifier has ONE output channel (the leaf logit).
    ``pretrained=True`` starts from the COCO_WITH_VOC_LABELS_V1 weights (read from, and downloaded to,
    ``<data_root>/_work/weights``) and replaces the 21-class heads; ``False`` builds the same architecture with random
    weights (tests, predict, which load a checkpoint)."""
    if arch not in SEG_ARCHITECTURES:
        raise ValueError(f"unknown segmenter {arch!r}, expected one of {tuple(SEG_ARCHITECTURES)}")
    if data_root is not None and pretrained:
        set_torch_home(data_root)
    builder = getattr(torchvision.models.segmentation, arch)
    if not pretrained:
        return builder(weights=None, weights_backbone=None, num_classes=1)
    model = builder(weights=torchvision.models.get_weight(SEG_ARCHITECTURES[arch]))
    if arch.startswith("lraspp"):
        head = model.classifier
        head.low_classifier = nn.Conv2d(head.low_classifier.in_channels, 1, 1)
        head.high_classifier = nn.Conv2d(head.high_classifier.in_channels, 1, 1)
    else:
        model.classifier[-1] = nn.Conv2d(model.classifier[-1].in_channels, 1, 1)
        model.aux_classifier = None
    return model


def seg_logits(model: nn.Module, x: torch.Tensor) -> torch.Tensor:
    """Leaf logits [N, H, W] for a normalised batch [N, 3, H, W]."""
    return model(x)["out"][:, 0]


def seg_augment(rgb: np.ndarray, mask: np.ndarray, rng: np.random.Generator, size: tuple[int, int]) -> tuple[np.ndarray, np.ndarray]:
    """The T3.2 training augmentation applied to an image and its mask together: both are stacked into one 4-channel
    array, so crop, flips, rotation and resize act identically; colour jitter acts on the image only. Returns the image
    (uint8 [H, W, 3]) and the mask (uint8 0/1 [H, W]) at ``size``."""
    stacked = np.dstack([rgb, mask])
    stacked = random_rotation(random_flips(random_crop(stacked, rng), rng), rng)
    stacked = resize_exact(np.ascontiguousarray(stacked), *size)
    return color_jitter(np.ascontiguousarray(stacked[..., :3]), rng), (stacked[..., 3] >= 128).astype(np.uint8)


def seg_eval_arrays(rgb: np.ndarray, mask: np.ndarray, size: tuple[int, int]) -> tuple[np.ndarray, np.ndarray]:
    """The evaluation transform: resize only. Returns (uint8 image, uint8 0/1 mask)."""
    return resize_exact(rgb, *size), (resize_exact(mask, *size) >= 128).astype(np.uint8)


class SegmenterDataset:
    """The training samples of one segmenter epoch: ``n_samples`` of them, ``composite_share`` composites (from
    ``composites``, a `CompositeSource`) and the rest white train images with accepted pseudo-masks, in this order
    (indices 0..n_composites-1 are composites). ``dataset[(i, epoch)]`` returns ``(uint8 CHW image, uint8 1HW mask, i)``;
    the white image used for slot ``j`` of an epoch and every random draw are functions of ``(seed, epoch, i)`` only."""

    def __init__(self, data_root, whites: list[Record], composites, *, size, n_samples=SEG_SAMPLES_PER_EPOCH, seed=0,
                 composite_share=SEG_COMPOSITE_SHARE):
        self.data_root, self.whites, self.composites = Path(data_root), list(whites), composites
        self.size, self.seed, self.epoch = tuple(size), _sample_seed(seed), 0
        n_composites = 0 if composites is None else n_samples if not self.whites else round(n_samples * composite_share)
        self.n_composites = n_composites if composites is None else min(n_composites, len(composites))
        self.n_samples = self.n_composites + (n_samples - self.n_composites if self.whites else 0)
        if self.n_samples == 0:
            raise ExperimentError("the segmenter has no training data (no white train image with a mask, no composites)")

    def __len__(self) -> int:
        return self.n_samples

    def __getitem__(self, key):
        index, epoch = key if isinstance(key, tuple) else (key, self.epoch)
        if not 0 <= index < self.n_samples:
            raise IndexError(index)
        if index < self.n_composites:
            rgb, mask, _, _ = self.composites.load_with_mask(index, epoch)
        else:
            order = np.random.default_rng([self.seed, int(epoch), 91]).permutation(len(self.whites))
            record = self.whites[int(order[(index - self.n_composites) % len(order)])]
            rgb, mask = load_leaf(self.data_root, record, SEG_WHITE_SCALE)
        rng = np.random.default_rng([self.seed, int(epoch), int(index)])
        image, target = seg_augment(rgb, mask, rng, self.size)
        return torch.from_numpy(np.ascontiguousarray(image.transpose(2, 0, 1))), torch.from_numpy(target[None]), index


@dataclass
class SegEvalSet:
    """Fixed validation images with their masks, already at network size."""

    images: torch.Tensor  # [N, 3, H, W] uint8
    masks: torch.Tensor  # [N, H, W] bool
    names: list[str]

    def __len__(self) -> int:
        return len(self.names)


def seg_eval_set(items: list[tuple]) -> SegEvalSet:
    """``items`` = [(name, uint8 RGB at network size, uint8 0/1 mask at network size)]."""
    if not items:
        return SegEvalSet(torch.empty(0, 3, 0, 0, dtype=torch.uint8), torch.empty(0, 0, 0, dtype=torch.bool), [])
    images = torch.from_numpy(np.stack([i.transpose(2, 0, 1) for _, i, _ in items]))
    masks = torch.from_numpy(np.stack([m for _, _, m in items]).astype(bool))
    return SegEvalSet(images, masks, [n for n, _, _ in items])


def white_mask_records(data_root, records: list[Record], filenames, rejects=None) -> list[Record]:
    """White images among ``filenames`` (a split part) that have an accepted pseudo-mask (not rejected, see `load_white_rejects`), in split order."""
    rejects = load_white_rejects(data_root, records) if rejects is None else rejects
    return [r for r in select_records(records, filenames, ("white",)) if r.filename not in rejects]


def build_seg_val_sets(data_root, split_seed: int, records: list[Record], size, *, n_composites: int = SEG_VAL_COMPOSITES,
                       limit: int | None = None) -> tuple[SegEvalSet, SegEvalSet]:
    """(validation composites, white validation images) of a split, at network ``size``. The composites put white **val**
    leaves on field **val** backgrounds of the same class (classes in turn, fixed seed `SEG_VAL_SEED`); none exist when the
    split has no such pair. ``limit`` (--fast) caps both sets."""
    split = load_split(data_root, split_seed)
    white = white_mask_records(data_root, records, split["val"])
    build_white_masks(data_root, white)
    if limit:
        white = subsample_records(white, limit)
    white_items = [(r.filename, *seg_eval_arrays(read_cached_rgb(data_root, r.filename), read_white_mask(data_root, r.filename), size)) for r in white]
    pool = CompositePool(data_root, split_seed, records, part="val")
    classes = sorted({r.cls_idx for r in pool.leaves})
    composite_items = []
    rng = np.random.default_rng(SEG_VAL_SEED)
    for i in range((min(n_composites, limit) if limit else n_composites) if classes else 0):
        leaf, background = pool.sample(rng, classes[i % len(classes)])
        image, mask, _ = make_composite(leaf, background, rng, data_root=data_root, scale=COMPOSITE_TRAIN_SCALE)
        composite_items.append((f"composite:{leaf.filename}+{background.filename}", *seg_eval_arrays(image, mask, size)))
    return seg_eval_set(composite_items), seg_eval_set(white_items)

def seg_loss(logits: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    """BCE on the logits plus soft Dice per image (averaged). ``logits`` [N, H, W], ``target`` [N, H, W] in {0, 1}."""
    logits, target = logits.float(), target.float()
    bce = F.binary_cross_entropy_with_logits(logits, target)
    probs = torch.sigmoid(logits)
    inter = (probs * target).sum(dim=(1, 2))
    dice = 1.0 - (2.0 * inter + 1.0) / (probs.sum(dim=(1, 2)) + target.sum(dim=(1, 2)) + 1.0)
    return bce + dice.mean()


def mask_iou(pred: np.ndarray, truth: np.ndarray) -> np.ndarray:
    """Per-image IoU of boolean masks [N, H, W] (1.0 where both are empty)."""
    inter = (pred & truth).sum(axis=(1, 2)).astype(np.float64)
    union = (pred | truth).sum(axis=(1, 2)).astype(np.float64)
    return np.where(union > 0, inter / np.maximum(union, 1.0), 1.0)


@torch.no_grad()
def segment_probabilities(model: nn.Module, images: torch.Tensor, device, *, batch_size: int = 32, amp: bool = False) -> np.ndarray:
    """Leaf probabilities [N, H, W] (float32, numpy) for a uint8 image tensor [N, 3, H, W]."""
    model.eval()
    out = []
    for start in range(0, len(images), batch_size):
        x = normalize_batch(images[start : start + batch_size], device)
        with torch.autocast(device_type="cuda", dtype=torch.float16, enabled=amp):
            logits = seg_logits(model, x)
        out.append(torch.sigmoid(logits.float()).cpu())
    return torch.cat(out).numpy() if out else np.zeros((0, 0, 0), dtype=np.float32)


def seg_val_iou(model: nn.Module, eval_set: SegEvalSet, device, *, amp: bool = False) -> float | None:
    """Mean per-image IoU of the thresholded probabilities on a SegEvalSet (None for an empty set)."""
    if not len(eval_set):
        return None
    pred = segment_probabilities(model, eval_set.images, device, amp=amp) > SEG_THRESHOLD
    return float(mask_iou(pred, eval_set.masks.numpy()).mean())


def seg_score(composite_iou, white_iou) -> float:
    """Checkpoint score: the mean of the validation-composite IoU and the white-val IoU (whichever exist)."""
    values = [v for v in (composite_iou, white_iou) if v is not None]
    return float(np.mean(values)) if values else float("nan")


def train_segmenter(cfg: ExperimentConfig, model: nn.Module, train_ds: SegmenterDataset, val_composites: SegEvalSet,
                    val_white: SegEvalSet, device: str, *, seed: int, num_workers: int = 0, mp_context=None, log=print) -> TrainOutcome:
    """AdamW + cosine (per optimiser step, no warmup), BCE + soft Dice, AMP on CUDA. Returns the epoch with the best
    validation score (`seg_score`); every epoch is evaluated, nothing stops early."""
    started = time.time()
    amp = device == "cuda"
    sampler = EpochSampler(len(train_ds), seed)
    drop_last = len(train_ds) % cfg.batch_size == 1  # a last batch of one sample breaks BatchNorm
    loader = make_loader(train_ds, cfg.batch_size, sampler=sampler, num_workers=num_workers, drop_last=drop_last,
                         pin_memory=device == "cuda", mp_context=mp_context)
    total_steps = cfg.epochs * len(loader)
    optimizer = torch.optim.AdamW(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay)
    scaler = torch.amp.GradScaler("cuda", enabled=amp)
    best_state, best_epoch, best_score, history, step = None, 0, -math.inf, [], 0
    for epoch in range(1, cfg.epochs + 1):
        epoch_started = time.time()
        sampler.set_epoch(epoch - 1)
        train_ds.epoch = epoch - 1
        model.train()
        loss_sum, seen, lr_now = 0.0, 0, cfg.lr
        for images, masks, _ in loader:
            lr_now = lr_at_step(step, base_lr=cfg.lr, warmup_steps=0, total_steps=total_steps)
            for group in optimizer.param_groups:
                group["lr"] = lr_now
            x, y = normalize_batch(images, device), masks[:, 0].to(device)
            with torch.autocast(device_type="cuda", dtype=torch.float16, enabled=amp):
                loss = seg_loss(seg_logits(model, x), y)
            loss_value = loss.item()
            if not math.isfinite(loss_value):
                raise ExperimentError(f"{cfg.exp_id}: the training loss became {loss_value} (diverged)")
            optimizer.zero_grad(set_to_none=True)
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            loss_sum += loss_value * len(y)
            seen += len(y)
            step += 1
        composite_iou, white_iou = seg_val_iou(model, val_composites, device, amp=amp), seg_val_iou(model, val_white, device, amp=amp)
        score = seg_score(composite_iou, white_iou)
        improved = best_state is None or score > best_score
        if improved:
            best_state, best_epoch, best_score = cpu_state_dict(model), epoch, score
        history.append({"epoch": epoch, "lr": lr_now, "train_loss": loss_sum / max(1, seen), "val_iou_composite": composite_iou,
                        "val_iou_white": white_iou, "val_score": score, "best": int(improved), "seconds": time.time() - epoch_started})
        fmt = lambda v: "n/a" if v is None else f"{v:.3f}"  # noqa: E731
        log(f"  epoch {epoch:2d}/{cfg.epochs}  lr {lr_now:.2e}  loss {history[-1]['train_loss']:.3f}  val IoU composites "
            f"{fmt(composite_iou)} white {fmt(white_iou)}  score {score:.3f}{' *' if improved else '  '}  {history[-1]['seconds']:.1f}s")
    return TrainOutcome(best_state, best_epoch, best_score, history, False, time.time() - started)

@dataclass(frozen=True)
class SegPost:
    """The result of post-processing one probability map (all coordinates are fractions of the image)."""

    mask: np.ndarray  # bool [H, W]: the selected component (all False on fallback)
    tight: tuple | None  # (x0, y0, x1, y1) bounding box of the component; None on fallback
    box: tuple  # tight box plus the margin, not clamped; (0, 0, 1, 1) on fallback
    fallback: bool
    area: float  # fraction of the image covered by the selected component (0 on fallback)


def postprocess_probability(prob: np.ndarray, *, threshold: float = SEG_THRESHOLD, min_area: float = SEG_MIN_AREA,
                            margin: float = SEG_MARGIN) -> SegPost:
    """Mask -> crop box (steps 1-4 of the section above, except the aspect step). ``prob`` is [H, W] in [0, 1]."""
    height, width = prob.shape
    count, labels, stats, centroids = cv2.connectedComponentsWithStats((prob > threshold).astype(np.uint8), connectivity=8)
    centre = np.array([(width - 1) / 2.0, (height - 1) / 2.0])
    half_diagonal = float(np.hypot(width - 1, height - 1)) / 2.0 or 1.0
    best, best_score = 0, -1.0
    for i in range(1, count):
        area = stats[i, cv2.CC_STAT_AREA] / float(height * width)
        if area < min_area:
            continue
        centrality = 1.0 - float(np.linalg.norm(centroids[i] - centre)) / half_diagonal
        if area * centrality > best_score:
            best, best_score = i, area * centrality
    if best == 0:
        return SegPost(np.zeros((height, width), bool), None, (0.0, 0.0, 1.0, 1.0), True, 0.0)
    x, y, w, h = (int(stats[best, c]) for c in (cv2.CC_STAT_LEFT, cv2.CC_STAT_TOP, cv2.CC_STAT_WIDTH, cv2.CC_STAT_HEIGHT))
    x0, y0, x1, y1 = x / width, y / height, (x + w) / width, (y + h) / height
    box = (x0 - margin * (x1 - x0), y0 - margin * (y1 - y0), x1 + margin * (x1 - x0), y1 + margin * (y1 - y0))
    return SegPost(labels == best, (x0, y0, x1, y1), box, False, float(stats[best, cv2.CC_STAT_AREA]) / (height * width))


def classifier_aspect(input_mode: str, size_div: int = 1) -> float:
    """Height / width of the classifier input (2.0 for rect, 1.0 for squash and pad)."""
    height, width = input_size(input_mode, size_div)
    return height / width


def fit_box(cx: float, cy: float, bw: float, bh: float, width: int, height: int) -> tuple[int, int, int, int]:
    """Pixel box of size (bw, bh) around (cx, cy): clamped to the image size, shifted inside the image, rounded outward to
    whole pixels (at least 1 x 1)."""
    bw, bh = min(bw, float(width)), min(bh, float(height))
    x0 = min(max(cx - bw / 2.0, 0.0), width - bw)
    y0 = min(max(cy - bh / 2.0, 0.0), height - bh)
    ix0, iy0 = int(math.floor(x0 + 1e-6)), int(math.floor(y0 + 1e-6))
    ix1, iy1 = min(width, max(ix0 + 1, int(math.ceil(x0 + bw - 1e-6)))), min(height, max(iy0 + 1, int(math.ceil(y0 + bh - 1e-6))))
    return ix0, iy0, ix1, iy1


def crop_box_pixels(box, aspect: float, width: int, height: int) -> tuple[int, int, int, int]:
    """The crop of an image of ``width`` x ``height`` for a stored (fractional, margin) ``box``: grown along its relatively
    short side to height / width = ``aspect``, then shifted inside the image and clamped (see the section text)."""
    x0, y0, x1, y1 = box[0] * width, box[1] * height, box[2] * width, box[3] * height
    bw, bh = max(x1 - x0, 1.0), max(y1 - y0, 1.0)
    if bh < bw * aspect:
        bh = bw * aspect
    else:
        bw = bh / aspect
    return fit_box((x0 + x1) / 2.0, (y0 + y1) / 2.0, bw, bh, width, height)


def jitter_crop(crop: tuple[int, int, int, int], rng: np.random.Generator, width: int, height: int, amount: float = SEG_JITTER):
    """Method B training augmentation of a pixel crop: scaled by a factor in 1 +- ``amount`` (both sides alike, so the aspect
    is kept) and shifted by up to ``amount`` of its width / height, then fitted into the image again."""
    x0, y0, x1, y1 = crop
    scale, dx, dy = rng.uniform(1 - amount, 1 + amount), rng.uniform(-amount, amount), rng.uniform(-amount, amount)
    bw, bh = x1 - x0, y1 - y0
    return fit_box((x0 + x1) / 2.0 + dx * bw, (y0 + y1) / 2.0 + dy * bh, bw * scale, bh * scale, width, height)


class SegCropHook:
    """`input_hook` of Method B: crop the image to the stored box of its filename (see the section text). ``jitter`` > 0
    makes the hook stochastic: the dataset then passes it a random generator derived from (seed, epoch, index)."""

    def __init__(self, boxes: dict, aspect: float, jitter: float = 0.0):
        self.boxes, self.aspect, self.jitter = boxes, float(aspect), float(jitter)
        self.stochastic = self.jitter > 0

    def __call__(self, rgb: np.ndarray, record, rng: np.random.Generator | None = None) -> np.ndarray:
        if record is None:
            raise ExperimentError("the stored-box crop needs the image's record (use LiveCropHook for ad-hoc images)")
        entry = self.boxes.get(record.filename)
        if entry is None:
            raise ExperimentError(f"boxes.json has no box for {record.filename}; rebuild it with `run --exp S-seg`")
        height, width = rgb.shape[:2]
        crop = (0, 0, width, height) if entry["fallback"] else crop_box_pixels(entry["box"], self.aspect, width, height)
        if self.jitter > 0 and rng is not None:
            crop = jitter_crop(crop, rng, width, height, self.jitter)
        x0, y0, x1, y1 = crop
        return np.ascontiguousarray(rgb[y0:y1, x0:x1])


@torch.no_grad()
def segmenter_posts(model: nn.Module, rgbs: list[np.ndarray], device, size, *, amp: bool = False) -> list[SegPost]:
    """Post-processed segmentation of full-size RGB images (each is resized to the network ``size`` first)."""
    batch = torch.from_numpy(np.stack([resize_exact(rgb, *size).transpose(2, 0, 1) for rgb in rgbs]))
    return [postprocess_probability(p) for p in segment_probabilities(model, batch, device, batch_size=len(rgbs), amp=amp)]


class LiveCropHook:
    """`input_hook` that segments the image it is given and crops to the resulting box (`predict` of Method B). The last
    decision is kept in ``last`` for the printout."""

    stochastic = False

    def __init__(self, model: nn.Module, device, aspect: float, size_div: int = 1):
        self.model, self.device, self.aspect, self.size, self.last = model, device, float(aspect), seg_size(size_div), None

    def __call__(self, rgb: np.ndarray, record=None) -> np.ndarray:
        post = segmenter_posts(self.model, [rgb], self.device, self.size, amp=str(self.device) == "cuda")[0]
        height, width = rgb.shape[:2]
        crop = (0, 0, width, height) if post.fallback else crop_box_pixels(post.box, self.aspect, width, height)
        self.last = {"crop": crop, "fallback": post.fallback, "area": post.area}
        x0, y0, x1, y1 = crop
        return np.ascontiguousarray(rgb[y0:y1, x0:x1])


BOXES_FILENAME = "boxes.json"
SEG_METRICS_FILENAME = "seg_metrics.json"


def seg_runs_root(data_root, seg_dir=None) -> Path:
    """The folder that holds the S-seg split folders: ``_work/runs/S-seg`` unless ``seg_dir`` is given."""
    return Path(seg_dir) if seg_dir is not None else runs_dir(data_root) / "S-seg"


def boxes_path(data_root, split_seed: int, seg_dir=None) -> Path:
    return split_dir(seg_runs_root(data_root, seg_dir), split_seed) / BOXES_FILENAME


def file_sha256(path: Path) -> str:
    return hashlib.sha256(read_file_bytes(path)).hexdigest()


def load_boxes(data_root, split_seed: int, seg_dir=None) -> dict:
    """``{filename: {"tight", "box", "fallback", ...}}`` of the split-``k`` segmenter, or a clear ExperimentError."""
    path = boxes_path(data_root, split_seed, seg_dir)
    if not path.is_file():
        raise ExperimentError(
            f"{path} does not exist: Method B (E4-B) crops by the boxes of the split-{split_seed} segmenter. "
            f"Run `run --exp S-seg --splits {split_seed}` first (it writes boxes.json after training)"
        )
    document = json.loads(read_file_bytes(path).decode("utf-8"))
    return document["images"]


def compute_boxes(model: nn.Module, data_root, records: list[Record], device, size, *, amp: bool = False, batch_size: int = 32) -> tuple[dict, dict]:
    """(boxes, fallback counts per domain) of the segmenter over every record (cached images): the document written to boxes.json."""
    boxes, counts = {}, {domain: {"n": 0, "fallback": 0} for domain in DOMAINS}
    for start in range(0, len(records), batch_size):
        chunk = records[start : start + batch_size]
        posts = segmenter_posts(model, [read_cached_rgb(data_root, r.filename) for r in chunk], device, size, amp=amp)
        for record, post in zip(chunk, posts):
            boxes[record.filename] = {
                "domain": record.domain, "fallback": post.fallback, "area": round(post.area, 5),
                "tight": None if post.tight is None else [round(v, 5) for v in post.tight],
                "box": [round(v, 5) for v in post.box],
            }
            counts[record.domain]["n"] += 1
            counts[record.domain]["fallback"] += int(post.fallback)
    return boxes, counts


def write_boxes(path: Path, split_seed: int, boxes: dict, counts: dict, exp_id: str) -> str:
    """Write boxes.json (one image per line) and return its sha256."""
    header = {"format": 1, "split": split_seed, "exp_id": exp_id, "box_recipe": BOX_RECIPE, "margin": SEG_MARGIN, "min_area": SEG_MIN_AREA,
              "threshold": SEG_THRESHOLD, "fallbacks": counts}
    head = ",\n".join(f" {json.dumps(k)}: {json.dumps(v)}" for k, v in header.items())
    body = ",\n".join(f"  {json.dumps(name)}: {json.dumps(entry)}" for name, entry in sorted(boxes.items()))
    write_text_atomic(path, "{\n" + head + ',\n "images": {\n' + body + "\n }\n}\n")
    return file_sha256(path)


def load_seg_run_model(run_dir, device: str = "cpu") -> tuple[nn.Module, dict]:
    """(segmenter in eval mode on ``device``, checkpoint dict) from <run_dir>/best.pt of an S-seg split folder."""
    path = Path(run_dir) / "best.pt"
    if not path.is_file():
        raise ExperimentError(
            f"{path} does not exist. Method B needs the segmenter checkpoint of its split to segment a new image; checkpoints "
            "are not synced back from Kaggle by default (*.pt is excluded): keep or restore _work/runs/S-seg/split_<k>/best.pt"
        )
    checkpoint = torch.load(fs_path(path), map_location="cpu", weights_only=True)
    model = build_segmenter(checkpoint["arch"], pretrained=False)
    model.load_state_dict(checkpoint["state_dict"])
    return model.to(device).eval(), checkpoint

SEG_EVAL_SETS = ("dev", "eval")
HIT_FRACTION = 0.5  # the crop box must contain at least this share of the annotated leaf area


def annotation_entries(data_root, which: str, annotations=None) -> list[dict]:
    """The annotated images of one set ("dev" or "eval"): ``{"filename", "cls", "set", "ambiguous", "polygon"}`` with the
    polygon as an array of fractional (x, y). ``annotations`` default to the embedded ``FIELD_ANNOTATIONS`` and are checked
    against the committed selection."""
    if which not in SEG_EVAL_SETS:
        raise ExperimentError(f"unknown annotation set {which!r}, expected one of {SEG_EVAL_SETS}")
    annotations = embedded_field_annotations() if annotations is None else annotations
    if annotations is None:
        raise ExperimentError("there are no annotations: annotations/field_salient_leaf.json is not embedded (see docs/instructions/annotation-guide.md)")
    selection = load_selection(data_root)
    validate_field_annotations(annotations, selection)
    return [
        {"filename": row["filename"], "cls": row["cls"], "set": row["set"], "ambiguous": bool(annotations[row["filename"]]["ambiguous"]),
         "polygon": np.asarray(annotations[row["filename"]]["polygon"], dtype=np.float64)}
        for row in selection if row["set"] == which
    ]


def rasterize_polygon(polygon, size: tuple[int, int]) -> np.ndarray:
    """Boolean mask [h, w] of a polygon given as fractional (x, y) vertices."""
    height, width = size
    canvas = np.zeros((height, width), np.uint8)
    cv2.fillPoly(canvas, [np.round(np.asarray(polygon) * (width, height)).astype(np.int32)], 1)
    return canvas.astype(bool)


def iou_dice(pred: np.ndarray, truth: np.ndarray) -> tuple[float, float]:
    inter = float((pred & truth).sum())
    union = float((pred | truth).sum())
    total = float(pred.sum() + truth.sum())
    return (inter / union if union else 1.0), (2 * inter / total if total else 1.0)


def box_fraction(crop_fractions, truth: np.ndarray) -> float:
    """Share of the ``truth`` mask's area that lies inside the box ``(x0, y0, x1, y1)`` (fractions of the image)."""
    height, width = truth.shape
    x0, y0 = int(math.floor(crop_fractions[0] * width + 1e-6)), int(math.floor(crop_fractions[1] * height + 1e-6))
    x1, y1 = int(math.ceil(crop_fractions[2] * width - 1e-6)), int(math.ceil(crop_fractions[3] * height - 1e-6))
    return float(truth[y0:y1, x0:x1].sum()) / max(1.0, float(truth.sum()))


def evaluate_annotations(model: nn.Module, data_root, entries: list[dict], device, size, aspect: float, *, amp: bool = False) -> tuple[list, list]:
    """(per-image results, SegPosts) of a segmenter on annotated images. Each result: filename, class, set, ambiguous, iou,
    dice, hit (crop box contains >= 50% of the leaf), fraction_in_box, fallback, area, crop (fractional box)."""
    rgbs = [read_cached_rgb(data_root, e["filename"]) for e in entries]
    posts = segmenter_posts(model, rgbs, device, size, amp=amp) if rgbs else []
    results = []
    for entry, rgb, post in zip(entries, rgbs, posts):
        height, width = rgb.shape[:2]
        truth = rasterize_polygon(entry["polygon"], post.mask.shape)
        crop = (0, 0, width, height) if post.fallback else crop_box_pixels(post.box, aspect, width, height)
        crop_fractions = (crop[0] / width, crop[1] / height, crop[2] / width, crop[3] / height)
        iou, dice = iou_dice(post.mask, truth)
        inside = box_fraction(crop_fractions, truth)
        results.append({
            "filename": entry["filename"], "cls": entry["cls"], "set": entry["set"], "ambiguous": entry["ambiguous"],
            "iou": iou, "dice": dice, "hit": inside >= HIT_FRACTION, "fraction_in_box": inside, "fallback": post.fallback,
            "area": post.area, "crop": [round(v, 5) for v in crop_fractions],
        })
    return results, posts


def summarize_annotation_results(results: list[dict]) -> dict:
    """Mean IoU, Dice, hit rate and crop-box area (share of the image) over all images and over the non-ambiguous ones,
    and the fallback count."""
    def block(rows):
        if not rows:
            return {"n": 0, "iou": None, "dice": None, "hit_rate": None, "box_area": None}
        return {"n": len(rows), "iou": float(np.mean([r["iou"] for r in rows])), "dice": float(np.mean([r["dice"] for r in rows])),
                "hit_rate": float(np.mean([r["hit"] for r in rows])),
                "box_area": float(np.mean([(r["crop"][2] - r["crop"][0]) * (r["crop"][3] - r["crop"][1]) for r in rows]))}
    return {"all": block(results), "excluding_ambiguous": block([r for r in results if not r["ambiguous"]]),
            "fallbacks": int(sum(r["fallback"] for r in results))}


def example_order(results: list[dict], n: int = 10, failures: int = 2) -> list[int]:
    """Indices of ``n`` results for the examples figure: the ``failures`` lowest-IoU images go last, the others are spread over
    the IoU range (best first). Deterministic."""
    order = sorted(range(len(results)), key=lambda i: (-results[i]["iou"], results[i]["filename"]))
    if len(order) <= n:
        return order
    worst, rest = order[len(order) - failures :], order[: len(order) - failures]
    picked = [rest[int(round(k))] for k in np.linspace(0, len(rest) - 1, n - failures)]
    return picked + worst


def show_photo(ax, fig, rgb: np.ndarray) -> None:
    """Draw a photo 1:1: it is downsampled once, with an area filter, to the pixels the axes occupy at FIGURE_DPI."""
    box = ax.get_position()
    tile = (max(1, round(box.width * fig.get_figwidth() * FIGURE_DPI)), max(1, round(box.height * fig.get_figheight() * FIGURE_DPI)))
    height, width = rgb.shape[:2]
    ax.imshow(cv2.resize(rgb, tile, interpolation=cv2.INTER_AREA), extent=(0, width, height, 0), interpolation="none")


def save_seg_examples(data_root, entries: list[dict], results: list[dict], posts: list[SegPost], path: Path, *, n: int = 10, failures: int = 2) -> Path:
    """`seg_examples.png`: ``n`` annotated field images (``failures`` of them the worst), each with the predicted mask (blue),
    the annotation (yellow outline) and the crop box (vermilion). Needs ``results`` and ``posts`` of the same images."""
    plt = pyplot()
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch

    picks = example_order(results, n, failures)
    columns = 5
    rows = math.ceil(len(picks) / columns)
    path.parent.mkdir(parents=True, exist_ok=True)
    worst = set(picks[-failures:]) if len(results) > n else set()
    with plt.rc_context({"font.size": 6}):
        fig = plt.figure(figsize=(5.8, 2.42 * rows + 0.3))
        grid = fig.add_gridspec(rows, columns, left=0.005, right=0.995, top=0.995, bottom=0.075, wspace=0.05, hspace=0.2)
        for slot, index in enumerate(picks):
            result, post = results[index], posts[index]
            ax = fig.add_subplot(grid[slot // columns, slot % columns])
            ax.set_xticks([])
            ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_visible(False)
            rgb = read_cached_rgb(data_root, result["filename"])
            height, width = rgb.shape[:2]
            show_photo(ax, fig, rgb)
            scale = np.array([width / post.mask.shape[1], height / post.mask.shape[0]])
            overlay = np.zeros((*post.mask.shape, 4), np.float32)
            overlay[post.mask] = (*[int(OKABE_ITO["sky"][i : i + 2], 16) / 255 for i in (1, 3, 5)], 0.5)
            ax.imshow(overlay, extent=(0, width, height, 0), interpolation="nearest")
            contours, _ = cv2.findContours(post.mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            for contour in contours:
                points = (contour[:, 0, :] + 0.5) * scale
                closed = np.vstack([points, points[:1]])
                ax.plot(closed[:, 0], closed[:, 1], color=OKABE_ITO["blue"], linewidth=0.7)
            polygon = entries[index]["polygon"] * (width, height)
            closed = np.vstack([polygon, polygon[:1]])
            ax.plot(closed[:, 0], closed[:, 1], color="black", linewidth=1.5, solid_joinstyle="round")
            ax.plot(closed[:, 0], closed[:, 1], color=OKABE_ITO["yellow"], linewidth=0.7, solid_joinstyle="round")
            if not result["fallback"]:  # a fallback crop is the whole frame: drawing it would only outline the photo
                x0, y0, x1, y1 = result["crop"]
                ax.plot([x0 * width, x1 * width, x1 * width, x0 * width, x0 * width], [y0 * height, y0 * height, y1 * height, y1 * height, y0 * height],
                        color=OKABE_ITO["vermilion"], linewidth=1.0, linestyle=(0, (3, 1.5)))
            ax.set_xlim(0, width)
            ax.set_ylim(height, 0)
            verdict = "fallback" if result["fallback"] else "box hit" if result["hit"] else "box miss"
            ax.set_xlabel(f"{result['filename']}\nIoU {result['iou']:.2f}, {verdict}", fontsize=5.5, labelpad=1.5,
                          color=OKABE_ITO["vermilion"] if index in worst else "black")
        handles = [Patch(fc=OKABE_ITO["sky"], ec=OKABE_ITO["blue"], alpha=0.7, label="predicted mask"),
                   Line2D([0], [0], color=OKABE_ITO["yellow"], lw=1.2, label="annotation"),
                   Line2D([0], [0], color=OKABE_ITO["vermilion"], lw=1.2, linestyle=(0, (3, 1.5)), label="crop box"),
                   Line2D([], [], linestyle="none", label="fallback: no leaf found, whole image used")]
        fig.legend(handles=handles, loc="lower center", ncol=4, frameon=False, fontsize=6, bbox_to_anchor=(0.5, 0.0),
                   handlelength=1.6, columnspacing=1.2)
        fig.savefig(path, dpi=FIGURE_DPI)
        plt.close(fig)
    return path



def read_seg_metrics(run_dir: Path) -> dict:
    path = Path(run_dir) / SEG_METRICS_FILENAME
    return json.loads(read_file_bytes(path).decode("utf-8")) if path.is_file() else {}


def run_seg_eval(data_root, which: str, splits, *, final: bool = False, again: bool = False, seg_dir=None, device: str = "cpu",
                 input_mode: str | None = None, annotations=None, figure: Path | None = None, out=print) -> dict:
    """`seg-eval`: segmenter metrics on the annotated field images of one set (see the section text for the rule).
    ``which="eval"`` needs ``final=True`` and, once measured, ``again=True`` to measure the same segmenter again.
    Returns {split: summary}."""
    data_root = Path(data_root)
    if which not in SEG_EVAL_SETS:
        raise ExperimentError(f"unknown annotation set {which!r}, expected one of {SEG_EVAL_SETS}")
    if which == "eval" and not final:
        raise ExperimentError(
            "the 20 eval annotations are looked at once per final segmenter, for reporting only (06, leakage rule): "
            "do not use them while developing (use --set dev). If this IS the final segmenter, add --final"
        )
    choices = load_choices(data_root)
    mode = input_mode or choices.raw("input_mode")
    if mode is None:
        mode = "rect"
        out("seg-eval: choices.json has no input_mode yet; the hit rate uses the rect crop aspect (448x224)")
    entries = annotation_entries(data_root, which, annotations)
    aspect = classifier_aspect(mode)
    summaries, shown_runs = {}, {}
    for split_seed in splits:
        run_dir = split_dir(seg_runs_root(data_root, seg_dir), split_seed)
        metrics = read_metrics(run_dir)
        if metrics is None:
            raise ExperimentError(f"{run_dir / 'metrics.json'} is missing: train the segmenter first (`run --exp S-seg --splits {split_seed}`)")
        record = read_seg_metrics(run_dir)
        previous = record.get(which)
        if which == "eval" and previous and previous.get("boxes_sha256") == metrics.get("boxes_sha256") and not again:
            raise ExperimentError(
                f"split {split_seed}: the eval annotations were already measured for this segmenter ({run_dir / SEG_METRICS_FILENAME}). "
                "They are looked at once; pass --again only if the segmenter changed or the first run was a mistake"
            )
        model, checkpoint = load_seg_run_model(run_dir, device)
        size = seg_size(checkpoint.get("size_div", 1))
        results, posts = evaluate_annotations(model, data_root, entries, device, size, aspect, amp=device == "cuda")
        summary = summarize_annotation_results(results)
        record[which] = {
            "set": which, "input_mode": mode, "hit_fraction": HIT_FRACTION, "config_fingerprint": metrics.get("config_fingerprint"),
            "boxes_sha256": metrics.get("boxes_sha256"), "best_epoch": metrics.get("best_epoch"), "summary": summary, "images": results,
        }
        write_json(run_dir / SEG_METRICS_FILENAME, record, indent=1)
        summaries[split_seed] = summary
        shown_runs[split_seed] = (run_dir, results, posts)
        a, e = summary["all"], summary["excluding_ambiguous"]
        out(f"seg-eval {which} split {split_seed}: IoU {a['iou']:.3f} Dice {a['dice']:.3f} hit {a['hit_rate']:.2f} (n={a['n']}); "
            f"excluding ambiguous IoU {e['iou']:.3f} Dice {e['dice']:.3f} hit {e['hit_rate']:.2f} (n={e['n']}); "
            f"crop box {100 * a['box_area']:.0f}% of the image; fallbacks {summary['fallbacks']}")
        if which == "dev":
            for r in results:
                out(f"    {r['filename']:<12}{r['cls']:<14} IoU {r['iou']:.3f} Dice {r['dice']:.3f}  box has {100 * r['fraction_in_box']:.0f}% of the leaf"
                    f"{'  FALLBACK' if r['fallback'] else ''}{'  (ambiguous)' if r['ambiguous'] else ''}")
    shown = shown_runs.get(0) if which == "eval" else next(iter(shown_runs.values()), None)
    if shown is not None:
        run_dir, results, posts = shown
        target = figure if figure is not None else figures_dir(data_root) / "seg_examples.png" if which == "eval" else run_dir / "seg_examples_dev.png"
        out(f"seg-eval: figure {save_seg_examples(data_root, entries, results, posts, Path(target))}")
    return summaries


def cmd_seg_eval(args: "argparse.Namespace") -> int:
    try:
        run_seg_eval(Path(args.data_root), args.set, args.splits, final=args.final, again=args.again, seg_dir=args.seg_dir,
                     device=resolve_device(args.device), figure=args.figure)
    except (ExperimentError, DatasetError) as exc:
        print(f"seg-eval: FAIL - {exc}", file=sys.stderr)
        return EXIT_FAILURE
    return EXIT_OK

def seg_fingerprint_extra(cfg: ExperimentConfig, data_root=None) -> dict:
    """What the segmenter row and the Method B row add to their config fingerprint; ``{}`` for every other row, so their
    fingerprints are exactly what they were before phase 06."""
    if cfg.kind == "segmenter":
        rejects = sorted(load_white_rejects(data_root)) if data_root is not None else []
        digest = hashlib.sha1("\n".join(rejects).encode()).hexdigest() if rejects else ""
        return {"segmenter": {"recipe": SEG_RECIPE, "composites": COMPOSITE_RECIPE, "rejects": digest}}
    if cfg.seg_crop:
        return {"seg_crop": {"recipe": BOX_RECIPE}}
    return {}


def run_seg_split(resolved: "ResolvedExperiment", split_seed: int, *, data_root, out_dir: Path, options: "RunOptions", log=print) -> dict:
    """Train the split-``k`` segmenter, pick the best epoch on validation, write the run folder and the boxes of every cached
    image (see the section text). Returns {"status": "skipped" | "done", "metrics": dict, "out_dir": Path}."""
    data_root, out_dir = Path(data_root), Path(out_dir)
    cfg = resolved.config
    split = load_split(data_root, split_seed)
    fingerprint = config_fingerprint(cfg, {"seed_offset": options.seed_offset, "limit": options.limit, **seg_fingerprint_extra(cfg, data_root)})
    state, reason = result_state(out_dir, split["sha256"], fingerprint)
    if state == "fresh" and not options.force:
        log(f"[{resolved.requested} split {split_seed}] skipped: {out_dir / 'metrics.json'} exists and is current (--force to retrain)")
        return {"status": "skipped", "metrics": read_metrics(out_dir), "out_dir": out_dir}
    if state == "stale":
        log(f"[{resolved.requested} split {split_seed}] existing result is stale: {reason}; retraining")
    (out_dir / "metrics.json").unlink(missing_ok=True)  # a half-finished retrain must not look complete

    started = time.time()
    seed = split_seed + options.seed_offset
    records = load_index(data_root)
    rejects = load_white_rejects(data_root, records)
    whites = white_mask_records(data_root, records, split["train"], rejects)
    if options.limit:
        whites = subsample_records(whites, options.limit)
    build_white_masks(data_root, whites)
    size = seg_size(cfg.size_div)
    n_samples = options.limit or SEG_SAMPLES_PER_EPOCH
    pool = CompositePool(data_root, split_seed, records, rejects=rejects)
    n_composites = round(SEG_COMPOSITE_SHARE * n_samples) if pool.leaves else 0
    if n_composites:
        check_cache_complete(data_root, [*pool.leaves, *(b for group in pool.backgrounds.values() for b in group)])
    composites = CompositeSource(data_root, split_seed, n_composites, seed, pool=pool) if n_composites else None
    train_ds = SegmenterDataset(data_root, whites, composites, size=size, n_samples=n_samples, seed=seed)
    val_composites, val_white = build_seg_val_sets(data_root, split_seed, records, size, limit=options.limit)
    workers = default_num_workers() if options.num_workers is None else options.num_workers
    log(f"[{resolved.requested} split {split_seed}] {cfg.exp_id}: {cfg.backbone}  input {size[0]}x{size[1]}  lr {cfg.lr:g}  "
        f"train {len(train_ds)}/epoch ({train_ds.n_composites} composites + {len(train_ds) - train_ds.n_composites} white), "
        f"val {len(val_composites)} composites + {len(val_white)} white  device {options.device}, batch {cfg.batch_size}, workers {usable_workers(workers)}")
    write_json(out_dir / "config.json", {
        "format": RUN_FORMAT, "requested_exp_id": resolved.requested, "experiment": asdict(cfg), "split": split_seed, "seed": seed,
        "seed_offset": options.seed_offset, "limit": options.limit, "overrides": dict(options.overrides),
        "weights": SEG_ARCHITECTURES[cfg.backbone] if cfg.pretrained else None, "input_size": list(size),
        "segmenter": {"constants": {k: list(v) if isinstance(v, tuple) else v for k, v in SEG_CONSTANTS.items()}, "recipe": SEG_RECIPE,
                      "composite_recipe": COMPOSITE_RECIPE, "rejects": len(rejects), "samples_per_epoch": n_samples},
        "config_fingerprint": fingerprint,
    })
    write_json(out_dir / "env.json", environment_record(options.device))

    seed_everything(seed)
    model = build_segmenter(cfg.backbone, pretrained=cfg.pretrained, data_root=options.weights_root).to(options.device)
    outcome = train_segmenter(cfg, model, train_ds, val_composites, val_white, options.device, seed=seed, num_workers=workers,
                              mp_context=options.mp_context, log=log)
    model.load_state_dict(outcome.best_state)
    amp = options.device == "cuda"
    composite_iou, white_iou = seg_val_iou(model, val_composites, options.device, amp=amp), seg_val_iou(model, val_white, options.device, amp=amp)
    boxes, counts = compute_boxes(model, data_root, records, options.device, size, amp=amp)
    for domain, c in counts.items():
        c["rate"] = c["fallback"] / c["n"] if c["n"] else None
    boxes_sha = write_boxes(out_dir / BOXES_FILENAME, split_seed, boxes, counts, cfg.exp_id)
    write_text_atomic(out_dir / "history.csv", csv_text(SEG_HISTORY_COLUMNS, [
        [f"{row[c]:.6g}" if isinstance(row[c], float) else "" if row[c] is None else row[c] for c in SEG_HISTORY_COLUMNS] for row in outcome.history]))
    save_torch_atomic({
        "format": RUN_FORMAT, "state_dict": outcome.best_state, "arch": cfg.backbone, "size_div": cfg.size_div, "exp_id": cfg.exp_id,
        "split": split_seed, "epoch": outcome.best_epoch, "val_score": outcome.best_score, "config": asdict(cfg),
    }, out_dir / "best.pt")
    write_json(out_dir / SEG_METRICS_FILENAME, {
        "format": 1, "split": split_seed, "best_epoch": outcome.best_epoch, "boxes_sha256": boxes_sha,
        "val": {"composite_iou": composite_iou, "white_iou": white_iou, "score": outcome.best_score,
                "n_composites": len(val_composites), "n_white": len(val_white)},
        "fallbacks": counts,
    }, indent=1)
    epoch_seconds = [row["seconds"] for row in outcome.history]
    metrics = {
        "format": RUN_FORMAT, "exp_id": cfg.exp_id, "requested_exp_id": resolved.requested, "kind": "segmenter", "split": split_seed,
        "seed": seed, "split_sha256": split["sha256"], "config_fingerprint": fingerprint,
        "wall_time_s": round(time.time() - started, 2), "train_time_s": round(outcome.seconds, 2),
        "seconds_per_epoch": round(float(np.mean(epoch_seconds)), 3) if epoch_seconds else None,
        "device": options.device, "arch": cfg.backbone, "lr": cfg.lr, "parameters": count_parameters(model),
        "n_train_per_epoch": len(train_ds), "n_composites_per_epoch": train_ds.n_composites, "n_val_composites": len(val_composites),
        "n_val_white": len(val_white), "epochs_run": len(outcome.history), "best_epoch": outcome.best_epoch,
        "best_val_score": outcome.best_score, "val_iou_composite": composite_iou, "val_iou_white": white_iou,
        "fallbacks": counts, "boxes_sha256": boxes_sha, "n_boxes": len(boxes), "fast": options.limit is not None,
        "overrides": dict(options.overrides),
    }
    write_json(out_dir / "metrics.json", metrics, indent=1)  # last: its presence marks the run as complete
    fmt = lambda v: "n/a" if v is None else f"{v:.3f}"  # noqa: E731
    log(f"[{resolved.requested} split {split_seed}] done in {metrics['wall_time_s']:.0f}s  best epoch {outcome.best_epoch}  val IoU composites "
        f"{fmt(composite_iou)} white {fmt(white_iou)}; boxes for {len(boxes)} images, fallbacks white {counts['white']['fallback']}/{counts['white']['n']} "
        f"field {counts['field']['fallback']}/{counts['field']['n']}")
    return {"status": "done", "metrics": metrics, "out_dir": out_dir}

# ---- from 50_analysis.ipynb ----
import re
from typing import NamedTuple

ANALYSIS_SPLITS = (0, 1, 2, 3, 4)  # every reported number is a mean +- std over these five splits
IGNORED_RUN_FOLDERS = ("sweep", "scratch", "retrain")  # under runs/: learning-rate sweeps, dev runs and retrained copies with best.pt (Grad-CAM), never results
SCORE_SUBSETS = ("white", "field", "mixed", "domain_balanced")
SCORE_METRICS = ("macro_f1", "accuracy")
PARTS = ("val", "test")
SUBSET_LABELS = {"white": "White", "field": "Field", "mixed": "Mixed", "domain_balanced": "Domain-balanced"}
METRIC_LABELS = {"macro_f1": "macro-F1", "accuracy": "accuracy (%)"}
# Rows of the required tier that the tables cover (the later phases add their own rows).
ANALYSIS_EXPERIMENTS = (
    "E0-squash", "E0-pad", "E0-rect", "E1-U", "E1-WW", "E1-FF", "E1-WF",
    "E2-cnx-U", "E2-cnx-WF", "E2-swin-U", "E2-swin-WF",
)


@dataclass(frozen=True)
class ExperimentResults:
    """The complete, validated metrics of one experiment over the five splits."""

    exp_id: str  # the requested ID (E1-U for the alias)
    run_name: str  # folder under runs/ (E0-rect for E1-U)
    config: ExperimentConfig  # the registry's resolved config; its fingerprint matched every split
    metrics: dict  # split seed -> metrics.json content

    @property
    def splits(self) -> tuple:
        return tuple(sorted(self.metrics))


def expected_fingerprint(config: ExperimentConfig, composite_factor: float | None = None, data_root=None) -> str:
    """The fingerprint a plain `run` of this config writes (no seed offset, not --fast). Method A rows also carry their
    composites-per-epoch factor and the composite recipe (``composite_fingerprint_extra``), the segmenter and Method B
    rows their recipes (``seg_fingerprint_extra``; the segmenter's needs ``data_root`` for the reject list); other rows
    are unchanged."""
    return config_fingerprint(config, {"seed_offset": 0, "limit": None, **composite_fingerprint_extra(config, composite_factor),
                                       **seg_fingerprint_extra(config, data_root)})


def boxes_problem(data_root, split_seed: int, metrics: dict) -> str | None:
    """Method B runs only: why the split's run does not match the current S-seg boxes.json (None when it does)."""
    path = boxes_path(data_root, split_seed)
    if not path.is_file():
        return f"split {split_seed}: {path} is missing, so the boxes this run cropped by cannot be verified"
    if metrics.get("seg_boxes_sha256") != file_sha256(path):
        return f"split {split_seed}: the S-seg boxes changed since this run (boxes.json sha256 differs; stale run)"
    return None


def load_experiment(data_root, exp_id: str, choices) -> tuple:
    """(ExperimentResults, []) for a complete experiment whose runs match the committed splits and the registry,
    otherwise (None, [reasons]). Never raises for an experiment that is merely not run yet."""
    try:
        resolved = resolve_experiment(exp_id, choices)
        run_name = run_folder_name(exp_id, choices)
    except ExperimentError as exc:
        needed = re.search(r"needed: ([^)]*)\)", str(exc))
        return None, [f"not ready, choices.json has no {needed.group(1)} yet" if needed else f"not ready ({exc})"]
    run_root = runs_dir(data_root) / run_name
    if not run_root.is_dir():
        return None, [f"pending, no runs yet ({run_root} does not exist)"]
    expected = expected_fingerprint(resolved.config, resolved.composite_factor, data_root)
    problems, found = [], {}
    for split_seed in ANALYSIS_SPLITS:
        metrics = read_metrics(split_dir(run_root, split_seed))
        if metrics is None:
            problems.append(f"split {split_seed}: no metrics.json (run incomplete)")
            continue
        try:
            committed_sha = load_split(data_root, split_seed)["sha256"]
        except DatasetError as exc:
            problems.append(f"split {split_seed}: {exc}")
            continue
        if metrics.get("split_sha256") != committed_sha:
            problems.append(f"split {split_seed}: split sha256 differs from the committed split (stale run)")
        elif metrics.get("config_fingerprint") != expected:
            problems.append(f"split {split_seed}: config fingerprint differs from the registry (the experiment definition changed)")
        elif metrics.get("fast") or metrics.get("overrides"):
            problems.append(f"split {split_seed}: this is a --fast / dev-override run, not a result")
        elif resolved.config.seg_crop and boxes_problem(data_root, split_seed, metrics):
            problems.append(boxes_problem(data_root, split_seed, metrics))
        else:
            found[split_seed] = metrics
    if problems:
        return None, problems
    return ExperimentResults(exp_id, run_name, resolved.config, found), []


def load_experiments(data_root, exp_ids, choices) -> dict:
    """{exp_id: ExperimentResults} for the complete experiments. Every other one is skipped with a printed warning."""
    results = {}
    for exp_id in exp_ids:
        found, problems = load_experiment(data_root, exp_id, choices)
        if found is None:
            warn(f"{exp_id}: skipped - " + "; ".join(problems))
        else:
            results[exp_id] = found
    known = set()
    for exp_id in EXPERIMENTS:
        try:
            known.add(run_folder_name(exp_id, choices))
        except ExperimentError:
            known.add(exp_id)
    runs_root = runs_dir(data_root)
    for folder in sorted(runs_root.iterdir()) if runs_root.is_dir() else ():
        if folder.is_dir() and folder.name not in IGNORED_RUN_FOLDERS and folder.name not in known:
            warn(f"{folder}: not a run folder of any registry experiment, ignored")
    return results


def mean_std(values) -> tuple:
    """(mean, sample std with ddof=1). NaN when a value is missing or there are fewer than two values."""
    if len(values) == 0 or any(v is None for v in values):
        return float("nan"), float("nan")
    array = np.asarray(values, dtype=np.float64)
    std = float(np.std(array, ddof=1)) if len(array) > 1 else float("nan")
    return float(np.mean(array)), std


class Aggregate(NamedTuple):
    mean: float
    std: float  # ddof=1 (sample std over the splits)
    values: list  # per-split values, in split order


class PairedDifference(NamedTuple):
    mean: float
    std: float
    values: list  # a - b for each split
    ahead: int  # number of splits in which a is strictly ahead of b


def split_values(exp: ExperimentResults, subset: str, metric: str, part: str) -> list:
    if subset not in SCORE_SUBSETS or metric not in SCORE_METRICS or part not in PARTS:
        raise ValueError(f"unknown subset/metric/part: {subset!r}, {metric!r}, {part!r}")
    return [exp.metrics[k][part][subset][metric] for k in exp.splits]


def aggregate(exp: ExperimentResults, subset: str, metric: str, part: str = "test") -> Aggregate:
    """Mean, std (ddof=1) and per-split list of one metric of one experiment."""
    values = split_values(exp, subset, metric, part)
    mean, std = mean_std(values)
    return Aggregate(mean, std, values)


def paired_difference(a: ExperimentResults, b: ExperimentResults, subset: str, metric: str, part: str = "test") -> PairedDifference:
    """Per-split difference a - b (all experiments share the same five splits), as mean +- std."""
    if a.splits != b.splits:
        raise ValueError(f"{a.exp_id} and {b.exp_id} do not share the same splits: {a.splits} vs {b.splits}")
    diffs = [x - y for x, y in zip(split_values(a, subset, metric, part), split_values(b, subset, metric, part))]
    mean, std = mean_std(diffs)
    return PairedDifference(mean, std, diffs, sum(d > 0 for d in diffs))


def format_mean_std(stat, metric: str, *, signed: bool = False) -> str:
    """'0.912 +- 0.014' for F1 (3 decimals), '91.2 +- 1.4' for accuracy (percent, 1 decimal); signed for differences."""
    if stat.mean != stat.mean or stat.std != stat.std:
        return "n/a"
    scale, decimals = (100.0, 1) if metric == "accuracy" else (1.0, 3)
    sign = "+" if signed else ""
    return f"{stat.mean * scale:{sign}.{decimals}f} +- {stat.std * scale:.{decimals}f}"

@dataclass(frozen=True)
class Table:
    """A results table, written as <name>.csv (for Word) and <name>.md (for review in the repo)."""

    name: str
    title: str
    header: tuple
    rows: list
    note: str = ""

    def to_csv(self) -> str:
        return csv_text(list(self.header), self.rows)

    def to_markdown(self) -> str:
        lines = [f"# {self.title}", ""]
        if self.note:
            lines += [self.note, ""]
        lines.append("| " + " | ".join(self.header) + " |")
        lines.append("|" + "|".join(" --- " for _ in self.header) + "|")
        lines += ["| " + " | ".join(str(cell) for cell in row) + " |" for row in self.rows]
        return "\n".join(lines) + "\n"


def write_table(data_root, table: Table) -> list:
    paths = []
    for suffix, text in ((".csv", table.to_csv()), (".md", table.to_markdown())):
        path = results_dir(data_root) / (table.name + suffix)
        write_text_atomic(path, text)
        paths.append(path)
    return paths


PENDING = "pending"
SCORE_HEADER = tuple(f"{SUBSET_LABELS[s]} {METRIC_LABELS[m]}" for s in SCORE_SUBSETS for m in SCORE_METRICS)


def score_cells(exp, part: str, subsets=SCORE_SUBSETS) -> list:
    """White / field / mixed / domain-balanced, each as macro-F1 and accuracy (mean +- std). '-' for subsets a row
    does not report, 'pending' for an experiment that is not complete yet."""
    if exp is None:
        return [PENDING] * len(SCORE_HEADER)
    return [
        format_mean_std(aggregate(exp, s, m, part), m) if s in subsets else "-"
        for s in SCORE_SUBSETS
        for m in SCORE_METRICS
    ]


def difference_cells(a, b, part: str) -> list:
    if a is None or b is None:
        return [PENDING] * len(SCORE_HEADER)
    return [format_mean_std(paired_difference(a, b, s, m, part), m, signed=True) for s in SCORE_SUBSETS for m in SCORE_METRICS]


def table_input_mode(results: dict) -> Table:
    """E0 (G0 evidence): ResNet50 on white + field at three input sizes, val and test, and the paired
    differences to rect."""
    rows = []
    for part in PARTS:
        for mode in INPUT_MODES:
            height, width = INPUT_SIZES[mode]
            rows.append([part, mode, f"{height}x{width}", *score_cells(results.get(f"E0-{mode}"), part)])
        for mode in INPUT_MODES:
            if mode != "rect":
                rows.append([part, f"{mode} - rect (paired)", "-", *difference_cells(results.get(f"E0-{mode}"), results.get("E0-rect"), part)])
    return Table(
        "table_input_mode",
        "Input mode ablation (E0, ResNet50, white + field training)",
        ("Part", "Input mode", "Input HxW", *SCORE_HEADER),
        rows,
        "Mean +- std over the 5 splits (std with ddof=1; macro-F1 with 3 decimals, accuracy in % with 1 decimal). "
        "Gate G0 used only the val rows. The paired rows are the per-split difference of the first mode minus rect. "
        "Mixed is the full split (about 70% white); domain-balanced is the mean of white and field.",
    )


def table_required(results: dict, choices=None) -> Table:
    """The unified models on the test split (spec scenarios a, b, c plus the domain-balanced mean). The recommended method
    (gate G2) is marked, and added as a row when it is not one of the three plain models."""
    recommended = recommended_experiment(choices) if choices is not None else None
    rows = []
    for exp_id in dict.fromkeys(("E1-U", "E2-cnx-U", "E2-swin-U", *([recommended] if recommended else []))):
        found = results.get(exp_id)
        backbone = found.config.backbone if found is not None else EXPERIMENTS[exp_id].backbone
        rows.append([exp_id + (" (recommended)" if exp_id == recommended else ""), backbone, *score_cells(found, "test")])
    return Table(
        "table_required",
        "Required results: unified models, test split (E1-U, E2-cnx-U, E2-swin-U)",
        ("Experiment", "Backbone", *SCORE_HEADER),
        rows,
        "Mean +- std over the 5 splits (std with ddof=1). White, field and mixed are the three spec scenarios; "
        "domain-balanced is the mean of white and field. The recommended method is the one gate G2 froze. "
        "Rows that are not complete yet read 'pending'.",
    )


DOMAIN_EXPERIMENTS = ("E1-WW", "E1-FF", "E1-WF", "E1-U", "E2-cnx-WF", "E2-swin-WF")
OPTIONAL_DOMAIN_EXPERIMENTS = ("E3-A-WF",)  # Tier 4: a row only once it has run


def table_domains(results: dict, choices) -> Table:
    """Domain-wise and cross-domain experiments on the test split (only the subsets each row is about). E3-A-WF is a
    Method A test number, so like the test rows of table_methods it stays hidden until gate G2 froze the recommendation."""
    recommended = choices.raw("recommended")
    rows = []
    for exp_id in (*DOMAIN_EXPERIMENTS, *(e for e in OPTIONAL_DOMAIN_EXPERIMENTS if e in results)):
        base = EXPERIMENTS[exp_id]
        found = results.get(exp_id)
        backbone = found.config.backbone if found is not None else base.backbone
        train_on = " + ".join(base.train_domains) + (" + composites" if base.use_composites else "")
        subsets = set(base.test_subsets) | ({"domain_balanced"} if "mixed" in base.test_subsets else set())
        cells = score_cells(found, "test", subsets)
        if base.use_composites and recommended is None:
            cells = [HIDDEN_UNTIL_G2 if cell != "-" else cell for cell in cells]
        rows.append([exp_id, backbone, train_on, *cells])
    return Table(
        "table_domains",
        "Domain-wise and cross-domain experiments, test split",
        ("Experiment", "Backbone", "Train on", *SCORE_HEADER),
        rows,
        "W->W is E1-WW, F->F is E1-FF, W->F is E1-WF (field is its main result, white the reference), U is E1-U. "
        "E3-A-WF (when run) trains on white images plus composites: field images are only their backgrounds, so it is not "
        "pure W->F; its test numbers are hidden until gate G2. '-' marks subsets that a row is not about. Mean +- std over "
        "the 5 splits. Rows that are not complete yet read 'pending'.",
    )

GATE_METRIC = "validation mixed macro-F1 (mean over the 5 splits; std with ddof=1)"
TIE_RULE = "The top two are 'within one std' when their gap in mean is at most the larger of their two stds."
G0_RULE = (
    f"G0 (phase 04): choose the input mode with the highest {GATE_METRIC}. If the top two are within one std "
    "of each other, prefer rect (it preserves leaf geometry at no extra cost). " + TIE_RULE
)
G1_RULE = (
    f"G1 (phase 04): choose the backbone with the highest {GATE_METRIC}, among ResNet50 (E1-U), ConvNeXt-T and "
    "Swin-T. If the top two are within one std of each other, prefer the one with the higher mean validation "
    "field macro-F1 (field is the harder, more valuable domain). " + TIE_RULE
)
G1_CANDIDATES = {"resnet50": "E1-U", "convnext_tiny": "E2-cnx-U", "swin_t": "E2-swin-U"}


def rank_candidates(mixed: dict) -> list:
    """Candidate names by decreasing mean (a tie keeps the order of ``mixed``)."""
    return sorted(mixed, key=lambda name: -mixed[name].mean)


def top_two_gap(mixed: dict, ranked: list) -> tuple:
    """(gap between the top two means, tolerance of one std, whether the gap is within it)."""
    first, second = mixed[ranked[0]], mixed[ranked[1]]
    gap = first.mean - second.mean
    tolerance = max(first.std, second.std)
    return gap, tolerance, gap <= tolerance


def decide_g0(mixed: dict) -> dict:
    """Gate G0. ``mixed`` maps input mode -> Aggregate of val mixed macro-F1. Returns the winner and the clause."""
    ranked = rank_candidates(mixed)
    gap, tolerance, tied = top_two_gap(mixed, ranked)
    if tied and ranked[0] != "rect" and "rect" in ranked[:2]:
        value, clause = "rect", "within one std -> rect"
    elif tied and "rect" not in ranked[:2]:
        value, clause = ranked[0], "highest mean (the top two are within one std but rect is not one of them)"
    else:
        value, clause = ranked[0], "highest mean"
    return {"value": value, "decided_by": clause, "ranking": ranked, "top_two_gap": gap, "tolerance": tolerance}


def decide_g1(mixed: dict, field: dict) -> dict:
    """Gate G1. ``mixed`` / ``field`` map backbone -> Aggregate of val mixed / val field macro-F1."""
    ranked = rank_candidates(mixed)
    gap, tolerance, tied = top_two_gap(mixed, ranked)
    if tied:
        value = max(ranked[:2], key=lambda name: (field[name].mean, -ranked.index(name)))
        clause = "within one std -> higher val field macro-F1"
    else:
        value, clause = ranked[0], "highest mean"
    return {"value": value, "decided_by": clause, "ranking": ranked, "top_two_gap": gap, "tolerance": tolerance}


def stat_record(stat) -> dict:
    record = {"mean": float(stat.mean), "std": float(stat.std), "per_split": [float(v) for v in stat.values]}
    if isinstance(stat, PairedDifference):
        record["splits_ahead"] = int(stat.ahead)
    return record


def require_complete(data_root, exp_id: str, choices, gate: str) -> ExperimentResults:
    found, problems = load_experiment(data_root, exp_id, choices)
    if found is None:
        raise ExperimentError(f"gate {gate}: {exp_id} cannot be used - " + "; ".join(problems))
    return found


def candidate_evidence(exps: dict) -> dict:
    out = {}
    for name, exp in exps.items():
        out[name] = {
            "experiment": exp.exp_id, "run_folder": exp.run_name,
            "config_fingerprint": exp.metrics[exp.splits[0]]["config_fingerprint"],
            "split_sha256": [exp.metrics[k]["split_sha256"] for k in exp.splits],
            "val_mixed_macro_f1": stat_record(aggregate(exp, "mixed", "macro_f1", "val")),
            "val_field_macro_f1": stat_record(aggregate(exp, "field", "macro_f1", "val")),
        }
    return out


def paired_evidence(exps: dict, pairs) -> dict:
    return {
        f"{a}_minus_{b}": {
            "val_mixed_macro_f1": stat_record(paired_difference(exps[a], exps[b], "mixed", "macro_f1", "val")),
            "val_field_macro_f1": stat_record(paired_difference(exps[a], exps[b], "field", "macro_f1", "val")),
        }
        for a, b in pairs
    }


def gate_evidence(rule: str, decision: dict, exps: dict, pairs, **extra) -> dict:
    return {
        "rule": rule, "metric": GATE_METRIC, "decided_by": decision["decided_by"], "ranking": decision["ranking"],
        "top_two_gap": float(decision["top_two_gap"]), "tolerance_one_std": float(decision["tolerance"]), **extra,
        "candidates": candidate_evidence(exps), "paired_differences": paired_evidence(exps, pairs),
    }


def evaluate_g0(exps: dict) -> dict:
    """{"value", "evidence"} of gate G0 from the three complete E0 experiments (keyed by input mode)."""
    decision = decide_g0({mode: aggregate(exps[mode], "mixed", "macro_f1", "val") for mode in INPUT_MODES})
    pairs = [(mode, "rect") for mode in INPUT_MODES if mode != "rect"]
    return {"value": decision["value"], "evidence": gate_evidence(G0_RULE, decision, exps, pairs)}


def evaluate_g1(exps: dict, lrs: dict) -> dict:
    """{"value", "evidence"} of gate G1 from the three complete unified experiments (keyed by backbone);
    ``lrs`` maps backbone -> its learning rate from choices.json."""
    mixed = {name: aggregate(exps[name], "mixed", "macro_f1", "val") for name in G1_CANDIDATES}
    field = {name: aggregate(exps[name], "field", "macro_f1", "val") for name in G1_CANDIDATES}
    decision = decide_g1(mixed, field)
    pairs = [("convnext_tiny", "resnet50"), ("swin_t", "resnet50"), ("swin_t", "convnext_tiny")]
    winner = decision["value"]
    lr = {"backbone": winner, "value": lrs[winner], "source": "choices.json lr[backbone], chosen by the split-0 sweep"}
    return {"value": winner, "evidence": gate_evidence(G1_RULE, decision, exps, pairs, lr=lr)}


def describe_gate(gate: str, result: dict) -> str:
    ev = result["evidence"]

    def cell(record: dict) -> str:
        return f"{record['mean']:.3f} +- {record['std']:.3f}"

    lines = [f"gate {gate}: {ev['metric']}", f"  {'candidate':<15}{'val mixed F1':>16}{'val field F1':>16}"]
    for name in ev["ranking"]:
        c = ev["candidates"][name]
        lines.append(f"  {name:<15}{cell(c['val_mixed_macro_f1']):>16}{cell(c['val_field_macro_f1']):>16}")
    first, second = ev["ranking"][:2]
    within = "within" if ev["top_two_gap"] <= ev["tolerance_one_std"] else "outside"
    lines.append(f"  top two: {first} leads {second} by {ev['top_two_gap']:.3f}; one std = {ev['tolerance_one_std']:.3f} ({within} one std)")
    lines.append(f"  decision: {result['value']}  ({ev['decided_by']})")
    return "\n".join(lines)


def run_gate(data_root, gate: str, out=print, *, cut=(), force: bool = False) -> dict:
    """Recompute gate ``g0``, ``g1`` or ``g2`` from the run folders and write its entry to choices.json (other keys
    stay). ``cut`` and ``force`` belong to g2 (see its section below)."""
    data_root = Path(data_root)
    choices = load_choices(data_root)
    if gate != "g2" and (cut or force):
        raise ExperimentError(f"gate {gate}: --cut and --force belong to gate g2")
    if gate == "g2":
        return run_gate_g2(data_root, choices, cut=tuple(cut), force=force, out=out)
    if gate == "g0":
        exps = {mode: require_complete(data_root, f"E0-{mode}", choices, gate) for mode in INPUT_MODES}
        result, key = evaluate_g0(exps), "input_mode"
    elif gate == "g1":
        exps = {name: require_complete(data_root, exp_id, choices, gate) for name, exp_id in G1_CANDIDATES.items()}
        result, key = evaluate_g1(exps, {name: choices.get("lr", name) for name in G1_CANDIDATES}), "backbone"
    else:
        raise ExperimentError(f"unknown gate {gate!r}, expected g0, g1 or g2")
    path = write_choice(data_root, key, result["value"], result["evidence"])
    out(describe_gate(gate, result))
    out(f"  written to {path}: {key} = {result['value']!r}" + (f", lr = {result['evidence']['lr']['value']:g}" if gate == "g1" else ""))
    return result

G2_METHODS = ("plain", "A", "B")  # simplest first: the last tie-break prefers the earlier one
G2_METHOD_EXPERIMENTS = {"A": "E3-A", "B": "E4-B"}
G2_METHOD_LABELS = {"plain": "plain unified model", "A": "Method A (composites)", "B": "Method B (segment, crop)"}
G2_RULE = (
    f"G2 (phase 06): recommend the method with the highest {GATE_METRIC}, among the plain unified model of the G1 "
    "backbone, Method A (E3-A) and Method B (E4-B). If the top two are within one std of each other, prefer the one with "
    "the higher mean validation field macro-F1; if their field means are also within one std, prefer the simpler method "
    "(plain < A < B). " + TIE_RULE
)


def within_one_std(a, b) -> tuple:
    """(|gap| of the two means, tolerance = the larger std, whether the gap is within it)."""
    gap, tolerance = abs(a.mean - b.mean), max(a.std, b.std)
    return gap, tolerance, gap <= tolerance


def decide_g2(mixed: dict, field: dict) -> dict:
    """Gate G2. ``mixed`` / ``field`` map method ("plain", "A", "B"; the ones not cut) -> Aggregate of val mixed / field
    macro-F1. A tie in mean keeps the G2_METHODS order, so the simpler method ranks first."""
    methods = [m for m in G2_METHODS if m in mixed]
    ranked = sorted(methods, key=lambda m: -mixed[m].mean)
    if len(ranked) == 1:
        return {"value": ranked[0], "decided_by": "only candidate (the others were cut)", "ranking": ranked,
                "top_two_gap": None, "tolerance": None, "field_gap": None, "field_tolerance": None}
    gap, tolerance, tied = top_two_gap(mixed, ranked)
    first, second = ranked[:2]
    field_gap = field_tolerance = None
    if not tied:
        value, clause = first, "highest mean"
    else:
        field_gap, field_tolerance, field_tied = within_one_std(field[first], field[second])
        if field_tied:
            value, clause = min((first, second), key=G2_METHODS.index), "within one std on mixed and on field -> simpler method"
        else:
            value, clause = max((first, second), key=lambda m: field[m].mean), "within one std -> higher val field macro-F1"
    return {"value": value, "decided_by": clause, "ranking": ranked, "top_two_gap": gap, "tolerance": tolerance,
            "field_gap": field_gap, "field_tolerance": field_tolerance}


def g2_candidate_experiments(choices, cut=()) -> dict:
    """{method: experiment ID} of the G2 candidates that are not cut. The plain one is the G1 backbone's unified row."""
    unknown = set(cut) - set(G2_METHOD_EXPERIMENTS)
    if unknown:
        raise ExperimentError(f"gate g2: only Method A or B can be cut, not {sorted(unknown)}")
    plain = G1_CANDIDATES[choices.get("backbone")]
    return {"plain": plain, **{m: exp_id for m, exp_id in G2_METHOD_EXPERIMENTS.items() if m not in cut}}


def evaluate_g2(exps: dict, cut=()) -> dict:
    """{"value": recommended experiment ID, "evidence"} from the complete candidates (keyed by method)."""
    mixed = {m: aggregate(exps[m], "mixed", "macro_f1", "val") for m in exps}
    field = {m: aggregate(exps[m], "field", "macro_f1", "val") for m in exps}
    decision = decide_g2(mixed, field)
    method = decision["value"]
    pairs = [(m, "plain") for m in ("A", "B") if m in exps] + ([("B", "A")] if "A" in exps and "B" in exps else [])
    as_float = lambda v: None if v is None else float(v)  # noqa: E731
    evidence = {
        "rule": G2_RULE, "metric": GATE_METRIC, "method": method, "method_label": G2_METHOD_LABELS[method],
        "decided_by": decision["decided_by"], "ranking": decision["ranking"],
        "top_two_gap": as_float(decision["top_two_gap"]), "tolerance_one_std": as_float(decision["tolerance"]),
        "field_gap": as_float(decision["field_gap"]), "field_tolerance_one_std": as_float(decision["field_tolerance"]),
        "cut": sorted(cut), "candidates": candidate_evidence(exps), "paired_differences": paired_evidence(exps, pairs),
    }
    return {"value": exps[method].exp_id, "evidence": evidence}


def describe_g2(result: dict) -> str:
    ev = result["evidence"]

    def cell(record: dict) -> str:
        return f"{record['mean']:.3f} +- {record['std']:.3f}"

    lines = [f"gate g2: {ev['metric']}", f"  {'candidate':<22}{'val mixed F1':>16}{'val field F1':>16}"]
    for method in ev["ranking"]:
        c = ev["candidates"][method]
        lines.append(f"  {method + ' (' + c['experiment'] + ')':<22}{cell(c['val_mixed_macro_f1']):>16}{cell(c['val_field_macro_f1']):>16}")
    for method in ev["cut"]:
        lines.append(f"  {method + ' (' + G2_METHOD_EXPERIMENTS[method] + ')':<22}{'cut':>16}{'cut':>16}")
    if ev["top_two_gap"] is not None:
        first, second = ev["ranking"][:2]
        within = "within" if ev["top_two_gap"] <= ev["tolerance_one_std"] else "outside"
        lines.append(f"  top two: {first} leads {second} by {ev['top_two_gap']:.3f} on mixed; one std = {ev['tolerance_one_std']:.3f} ({within} one std)")
        if ev["field_gap"] is not None:
            within = "within" if ev["field_gap"] <= ev["field_tolerance_one_std"] else "outside"
            lines.append(f"  on field they differ by {ev['field_gap']:.3f}; one std = {ev['field_tolerance_one_std']:.3f} ({within} one std)")
    lines.append(f"  decision: {result['value']} = {ev['method_label']}  ({ev['decided_by']})")
    return "\n".join(lines)


def run_gate_g2(data_root, choices, *, cut=(), force: bool = False, out=print) -> dict:
    """Gate G2 (see the section text): refuses incomplete candidates that are not cut, and a changed outcome once frozen."""
    names = g2_candidate_experiments(choices, cut)
    exps = {method: require_complete(data_root, exp_id, choices, "g2") for method, exp_id in names.items()}
    result = evaluate_g2(exps, cut)
    frozen = choices.raw("recommended")
    if frozen is not None and frozen != result["value"] and not force:
        out(describe_g2(result))
        raise ExperimentError(
            f"choices.json already recommends {frozen!r} (frozen by an earlier `gate g2`), and the runs now decide "
            f"{result['value']!r}. The recommendation is frozen once made (06: flipping it after seeing test numbers is "
            "test-set selection). If the earlier decision was a genuine mistake, rerun with --force and say so in the report"
        )
    path = write_choice(data_root, "recommended", result["value"], result["evidence"])
    out(describe_g2(result))
    out(f"  written to {path}: recommended = {result['value']!r}" + (" (overwrote a different frozen choice: --force)" if frozen not in (None, result["value"]) else ""))
    return result

METHOD_EXPERIMENTS = ("E3-A", "E4-B")
SEGMENTER_EXPERIMENT = "S-seg"
HIDDEN_UNTIL_G2 = "hidden until gate g2"


def plain_method_experiment(choices) -> str | None:
    """The G2 'plain' candidate: the unified row of the G1 backbone (None while gate G1 has not run)."""
    backbone = choices.raw("backbone")
    return G1_CANDIDATES.get(backbone) if backbone else None


def table_methods(results: dict, choices) -> Table:
    """Plain vs Method A vs Method B (G2 evidence on val; test only once the recommendation is frozen)."""
    plain = plain_method_experiment(choices)
    recommended = choices.raw("recommended")
    rows_spec = (("plain", plain), ("A", "E3-A"), ("B", "E4-B"))
    rows = []
    for part in PARTS:
        hidden = part == "test" and recommended is None
        for method, exp_id in rows_spec:
            label = exp_id or "(G1 backbone not chosen)"
            cells = [HIDDEN_UNTIL_G2] * len(SCORE_HEADER) if hidden else score_cells(results.get(exp_id) if exp_id else None, part)
            mark = " (recommended)" if recommended is not None and exp_id == recommended else ""
            rows.append([part, G2_METHOD_LABELS[method] + mark, label, *cells])
        for method, exp_id in rows_spec[1:]:
            cells = ([HIDDEN_UNTIL_G2] * len(SCORE_HEADER) if hidden
                     else difference_cells(results.get(exp_id), results.get(plain) if plain else None, part))
            rows.append([part, f"{method} - plain (paired)", f"{exp_id} - {plain or 'plain'}", *cells])
    return Table(
        "table_methods",
        "Methods: plain unified model vs Method A (composites) vs Method B (segment, crop)",
        ("Part", "Method", "Experiment", *SCORE_HEADER),
        rows,
        "Mean +- std over the 5 splits (std with ddof=1). Plain is the unified model of the G1 backbone; A adds composites "
        "to its training data; B crops every image to the box of its split's leaf segmenter. Gate G2 uses only the val rows. "
        "The paired rows are the per-split difference minus plain. Test rows are shown only after gate G2 froze the "
        "recommendation. Rows that are not complete yet read 'pending'.",
    )


def segmenter_eval_sections(exp: ExperimentResults | None, data_root) -> dict | None:
    """{split: eval section of seg_metrics.json} when every split has one measured on its current boxes, else None."""
    if exp is None:
        return None
    sections = {}
    for split_seed in exp.splits:
        section = read_seg_metrics(split_dir(runs_dir(data_root) / exp.run_name, split_seed)).get("eval")
        if not section or section.get("boxes_sha256") != exp.metrics[split_seed].get("boxes_sha256"):
            return None
        sections[split_seed] = section
    return sections


def annotation_counts(data_root, which: str) -> dict:
    """{"all": n, "excluding_ambiguous": n} of an annotation set (flags only, no measurement); '-' when unavailable."""
    try:
        entries = annotation_entries(data_root, which)
    except (ExperimentError, DatasetError):
        return {"all": "-", "excluding_ambiguous": "-"}
    return {"all": len(entries), "excluding_ambiguous": sum(not e["ambiguous"] for e in entries)}


def format_rate(stat) -> str:
    """'85.0 +- 5.0' (percent, 1 decimal) or 'n/a'."""
    return "n/a" if stat.mean != stat.mean or stat.std != stat.std else f"{100 * stat.mean:.1f} +- {100 * stat.std:.1f}"


def table_segmenter(exp: ExperimentResults | None, data_root) -> Table:
    """The leaf segmenter over its 5 splits (see the section text): eval annotations, fallbacks and the validation IoUs."""
    eval_sections = segmenter_eval_sections(exp, data_root)
    measure = "seg-eval --set eval --final"
    rows = []

    def add(label, images, values, fmt, *, needs_eval=False):
        if exp is None:
            rows.append([label, images, PENDING, PENDING])
        elif needs_eval and eval_sections is None:
            rows.append([label, images, f"{PENDING} ({measure})", PENDING])
        else:
            values = values()
            mean, std = mean_std(values)
            stat = Aggregate(mean, std, values)
            per_split = "; ".join("n/a" if v is None else (f"{100 * v:.1f}" if fmt is format_rate else f"{v:.3f}") for v in values)
            rows.append([label, images, fmt(stat) if fmt is format_rate else format_mean_std(stat, "macro_f1"), per_split])

    splits = exp.splits if exp is not None else ()
    n_eval = ({block: eval_sections[splits[0]]["summary"][block]["n"] for block in ("all", "excluding_ambiguous")} if eval_sections
              else annotation_counts(data_root, "eval"))
    for block, label in (("all", "eval annotations"), ("excluding_ambiguous", "eval annotations without the ambiguous ones")):
        n = n_eval[block]
        for key, name, fmt in (("iou", "IoU", None), ("dice", "Dice", None), ("hit_rate", "Salient-leaf hit rate (%)", format_rate),
                               ("box_area", "Crop box area (% of the image)", format_rate)):
            add(f"{name}, {label}", n, lambda b=block, k=key: [eval_sections[s]["summary"][b].get(k) for s in splits], fmt, needs_eval=True)
    add("Fallbacks on the eval annotations (%)", n_eval["all"], lambda: [eval_sections[s]["summary"]["fallbacks"] / max(1, eval_sections[s]["summary"]["all"]["n"]) for s in splits],
        format_rate, needs_eval=True)
    for domain in DOMAINS:
        n = exp.metrics[splits[0]]["fallbacks"][domain]["n"] if exp is not None else "-"
        add(f"Fallbacks, all cached {domain} images (%)", n, lambda d=domain: [exp.metrics[s]["fallbacks"][d]["rate"] for s in splits], format_rate)
    add("IoU, white val pseudo-masks (checkpoint data)", exp.metrics[splits[0]]["n_val_white"] if exp is not None else "-",
        lambda: [exp.metrics[s]["val_iou_white"] for s in splits], None)
    add("IoU, val composites (checkpoint data)", exp.metrics[splits[0]]["n_val_composites"] if exp is not None else "-",
        lambda: [exp.metrics[s]["val_iou_composite"] for s in splits], None)
    return Table(
        "table_segmenter",
        "Salient-leaf segmenter (S-seg, one per split)",
        ("Metric", "Images per split", "Mean +- std", "Per split (0-4)"),
        rows,
        "Mean +- std over the 5 split-segmenters (std with ddof=1). Eval annotations: the 20 hand-annotated field images that "
        "are looked at once per final segmenter. IoU and Dice compare the post-processed mask (the selected component; a "
        "fallback scores 0) with the annotated polygon at 512x256. Hit: the crop box (with the 15% margin, at the classifier's "
        "input aspect) contains at least 50% of the annotated leaf area; a fallback box is the whole image. Fallback: no "
        "component covers 2% of the image, so the whole image is used. The validation IoUs threshold the raw mask at 0.5.",
    )

BACKBONE_LABELS = {"resnet50": "ResNet50", "convnext_tiny": "ConvNeXt-T", "swin_t": "Swin-T"}
# Every run folder the report draws on, in table order (E1-U and E1-WW are aliases that read another run folder).
REPORTED_EXPERIMENTS = (*ANALYSIS_EXPERIMENTS, "E3-A", "E3-A-WF")


def recommended_experiment(choices) -> str | None:
    return choices.raw("recommended")


def per_class_stat(exp: ExperimentResults, part: str, subset: str, cls: str, key: str) -> Aggregate:
    """Precision, recall or F1 of one class on one subset: mean, std (ddof=1) and the per-split list."""
    values = [exp.metrics[k][part][subset]["per_class"][cls][key] for k in exp.splits]
    mean, std = mean_std(values)
    return Aggregate(mean, std, values)


def per_class_support(exp: ExperimentResults, part: str, subset: str, cls: str) -> int:
    return sum(exp.metrics[k][part][subset]["per_class"][cls]["support"] for k in exp.splits)


def summed_confusion(exp: ExperimentResults, subset: str, part: str = "test") -> np.ndarray:
    """The confusion matrices of the splits added up: rows = true class, columns = predicted class (CLASS_NAMES order)."""
    return sum(np.asarray(exp.metrics[k][part][subset]["confusion_matrix"], dtype=np.int64) for k in exp.splits)


def table_per_class(results: dict, choices) -> Table:
    """Per-class precision, recall and F1 of the recommended method on the white and the field test images."""
    exp_id = recommended_experiment(choices)
    exp = results.get(exp_id) if exp_id else None
    rows = []
    for domain in DOMAINS:
        for cls in CLASS_NAMES:
            if exp is None:
                rows.append([domain, cls, PENDING, PENDING, PENDING, PENDING])
                continue
            stats = [format_mean_std(per_class_stat(exp, "test", domain, cls, key), "macro_f1") for key in ("precision", "recall", "f1")]
            rows.append([domain, cls, per_class_support(exp, "test", domain, cls), *stats])
        if exp is None:
            rows.append([domain, "macro-F1", PENDING, "-", "-", PENDING])
        else:
            total = sum(per_class_support(exp, "test", domain, cls) for cls in CLASS_NAMES)
            rows.append([domain, "macro-F1", total, "-", "-", format_mean_std(aggregate(exp, domain, "macro_f1", "test"), "macro_f1")])
    return Table(
        "table_per_class",
        f"Per-class results of the recommended method ({exp_id or 'not chosen yet, gate g2'}), test split",
        ("Domain", "Class", "Support (5 splits)", "Precision", "Recall", "F1"),
        rows,
        "Mean +- std over the 5 test splits (std with ddof=1). Support is the number of test images of the class summed over the "
        "5 splits (an image can be in the test part of several splits). The macro-F1 row is the mean of the per-split macro-F1, "
        "not the mean of the class rows above it. A class that is never predicted in a split has precision 0 in that split.",
    )


def read_run_json(data_root, exp: ExperimentResults, split_seed: int, name: str) -> dict | None:
    """config.json or env.json of one split of an experiment's run folder (None when the file is missing)."""
    path = split_dir(runs_dir(data_root) / exp.run_name, split_seed) / name
    if not path.is_file():
        return None
    return json.loads(read_file_bytes(path).decode("utf-8"))


def hparam_cells(config: dict) -> dict:
    """The hyperparameters of one run as the table shows them, all read from its config.json."""
    e = config["experiment"]
    factor = config.get("choices_used", {}).get("composite_n_factor")
    return {
        "Backbone": e["backbone"],
        "Pretrained weights": config.get("weights") or "none",
        "Input mode": e["input_mode"],
        "Input HxW": "x".join(str(v) for v in config["input_size"]),
        "Train on": " + ".join(e["train_domains"]) + (" + composites" if e["use_composites"] else ""),
        "Checkpoint chosen on (val)": " + ".join(e["select_domains"]),
        "Composites per epoch": f"{factor:g}x" if factor is not None and e["use_composites"] else "-",
        "Linear-probe epochs x lr": f"{e['stage1_epochs']} x {e['stage1_lr']:g}",
        "Fine-tune epochs (max)": e["epochs"],
        "Learning rate": f"{e['lr']:g}",
        "Weight decay": f"{e['weight_decay']:g}",
        "Warmup epochs": e["warmup_epochs"],
        "Label smoothing": f"{e['label_smoothing']:g}",
        "Batch size x accumulation": f"{e['batch_size']} x {e['grad_accum']}",
        "Gradient clip norm": f"{e['clip_norm']:g}",
        "Early-stop patience": e["patience"],
        "Dropout": f"{e['dropout']:g}",
    }


HPARAM_COLUMNS = (
    "Backbone", "Pretrained weights", "Input mode", "Input HxW", "Train on", "Checkpoint chosen on (val)", "Composites per epoch",
    "Linear-probe epochs x lr", "Fine-tune epochs (max)", "Learning rate", "Weight decay", "Warmup epochs", "Label smoothing",
    "Batch size x accumulation", "Gradient clip norm", "Early-stop patience", "Dropout",
)


def alias_note(exp: ExperimentResults) -> str:
    """'' for a run folder that carries its own name, else 'E0-rect' (the run an alias such as E1-U reads)."""
    return "" if exp.run_name == exp.exp_id else exp.run_name


def table_hparams(results: dict, data_root) -> Table:
    """One row per reported experiment, every value read from the config.json of its five runs. A value that differs
    between the splits of one experiment is shown as 'varies: a / b' and named in the note."""
    rows, varying, missing = [], [], []
    for exp_id in REPORTED_EXPERIMENTS:
        exp = results.get(exp_id)
        if exp is None:
            rows.append([exp_id, "-", *[PENDING] * len(HPARAM_COLUMNS)])
            continue
        configs = [read_run_json(data_root, exp, k, "config.json") for k in exp.splits]
        if any(config is None for config in configs):
            missing.append(exp_id)
            rows.append([exp_id, exp.run_name, *["n/a"] * len(HPARAM_COLUMNS)])
            continue
        per_split = [hparam_cells(config) for config in configs]
        cells = []
        for column in HPARAM_COLUMNS:
            values = list(dict.fromkeys(str(cell[column]) for cell in per_split))
            if len(values) > 1:
                varying.append(f"{exp_id} ({column})")
            cells.append(values[0] if len(values) == 1 else "varies: " + " / ".join(values))
        rows.append([exp_id, exp.run_name, *cells])
    note = (
        "Every value is read from config.json of the experiment's runs (not typed in). "
        + ("Values are identical across the 5 splits of every experiment. " if not varying
           else "Not identical across the splits: " + ", ".join(varying) + ". ")
        + ("config.json is missing for: " + ", ".join(missing) + ". " if missing else "")
        + "E1-U and E1-WW are aliases that read the run folder named in the second column. Not part of config.json because they "
        "are fixed in the code: optimiser AdamW; stage 1 trains the classifier head only at a constant lr, stage 2 all weights with a linear warmup "
        "then cosine decay per optimiser step; mixed precision (fp16 autocast) on CUDA only, cross-entropy with the label smoothing "
        "above, checkpoint = best validation macro-F1 on the domains the model trained on. Training augmentation: random crop of "
        f"{AUG_CROP_AREA[0]:.0%}-{AUG_CROP_AREA[1]:.0%} of the area, random horizontal and vertical flips, rotation up to "
        f"+-{AUG_ROTATION_DEG:g} degrees, brightness +-{AUG_BRIGHTNESS:g}, contrast +-{AUG_CONTRAST:g}, saturation "
        f"+-{AUG_SATURATION:g}, hue +-{AUG_HUE:g}; evaluation images are only resized. Rows that are not complete yet read 'pending'."
    )
    return Table("table_hparams", "Hyperparameters of every reported experiment", ("Experiment", "Run folder", *HPARAM_COLUMNS), rows, note)

BENCHMARK_FILENAME = "inference_benchmark.json"
BENCHMARK_FORMAT = 1
BENCHMARK_WARMUP = 10  # forward passes that are run and not timed
BENCHMARK_REPEATS = 50  # timed forward passes; the table reports their median
DEVICE_ORDER = ("cpu", "mps", "cuda")


def benchmark_path(data_root) -> Path:
    return results_dir(data_root) / BENCHMARK_FILENAME


def read_benchmark(data_root) -> dict:
    """{device: record} of inference_benchmark.json. {} when the file is missing (no benchmark run yet) or unusable."""
    path = benchmark_path(data_root)
    if not path.is_file():
        return {}
    try:
        data = json.loads(read_file_bytes(path).decode("utf-8"))
        devices = data["devices"]
        if data["format"] != BENCHMARK_FORMAT or not all(isinstance(r["backbones"], dict) for r in devices.values()):
            raise ValueError(f"unexpected format {data['format']!r}")
    except (ValueError, KeyError, TypeError, AttributeError) as exc:
        warn(f"{path}: unusable ({exc}); run `benchmark` again. Inference times read 'not measured'")
        return {}
    return {device: devices[device] for device in DEVICE_ORDER if device in devices}


def synchronize(device: str) -> None:
    if device == "cuda":
        torch.cuda.synchronize()
    elif device == "mps":
        torch.mps.synchronize()


def time_inference(model: nn.Module, device: str, size: tuple, *, warmup: int = BENCHMARK_WARMUP, repeats: int = BENCHMARK_REPEATS) -> dict:
    """Milliseconds of one forward pass on one image (batch 1): median and quartiles of ``repeats`` timed passes after
    ``warmup`` untimed ones. The device is synchronised around every pass, so asynchronous GPU work is counted."""
    model.eval()
    x = torch.rand(1, 3, *size, device=device)
    amp = device == "cuda"  # the same autocast the evaluation uses
    times = []
    with torch.inference_mode(), torch.autocast(device_type="cuda", dtype=torch.float16, enabled=amp):
        for i in range(warmup + repeats):
            synchronize(device)
            started = time.perf_counter()
            model(x)
            synchronize(device)
            if i >= warmup:
                times.append((time.perf_counter() - started) * 1000.0)
    q1, median, q3 = (float(v) for v in np.percentile(times, [25, 50, 75]))
    return {"median_ms": round(median, 2), "q1_ms": round(q1, 2), "q3_ms": round(q3, 2)}


def run_benchmark(data_root, device: str, out=print, *, warmup: int = BENCHMARK_WARMUP, repeats: int = BENCHMARK_REPEATS) -> dict:
    """Time the three backbones at the chosen input mode on ``device`` (untrained weights: the speed does not depend on
    them) and merge the record into inference_benchmark.json, keeping the records of the other devices."""
    data_root = Path(data_root)
    mode = load_choices(data_root).get("input_mode")
    size = input_size(mode)
    env = environment_record(device)
    backbones = {}
    for name in BACKBONES:
        torch.manual_seed(0)
        model = build_model(name, pretrained=False).to(device)
        backbones[name] = {**time_inference(model, device, size, warmup=warmup, repeats=repeats), "parameters": count_parameters(model)}
        out(f"benchmark: {name} on {device}: {backbones[name]['median_ms']:.1f} ms/image (median of {repeats})")
        del model
        free_device_memory(device)
    record = {
        "device": device, "precision": precision_of(device), "input_mode": mode, "input_size": list(size), "batch_size": 1,
        "warmup": warmup, "repeats": repeats, "torch_threads": torch.get_num_threads(),
        **{key: env[key] for key in ("python", "platform", "torch", "torchvision", "cpu_count", "gpu", "cuda")},
        "measured": "model forward pass only (no image decoding or resizing), untrained weights, batch size 1",
        "backbones": backbones,
    }
    devices = read_benchmark(data_root)
    devices[device] = record
    path = benchmark_path(data_root)
    write_json(path, {"format": BENCHMARK_FORMAT, "devices": {d: devices[d] for d in DEVICE_ORDER if d in devices}}, indent=2)
    out(f"benchmark: wrote {path}")
    return record


def precision_of(device: str) -> str:
    """The numeric precision a run on this device uses: training and evaluation autocast to fp16 on CUDA only."""
    return "mixed precision (fp16 autocast)" if device == "cuda" else "fp32"


def host_label(env: dict) -> str:
    """Where a run was made, from its env.json: Kaggle and Colab leave their paths in torch_home."""
    home = env.get("torch_home") or ""
    if home.startswith("/kaggle"):
        return "Kaggle"
    if home.startswith("/content"):
        return "Colab"
    return "local " + str(env.get("platform", "")).split("-")[0]


def hardware_signature(exp: ExperimentResults | None, data_root) -> tuple | None:
    """The distinct (host, device, gpu, torch, python) of an experiment's five runs, read from env.json."""
    if exp is None:
        return None
    envs = [read_run_json(data_root, exp, k, "env.json") for k in exp.splits]
    if any(env is None for env in envs):
        return None
    return tuple(sorted({(host_label(env), env["device"], env.get("gpu") or "-", env["torch"], env["python"]) for env in envs}))


def hardware_text(signature: tuple | None, *, full: bool = True) -> str:
    """'Kaggle, cuda (Tesla T4), torch 2.11.0+cu128, Python 3.13.15, mixed precision (fp16 autocast)'; ``full=False`` stops at the device."""
    if not signature:
        return "n/a"
    parts = []
    for host, device, gpu, torch_version, python in signature:
        text = f"{host}, {device} ({gpu})"
        parts.append(text + (f", torch {torch_version}, Python {python}, {precision_of(device)}" if full else ""))
    return " / ".join(parts)


def format_number(stat, decimals: int = 1, scale: float = 1.0) -> str:
    """'8.5 +- 1.2' for a mean +- std of a plain quantity (minutes, seconds, epochs)."""
    if stat.mean != stat.mean or stat.std != stat.std:
        return "n/a"
    return f"{stat.mean * scale:.{decimals}f} +- {stat.std * scale:.{decimals}f}"


def metric_stat(exp: ExperimentResults, key: str) -> Aggregate:
    values = [exp.metrics[k][key] for k in exp.splits]
    mean, std = mean_std(values)
    return Aggregate(mean, std, values)


def table_runtime(results: dict, data_root) -> Table:
    """Training cost per experiment from metrics.json and env.json, and inference ms/image from the benchmark file."""
    benchmark = read_benchmark(data_root)
    devices = list(benchmark)
    header = ("Experiment", "Run folder", "Hardware", "Training time per run (min)", "Seconds per epoch", "Epochs run", "Parameters (M)",
              *([f"Inference ms/image, median (quartiles), {d}" for d in devices] or ["Inference ms/image"]))
    rows = []
    for exp_id in REPORTED_EXPERIMENTS:
        exp = results.get(exp_id)
        backbone = exp.config.backbone if exp is not None else EXPERIMENTS[exp_id].backbone
        if devices:
            timing = []
            for device in devices:
                entry = benchmark[device]["backbones"].get(backbone) if backbone else None
                timing.append("n/a" if entry is None else f"{entry['median_ms']:.1f} ({entry['q1_ms']:.1f}-{entry['q3_ms']:.1f})")
        else:
            timing = ["not measured (run benchmark)"]
        if exp is None:
            rows.append([exp_id, "-", *[PENDING] * (len(header) - 2)])
            continue
        hardware = hardware_signature(exp, data_root)
        rows.append([
            exp_id, exp.run_name, hardware_text(hardware, full=False),
            format_number(metric_stat(exp, "train_time_s"), 1, 1 / 60), format_number(metric_stat(exp, "seconds_per_epoch"), 1),
            format_number(metric_stat(exp, "epochs_run"), 1), f"{exp.metrics[exp.splits[0]]['parameters'] / 1e6:.1f}", *timing,
        ])
    where = "; ".join(
        f"{d}: {r['platform']}, {r['cpu_count']} cores, {r['gpu'] or 'no GPU'}, torch {r['torch']}, {r['input_mode']} input "
        f"{r['input_size'][0]}x{r['input_size'][1]}, {r['precision']}, median of {r['repeats']} after {r['warmup']} warm-up passes"
        for d, r in benchmark.items()
    )
    note = (
        "Training time and seconds per epoch are the mean +- std (ddof=1) over the 5 runs of an experiment; a run's time includes "
        "validation after every epoch, and the time is wall clock on a machine whose load varied (shared Kaggle/Colab sessions, "
        "a laptop), so it is only comparable within one hardware group and only roughly. Early stopping makes the epochs run "
        "differ between runs. Hardware is read from env.json (the findings list the groups with their torch versions). "
        "E1-U and E1-WW are aliases that read the run folder named in the second column. Parameters are those of the classifier "
        "with its 5-class head. Inference time is not measured by `summarize` (it would not be reproducible): the `benchmark` "
        "command writes inference_benchmark.json and this table reads it. It times the model forward pass for one image "
        "(batch 1), not image decoding, resizing or the first call. "
        + (f"Measured on - {where}." if benchmark else "No benchmark file yet, so inference times read 'not measured (run benchmark)'.")
    )
    return Table("table_runtime", "Training and inference cost", header, rows, note)

# One marker per subset in every figure that shows scores (colours: DOMAIN_COLORS; mixed has no domain, so it is grey).
SUBSET_COLORS = {**DOMAIN_COLORS, "mixed": "#8C8C8C"}
SUBSET_MARKERS = {"white": "o", "field": "s", "mixed": "^"}
SPLIT_COLORS = (OKABE_ITO["black"], OKABE_ITO["sky"], OKABE_ITO["green"], OKABE_ITO["vermilion"], OKABE_ITO["purple"])  # one per split
SCENARIO_MODELS = ("E1-U", "E2-cnx-U", "E2-swin-U", "E3-A")  # the main models of scenario_bars.png
# domain_gap.png: (training regime, experiment). The regimes follow the phase-04 questions.
DOMAIN_GAP_ROWS = (
    ("F->F", "E1-FF"), ("W->F", "E1-WF"), ("W->F", "E2-cnx-WF"), ("W->F", "E2-swin-WF"), ("W + composites->F*", "E3-A-WF"),
    ("U (white + field)", "E1-U"), ("U (white + field)", "E2-swin-U"), ("A (U + composites)", "E3-A"),
)
WF_CONFUSION_EXPERIMENTS = ("E1-WF", "E2-swin-WF", "E3-A-WF")  # which classes collapse under W->F, with E1-WF as the reference
FIGURE_FONT = 7
WRAPPED_CLASSES = [name.replace(" ", "\n") for name in CLASS_NAMES]


def tidy_axes(ax) -> None:
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.set_axisbelow(True)


def finish_figure(fig, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=FIGURE_DPI)
    pyplot().close(fig)
    return path


def experiment_label(exp: ExperimentResults) -> str:
    return f"{exp.exp_id} ({BACKBONE_LABELS.get(exp.config.backbone, exp.config.backbone)})"


def save_confusion(data_root, exp: ExperimentResults, subset: str, path: Path | None = None) -> Path:
    """`confusion_<exp>_<subset>.png`: the test confusion matrices of the 5 splits added up; the colour is the share of the
    true class (each row sums to 1), the number in a cell is the image count. The frame has the domain's colour."""
    plt = pyplot()
    path = path or figures_dir(data_root) / f"confusion_{exp.exp_id}_{subset}.png"
    matrix = summed_confusion(exp, subset)
    share = matrix / np.maximum(matrix.sum(axis=1, keepdims=True), 1)
    trained = " + ".join(exp.config.train_domains)
    with plt.rc_context({"font.size": FIGURE_FONT}):
        fig, ax = plt.subplots(figsize=(3.9, 3.75))
        image = ax.imshow(share, cmap="Blues", vmin=0.0, vmax=1.0)
        for i in range(NUM_CLASSES):
            for j in range(NUM_CLASSES):
                ax.text(j, i, str(matrix[i, j]), ha="center", va="center", fontsize=FIGURE_FONT + 0.5,
                        fontweight="bold" if i == j else "normal", color="white" if share[i, j] > 0.55 else "black")
        ax.set_xticks(range(NUM_CLASSES), WRAPPED_CLASSES)
        ax.set_yticks(range(NUM_CLASSES), WRAPPED_CLASSES)
        ax.set_xlabel("Predicted class")
        ax.set_ylabel("True class")
        ax.set_title(f"{exp.exp_id}: trained on {trained}, tested on {subset} images\n"
                     f"(5 test splits added up, {int(matrix.sum())} predictions)", fontsize=FIGURE_FONT + 0.5)
        for spine in ax.spines.values():
            spine.set_edgecolor(DOMAIN_COLORS[subset])
            spine.set_linewidth(2.0)
        colorbar = fig.colorbar(image, ax=ax, fraction=0.046, pad=0.03)
        colorbar.set_label("Share of the true class")
        colorbar.outline.set_visible(False)
        fig.tight_layout(pad=0.6)
        return finish_figure(fig, path)


def save_scenario_bars(data_root, results: dict, recommended: str | None, path: Path | None = None) -> Path | None:
    """`scenario_bars.png`: test macro-F1 of the main models for the three scenarios (white, field, mixed); bars = mean over
    the 5 splits, whiskers = std (ddof=1), dots = the single splits."""
    plt = pyplot()
    path = path or figures_dir(data_root) / "scenario_bars.png"
    models = [m for m in SCENARIO_MODELS if m in results]
    if not models:
        return None
    subsets = ("white", "field", "mixed")
    width = 0.26
    with plt.rc_context({"font.size": FIGURE_FONT}):
        fig, ax = plt.subplots(figsize=(4.4, 3.0))
        for k, subset in enumerate(subsets):
            for position, model in enumerate(models):
                stat = aggregate(results[model], subset, "macro_f1", "test")
                x = position + (k - 1) * width
                ax.bar(x, stat.mean, width * 0.92, color=SUBSET_COLORS[subset], label=SUBSET_LABELS[subset] if position == 0 else None)
                ax.errorbar(x, stat.mean, yerr=stat.std, color="black", capsize=2, linewidth=0.8, capthick=0.8)
                jitter = np.linspace(-0.07, 0.07, len(stat.values))
                ax.scatter(x + jitter, stat.values, s=5, marker=SUBSET_MARKERS[subset], color="white", edgecolor="black", linewidth=0.4, zorder=3)
        ax.set_xticks(range(len(models)), [f"{m}\n{BACKBONE_LABELS.get(results[m].config.backbone, '')}"
                                           + ("\n(recommended)" if m == recommended else "") for m in models])
        ax.set_ylim(0, 1.0)
        ax.set_ylabel("Test macro-F1 (mean ± std, 5 splits)")
        ax.yaxis.grid(True, color="#DDDDDD", linewidth=0.6)
        tidy_axes(ax)
        ax.legend(frameon=False, ncol=3, loc="lower center", bbox_to_anchor=(0.5, 1.0), handlelength=1.2, columnspacing=1.2)
        fig.tight_layout(pad=0.6)
        return finish_figure(fig, path)


def save_domain_gap(data_root, results: dict, path: Path | None = None) -> Path | None:
    """`domain_gap.png`: test macro-F1 on the field images for each training regime (the transfer story). Bars = mean over the
    5 splits, whiskers = std (ddof=1), dots = the single splits."""
    plt = pyplot()
    path = path or figures_dir(data_root) / "domain_gap.png"
    rows = [(regime, exp_id) for regime, exp_id in DOMAIN_GAP_ROWS if exp_id in results]
    if not rows:
        return None
    ypos, last, y = [], None, 0.0
    for regime, _ in rows:
        y += 0.0 if last in (None, regime) else 0.6
        ypos.append(y)
        y += 1.0
        last = regime
    with plt.rc_context({"font.size": FIGURE_FONT}):
        fig, ax = plt.subplots(figsize=(4.4, 0.27 * (ypos[-1] + 1) + 1.0))
        for y, (regime, exp_id) in zip(ypos, rows):
            stat = aggregate(results[exp_id], "field", "macro_f1", "test")
            ax.barh(y, stat.mean, 0.72, color=DOMAIN_COLORS["field"])
            ax.errorbar(stat.mean, y, xerr=stat.std, color="black", capsize=2, linewidth=0.8, capthick=0.8)
            ax.scatter(stat.values, y + np.linspace(-0.2, 0.2, len(stat.values)), s=5, marker=SUBSET_MARKERS["field"], color="white",
                       edgecolor="black", linewidth=0.4, zorder=3)
            ax.text(min(1.0, max(stat.values + [stat.mean + stat.std])) + 0.015, y, f"{stat.mean:.3f}", va="center", fontsize=FIGURE_FONT)
        ax.set_yticks(ypos, [f"{regime}\n{exp_id}, {BACKBONE_LABELS.get(results[exp_id].config.backbone, '')}" for regime, exp_id in rows],
                      fontsize=FIGURE_FONT - 0.5)
        ax.set_ylim(ypos[-1] + 0.7, -0.7)
        ax.set_xlim(0, 1.0)
        ax.set_xlabel("Field test macro-F1 (mean ± std, 5 splits)")
        ax.xaxis.grid(True, color="#DDDDDD", linewidth=0.6)
        tidy_axes(ax)
        if any(exp_id == "E3-A-WF" for _, exp_id in rows):
            fig.text(0.01, 0.005, "* white photos only as leaves, but field images are the composite backgrounds: not pure W->F",
                     fontsize=FIGURE_FONT - 1.5, va="bottom", color="#444444")
        fig.tight_layout(pad=0.6, rect=(0, 0.03, 1, 1))
        return finish_figure(fig, path)


def read_history(data_root, exp: ExperimentResults, split_seed: int) -> list | None:
    """history.csv of one run as dicts (numbers as floats, stage as text); None when the file is missing."""
    path = split_dir(runs_dir(data_root) / exp.run_name, split_seed) / "history.csv"
    if not path.is_file():
        return None
    with open(path, newline="") as handle:
        return [{key: (value if key == "stage" else float(value)) for key, value in row.items()} for row in csv.DictReader(handle)]


def save_training_curves(data_root, exp: ExperimentResults, path: Path | None = None) -> Path | None:
    """`training_curves_<exp>.png`: training loss and validation macro-F1 per epoch, the 5 splits overlaid. The grey band is the
    linear-probe stage, the star the epoch whose checkpoint was kept."""
    plt = pyplot()
    path = path or figures_dir(data_root) / f"training_curves_{exp.exp_id}.png"
    histories = {k: read_history(data_root, exp, k) for k in exp.splits}
    histories = {k: h for k, h in histories.items() if h}
    if not histories:
        return None
    selected = " + ".join(exp.config.select_domains)
    with plt.rc_context({"font.size": FIGURE_FONT}):
        fig, (loss_ax, f1_ax) = plt.subplots(2, 1, figsize=(4.4, 4.2), sharex=True)
        for k, history in histories.items():
            color = SPLIT_COLORS[k % len(SPLIT_COLORS)]
            epochs = [row["epoch"] for row in history]
            loss_ax.plot(epochs, [row["train_loss"] for row in history], color=color, linewidth=1.0, label=f"split {k}")
            f1_ax.plot(epochs, [row["val_macro_f1"] for row in history], color=color, linewidth=1.0)
            kept = [row for row in history if row["best"]][-1:]
            f1_ax.scatter([row["epoch"] for row in kept], [row["val_macro_f1"] for row in kept], marker="*", s=40, color=color,
                          edgecolor="black", linewidth=0.5, zorder=3)
        probe = max((row["epoch"] for h in histories.values() for row in h if row["stage"] == "lp"), default=0)
        for ax in (loss_ax, f1_ax):
            if probe:
                ax.axvspan(0.5, probe + 0.5, color="#E6E6E6", zorder=0)
            ax.yaxis.grid(True, color="#DDDDDD", linewidth=0.6)
            tidy_axes(ax)
        if probe:
            loss_ax.text(probe / 2 + 0.5, 0.4, "linear\nprobe", transform=loss_ax.get_xaxis_transform(), ha="center", va="top",
                         fontsize=FIGURE_FONT - 1)
        loss_ax.set_ylabel("Training loss")
        f1_ax.set_ylabel(f"Validation macro-F1\n({selected})")
        f1_ax.set_xlabel("Epoch (star = kept checkpoint)")
        f1_ax.set_ylim(0, 1.0)
        loss_ax.set_title(f"{exp.exp_id}: training curves of the 5 splits", fontsize=FIGURE_FONT + 0.5)
        loss_ax.legend(frameon=False, ncol=5, loc="upper right", fontsize=FIGURE_FONT - 1, handlelength=1.2, columnspacing=0.8)
        fig.tight_layout(pad=0.6)
        return finish_figure(fig, path)


def write_figures(data_root, results: dict, choices) -> list:
    """The T7.3 figures that the available runs support. Returns the paths written."""
    recommended = recommended_experiment(choices)
    paths = []
    if recommended in results:
        paths += [save_confusion(data_root, results[recommended], subset) for subset in DOMAINS]
        paths.append(save_training_curves(data_root, results[recommended]))
    for exp_id in WF_CONFUSION_EXPERIMENTS:
        if exp_id in results:
            paths.append(save_confusion(data_root, results[exp_id], "field"))
    paths += [save_scenario_bars(data_root, results, recommended), save_domain_gap(data_root, results)]
    return [p for p in paths if p is not None]

CASE_LOW_CONFIDENCE = 0.5  # a correct prediction whose top probability is below this is not a success but a challenging case
CASE_SHEET_IMAGES = 10  # images per contact sheet: 2 rows of 5
CASE_CATEGORIES = ("success", "failure", "challenging")
CASE_SHEET_COLUMNS = 5
CASES_FILENAME = "cases.csv"


def classify_case(correct: list, confidence: list) -> str:
    """One image's outcomes over the splits whose test part held it: ``correct[i]`` and the top probability
    ``confidence[i]`` of each. failure = wrong every time; success = right every time and never below
    CASE_LOW_CONFIDENCE; challenging = everything else (mixed outcomes, or right but unsure)."""
    if not any(correct):
        return "failure"
    if all(correct) and min(confidence) >= CASE_LOW_CONFIDENCE:
        return "success"
    return "challenging"


def pool_predictions(data_root, exp: ExperimentResults) -> dict:
    """{filename: {"domain", "true", "tests": {split: (predicted class index, probabilities)}}} from predictions_test.csv of
    every split of ``exp``. An image is in the test part of about 0.75 splits on average, so most have one to three entries."""
    pooled = {}
    for split_seed in exp.splits:
        path = split_dir(runs_dir(data_root) / exp.run_name, split_seed) / "predictions_test.csv"
        if not path.is_file():
            raise ExperimentError(f"{exp.exp_id}: {path} is missing")
        with open(path, newline="") as handle:
            for row in csv.DictReader(handle):
                probs = [float(row[f"p{i}"]) for i in range(NUM_CLASSES)]
                entry = pooled.setdefault(row["filename"], {"domain": row["domain"], "true": row["true"], "tests": {}})
                entry["tests"][split_seed] = (CLASS_NAMES.index(row["pred"]), probs)
    return pooled


def case_rows(pooled: dict) -> list:
    """One dict per image (sorted by filename): outcome counts, category, the split-wise predictions, the modal prediction
    (ties go to the higher summed probability) and the probabilities of the true and the modal class, averaged over the splits."""
    rows = []
    for filename in sorted(pooled):
        entry = pooled[filename]
        true_index = CLASS_NAMES.index(entry["true"])
        tests = entry["tests"]
        correct = [pred == true_index for pred, _ in tests.values()]
        top = [max(probs) for _, probs in tests.values()]
        counts = Counter(pred for pred, _ in tests.values())
        wrong = [pred for pred, _ in counts.most_common() if pred != true_index]  # wrong classes, the most frequent first
        modal = max(counts, key=lambda c: (counts[c], sum(probs[c] for _, probs in tests.values()), -c))
        rows.append({
            "filename": filename, "domain": entry["domain"], "true": entry["true"], "tested": len(tests), "correct": sum(correct),
            "category": classify_case(correct, top),
            "preds": [CLASS_NAMES[tests[k][0]] if k in tests else "" for k in ANALYSIS_SPLITS],
            "modal_pred": CLASS_NAMES[modal], "wrong_pred": CLASS_NAMES[wrong[0]] if wrong else "",
            "mean_p_modal": float(np.mean([probs[modal] for _, probs in tests.values()])),
            "mean_p_true": float(np.mean([probs[true_index] for _, probs in tests.values()])),
            "min_top_p": float(min(top)),
        })
    return rows


def cases_csv(rows: list) -> str:
    header = ["filename", "domain", "true", "tested", "correct", "category", *[f"pred_split{k}" for k in ANALYSIS_SPLITS],
              "modal_pred", "wrong_pred", "mean_p_modal", "mean_p_true", "min_top_p"]
    return csv_text(header, [[r["filename"], r["domain"], r["true"], r["tested"], r["correct"], r["category"], *r["preds"], r["modal_pred"],
                              r["wrong_pred"], f"{r['mean_p_modal']:.3f}", f"{r['mean_p_true']:.3f}", f"{r['min_top_p']:.3f}"] for r in rows])


# Which images a contact sheet shows first within one (domain, class): successes the model is surest of, failures that were tested
# most often (the most evidence) and are the most confidently wrong, challenging cases that split the splits closest to half.
CASE_ORDER = {
    "success": lambda r: (-r["mean_p_modal"], -r["tested"], r["filename"]),
    "failure": lambda r: (-r["tested"], -r["mean_p_modal"], r["filename"]),
    "challenging": lambda r: (-r["tested"], abs(r["correct"] / r["tested"] - 0.5), r["filename"]),
}


def select_cases(rows: list, category: str, n: int = CASE_SHEET_IMAGES) -> list:
    """Up to ``n`` images of a category for its contact sheet, deterministic and balanced: one image per (class, domain) group in
    turn, white and field alternating, until ``n`` are picked, so a domain or class with cases is shown before any is repeated.
    The result is ordered white then field, by class."""
    queues = []
    for cls in CLASS_NAMES:
        for domain in DOMAINS:
            group = [r for r in rows if r["category"] == category and r["domain"] == domain and r["true"] == cls]
            if group:
                queues.append(sorted(group, key=CASE_ORDER[category]))
    picked = []
    while len(picked) < n and any(queues):
        for queue in queues:
            if queue and len(picked) < n:
                picked.append(queue.pop(0))
    return sorted(picked, key=lambda r: (DOMAINS.index(r["domain"]), CLASS_NAMES.index(r["true"]), r["filename"]))


def case_label(row: dict) -> str:
    """'true ->' over 'predicted (p)' over 'filename  correct/tested'; p is the mean probability of the predicted (modal) class.
    A fourth line names the wrong class an image that is mostly right was also taken for."""
    text = f"{row['true']} ->\n{row['modal_pred']} ({row['mean_p_modal']:.2f})\n{row['filename']}  {row['correct']}/{row['tested']} correct"
    if row["wrong_pred"] and row["modal_pred"] == row["true"]:
        text += f"\nalso taken for {row['wrong_pred']}"
    return text


def save_case_sheet(data_root, rows: list, category: str, exp_id: str, path: Path | None = None) -> Path:
    """A contact sheet `cases_<category>.png` (2 rows of 5): the photo (domain-coloured frame and tag), the label
    `true -> predicted (p)` and how often the image was right. The photos are drawn 1:1 at the figure's resolution."""
    plt = pyplot()
    path = path or figures_dir(data_root) / f"cases_{category}.png"
    picks = select_cases(rows, category)
    n_rows = max(1, math.ceil(len(picks) / CASE_SHEET_COLUMNS))
    width_in, margin, gap, tile_w, tile_h, label_h, head = 5.8, 0.08, 0.05, 1.08, 1.9, 0.46, 0.22
    pitch = (width_in - 2 * margin - tile_w) / (CASE_SHEET_COLUMNS - 1)  # left edge to left edge of neighbouring tiles
    height_in = head + n_rows * (tile_h + label_h + gap) + margin
    adjective = {"success": "consistent successes", "failure": "consistent failures", "challenging": "challenging cases"}[category]
    with plt.rc_context({"font.size": 6}):
        fig = plt.figure(figsize=(width_in, height_in))
        fig.text(margin / width_in, 1 - 0.04 / height_in, f"{exp_id}: {adjective} (test images pooled over the 5 splits; label: true -> predicted (mean p))",
                 fontsize=6.3, fontweight="bold", va="top")
        if not picks:
            fig.text(0.5, 0.5, f"no {adjective} in the test predictions", ha="center", va="center", fontsize=8)
        for slot, row in enumerate(picks):
            r, c = divmod(slot, CASE_SHEET_COLUMNS)
            cell_left = margin + c * pitch
            cell_top = height_in - head - r * (tile_h + label_h + gap)
            rgb = read_cached_rgb(data_root, row["filename"])
            scale = min(tile_w * FIGURE_DPI / rgb.shape[1], tile_h * FIGURE_DPI / rgb.shape[0])
            px = (max(1, round(rgb.shape[1] * scale)), max(1, round(rgb.shape[0] * scale)))
            w, h = px[0] / FIGURE_DPI, px[1] / FIGURE_DPI
            ax = fig.add_axes(((cell_left + (tile_w - w) / 2) / width_in, (cell_top - tile_h + (tile_h - h) / 2) / height_in, w / width_in, h / height_in))
            ax.imshow(cv2.resize(rgb, px, interpolation=cv2.INTER_AREA), interpolation="none", aspect="auto")
            ax.set_xticks([])
            ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_edgecolor(DOMAIN_COLORS[row["domain"]])
                spine.set_linewidth(1.6)
            ax.text(0.04, 0.985, DOMAIN_LABELS[row["domain"]].split()[0], transform=ax.transAxes, ha="left", va="top", fontsize=5.5,
                    fontweight="bold", color="white" if row["domain"] == "white" else "black",
                    bbox={"boxstyle": "square,pad=0.2", "fc": DOMAIN_COLORS[row["domain"]], "ec": "none"})
            fig.text((cell_left + tile_w / 2) / width_in, (cell_top - tile_h - 0.03) / height_in, case_label(row), ha="center", va="top",
                     fontsize=5.6, linespacing=1.15)
        return finish_figure(fig, path)


def write_cases(data_root, results: dict, choices, out=print) -> list | None:
    """T7.4: cases.csv and the three contact sheets for the recommended method. None while it is not chosen or not complete."""
    exp_id = recommended_experiment(choices)
    exp = results.get(exp_id) if exp_id else None
    if exp is None:
        warn("cases: skipped, the recommended method is not chosen (gate g2) or not complete")
        return None
    rows = case_rows(pool_predictions(data_root, exp))
    path = results_dir(data_root) / CASES_FILENAME
    write_text_atomic(path, cases_csv(rows))
    out(f"summarize: wrote {path}")
    shown = [name for category in CASE_CATEGORIES for name in (r["filename"] for r in select_cases(rows, category))]
    if not all((cache_dir(data_root) / name).is_file() for name in shown):
        warn("cases: contact sheets skipped, the image cache is incomplete (run `prepare`)")
        return rows
    for category in CASE_CATEGORIES:
        out(f"summarize: wrote {save_case_sheet(data_root, rows, category, exp.exp_id)}")
    return rows

def have(results: dict, *exp_ids) -> bool:
    return all(exp_id in results for exp_id in exp_ids)


def pending_sentence(*exp_ids) -> str:
    return "Not available yet: " + ", ".join(exp_ids) + " is not complete."


def f1_text(exp: ExperimentResults, subset: str = "field", part: str = "test") -> str:
    return format_mean_std(aggregate(exp, subset, "macro_f1", part), "macro_f1")


def paired_text(a: ExperimentResults, b: ExperimentResults, subset: str = "field", part: str = "test") -> str:
    """'+0.012 +- 0.034; E2-swin-U ahead in 3 of 5 splits' for the per-split difference a - b."""
    diff = paired_difference(a, b, subset, "macro_f1", part)
    return f"{diff.mean:+.3f} +- {diff.std:.3f}; {a.exp_id} ahead in {diff.ahead} of {len(diff.values)} splits"


def paired_mean(a: ExperimentResults, b: ExperimentResults, subset: str = "field", part: str = "test") -> float:
    return paired_difference(a, b, subset, "macro_f1", part).mean


def direction(value: float, up: str, down: str) -> str:
    return up if value > 0 else down


def per_class_f1_text(exp: ExperimentResults, subset: str = "field") -> str:
    return ", ".join(f"{cls} {per_class_stat(exp, 'test', subset, cls, 'f1').mean:.3f}" for cls in CLASS_NAMES)


def largest_confusions(exp: ExperimentResults, subset: str = "field", top: int = 2) -> str:
    """The most frequent mistakes (true class predicted as another class) of the summed test confusion matrix, with the share of
    the true class's images they make up."""
    matrix = summed_confusion(exp, subset)
    mistakes = sorted(((int(matrix[i, j]), i, j) for i in range(NUM_CLASSES) for j in range(NUM_CLASSES) if i != j and matrix[i, j] > 0),
                      key=lambda m: (-m[0], m[1], m[2]))[:top]
    return "; ".join(f"{CLASS_NAMES[i]} taken for {CLASS_NAMES[j]} in {n} of {int(matrix[i].sum())} images ({n / matrix[i].sum():.0%})"
                     for n, i, j in mistakes) or "no mistakes"


COLLAPSE_RATIO = 0.5  # a class has collapsed under W->F when its field F1 is below this share of the field-trained model's (E1-FF)


def domain_questions_findings(results: dict) -> str:
    """Answers to the four phase-04 questions, in numbers read from the test metrics (field/white macro-F1, mean +- std over the
    5 splits; paired = per-split difference)."""
    paragraphs = []
    if have(results, "E1-FF", "E1-WF"):
        ff, wf = results["E1-FF"], results["E1-WF"]
        gap = paired_mean(wf, ff)
        text = (f"**1. Domain gap.** Field test macro-F1 is {f1_text(ff)} for E1-FF (ResNet50 trained on field images) and {f1_text(wf)} for "
                f"E1-WF (trained on white images only), so training on white alone {direction(gap, 'raises', 'lowers')} field macro-F1 by "
                f"{abs(gap):.3f} (paired E1-WF - E1-FF: {paired_text(wf, ff)}).")
        for exp_id in ("E2-cnx-WF", "E2-swin-WF"):
            if exp_id in results:
                text += f" {exp_id} (white only, {BACKBONE_LABELS[results[exp_id].config.backbone]}) reaches {f1_text(results[exp_id])}."
        if "E3-A-WF" in results:
            extra = f" (paired E3-A-WF - E2-swin-WF: {paired_text(results['E3-A-WF'], results['E2-swin-WF'])})" if "E2-swin-WF" in results else ""
            text += (f" With composites E3-A-WF reaches {f1_text(results['E3-A-WF'])}{extra}; its training leaves are white photos, but the "
                     "backgrounds are field images, so it is not pure W->F.")
        paragraphs.append(text)
    else:
        paragraphs.append("**1. Domain gap.** " + pending_sentence("E1-FF", "E1-WF"))
    if have(results, "E1-U", "E1-FF"):
        u, ff = results["E1-U"], results["E1-FF"]
        diff = paired_mean(u, ff)
        paragraphs.append(f"**2. Does white data help field?** Field test macro-F1 is {f1_text(u)} for E1-U (white + field) and {f1_text(ff)} for E1-FF "
                          f"(field only): the unified model is {direction(diff, 'ahead', 'behind')} by {abs(diff):.3f} (paired E1-U - E1-FF: {paired_text(u, ff)}).")
    else:
        paragraphs.append("**2. Does white data help field?** " + pending_sentence("E1-U", "E1-FF"))
    if have(results, "E1-U", "E1-WW"):
        u, ww = results["E1-U"], results["E1-WW"]
        diff = paired_mean(u, ww, "white")
        paragraphs.append(f"**3. Does field data hurt white?** White test macro-F1 is {f1_text(u, 'white')} for E1-U (white + field) and {f1_text(ww, 'white')} for "
                          f"E1-WW (white only, the E1-WF run): the unified model is {direction(diff, 'ahead', 'behind')} by {abs(diff):.3f} "
                          f"(paired E1-U - E1-WW: {paired_text(u, ww, 'white')}).")
    else:
        paragraphs.append("**3. Does field data hurt white?** " + pending_sentence("E1-U", "E1-WW"))
    rows = [exp_id for exp_id in ("E1-WF", "E2-cnx-WF", "E2-swin-WF", "E3-A-WF") if exp_id in results]
    if rows and "E1-FF" in results:
        lines = [f"- E1-FF (field only, reference): per-class field F1 {per_class_f1_text(results['E1-FF'])}."]
        for exp_id in rows:
            exp = results[exp_id]
            change = {cls: per_class_stat(exp, "test", "field", cls, "f1").mean - per_class_stat(results["E1-FF"], "test", "field", cls, "f1").mean
                      for cls in CLASS_NAMES}
            collapsed = [cls for cls in CLASS_NAMES
                         if per_class_stat(exp, "test", "field", cls, "f1").mean < COLLAPSE_RATIO * per_class_stat(results["E1-FF"], "test", "field", cls, "f1").mean]
            worst = min(change, key=lambda cls: (change[cls], CLASS_NAMES.index(cls)))
            lines.append(f"- {exp_id}: per-class field F1 {per_class_f1_text(exp)}. Collapsed: {', '.join(collapsed) if collapsed else 'none'}. "
                         f"Largest change against E1-FF: {worst} ({change[worst]:+.3f}). Most frequent mistakes: {largest_confusions(exp)}.")
        paragraphs.append("**4. Which classes collapse under W->F?** Per-class field test F1 (mean over the 5 splits). A class counts as collapsed when its "
                          f"F1 is below {COLLAPSE_RATIO:.0%} of E1-FF's for that class. The mistakes are counted in the "
                          "confusion matrices added up over the 5 test splits (`confusion_<exp>_field.png`).\n\n" + "\n".join(lines))
    else:
        paragraphs.append("**4. Which classes collapse under W->F?** " + pending_sentence("E1-FF", "E1-WF"))
    return "\n\n".join(paragraphs)


HARDWARE_COMPARISONS = (("E1-FF", "E1-WF"), ("E1-U", "E1-FF"), ("E1-U", "E1-WW"), ("E2-cnx-U", "E1-U"), ("E2-swin-U", "E1-U"),
                        ("E2-swin-U", "E2-cnx-U"), ("E2-swin-WF", "E1-WF"), ("E3-A", "E2-swin-U"), ("E3-A-WF", "E2-swin-WF"))


def hardware_findings(results: dict, data_root) -> str:
    """Which runs were made on which hardware (from env.json), and which comparisons of the tables cross hardware. '' when no
    complete experiment has an env.json."""
    readers = {}  # run folder -> the experiment IDs that read it (E1-U reads E0-rect)
    for exp_id in REPORTED_EXPERIMENTS:
        if exp_id in results:
            readers.setdefault(results[exp_id].run_name, []).append(exp_id)
    groups = {}
    for run_name, exp_ids in readers.items():
        signature = hardware_signature(results[exp_ids[0]], data_root)
        aliases = [e for e in exp_ids if e != run_name]
        if signature:
            groups.setdefault(signature, []).append(run_name + (f" (also {', '.join(aliases)})" if aliases else ""))
    lines = [f"- {', '.join(names)}: {hardware_text(signature)}" for signature, names in groups.items()]
    if not lines:
        return ""
    text = "Hardware per run folder, read from each run's env.json:\n\n" + "\n".join(lines)
    if len(groups) > 1:
        crossing = []
        for a, b in HARDWARE_COMPARISONS:
            if have(results, a, b) and hardware_signature(results[a], data_root) != hardware_signature(results[b], data_root):
                crossing.append(f"{a} vs {b}")
        text += ("\n\nThe runs were not all made on the same hardware, torch build and precision, so a small difference between experiment "
                 "families can include hardware and numerics effects (fp16 autocast on CUDA against fp32 on the Mac, different GPUs and "
                 "torch builds), not only the method. Comparisons inside one group share their hardware. Comparisons made in the tables that "
                 "cross groups: " + (", ".join(crossing) if crossing else "none") + ". Read those gaps against the paired std. Training "
                 "times (table_runtime) are only comparable inside a group.")
    else:
        text += "\n\nAll runs share the same hardware, torch build and precision, so comparisons between experiments carry no hardware effect."
    return text


def cases_findings(rows: list, exp_id: str) -> str:
    """Counts of the T7.4 case categories for the recommended method, by domain, and where the failures concentrate."""
    total = len(rows)
    once = sum(r["tested"] == 1 for r in rows)
    by = lambda category, domain=None: [r for r in rows if r["category"] == category and (domain is None or r["domain"] == domain)]  # noqa: E731
    sentences = [f"Pooled test predictions of {exp_id} over the 5 splits cover {total} distinct images; {once} of them were in the test part of only one split."]
    names = {"success": "consistent successes (right in every split they were tested in, top probability never below "
                        f"{CASE_LOW_CONFIDENCE:g})", "failure": "consistent failures (wrong in every split they were tested in)",
             "challenging": f"challenging cases (right in some splits and wrong in others, or right but below {CASE_LOW_CONFIDENCE:g} top probability)"}
    for category in CASE_CATEGORIES:
        found = by(category)
        sentences.append(f"{len(found)} {names[category]}: {len(by(category, 'white'))} white, {len(by(category, 'field'))} field.")
    failures = by("failure")
    if failures:
        pairs = Counter((r["true"], r["modal_pred"]) for r in failures).most_common(3)
        sentences.append("Most frequent failure pairs (true -> predicted): " + "; ".join(f"{t} -> {p} ({n})" for (t, p), n in pairs) + ".")
        tested_once = sum(r["tested"] == 1 for r in failures)
        sentences.append(f"{tested_once} of the {len(failures)} failures were tested in one split only, so for them 'every time' rests on one prediction.")
    sentences.append("The per-image list is `cases.csv`; the contact sheets are `cases_success.png`, `cases_failure.png` and `cases_challenging.png`.")
    return " ".join(sentences)

FINDINGS_TITLE = (
    "# Findings\n\n"
    "Sections between `<!-- auto:NAME:begin -->` and `<!-- auto:NAME:end -->` markers are regenerated by "
    "`summarize` from the run folders. Anything outside the markers is yours and is never touched.\n"
)


def auto_block(name: str, heading: str, body: str) -> str:
    return f"<!-- auto:{name}:begin -->\n## {heading}\n\n{body.strip()}\n<!-- auto:{name}:end -->"


def update_findings_text(existing: str | None, blocks: dict) -> str:
    """Replace each auto block in ``existing`` (append the ones that are not there yet); keep everything else."""
    text = existing if existing else FINDINGS_TITLE
    for name, block in blocks.items():
        pattern = re.compile(rf"<!-- auto:{re.escape(name)}:begin -->.*?<!-- auto:{re.escape(name)}:end -->", re.DOTALL)
        if pattern.search(text):
            text = pattern.sub(lambda _match: block, text, count=1)
        else:
            text = text.rstrip("\n") + "\n\n" + block + "\n"
    return text


def g0_findings(result: dict) -> str:
    """The G0 section of findings.md in plain English, with every number taken from the gate evidence."""
    ev, value = result["evidence"], result["value"]

    def f1(mode: str) -> str:
        record = ev["candidates"][mode]["val_mixed_macro_f1"]
        return f"{record['mean']:.3f} +- {record['std']:.3f}"

    height, width = INPUT_SIZES[value]
    order = ev["ranking"]
    sentences = [
        f"Gate G0 picked the {value} input ({height}x{width}) with the rule fixed in phase 04: highest mean validation mixed "
        "macro-F1, and if the top two are within one std, prefer rect.",
        "Validation mixed macro-F1 (mean +- std over 5 splits) was " + ", ".join(f"{m} {f1(m)}" for m in order[:-1])
        + f" and {order[-1]} {f1(order[-1])}.",
    ]
    leader = order[0]
    if ev["decided_by"].startswith("within one std") and leader != value:
        sentences.append(
            f"{leader.capitalize()} leads {value} by {ev['top_two_gap']:.3f}, less than one std ({ev['tolerance_one_std']:.3f}), so {value} was "
            "preferred because it keeps the leaf geometry at no extra cost."
        )
        paired = ev["paired_differences"][f"{leader}_minus_{value}"]
        mixed, field = paired["val_mixed_macro_f1"], paired["val_field_macro_f1"]
        sentences.append(
            f"The paired {leader}-minus-{value} validation difference is {mixed['mean']:+.3f} +- {mixed['std']:.3f} on mixed and "
            f"{field['mean']:+.3f} +- {field['std']:.3f} on field macro-F1, with {leader} ahead on field in "
            f"{field['splits_ahead']} of {len(field['per_split'])} splits; this is recorded as a finding, not as a reason to revisit the choice."
        )
    else:
        sentences.append(f"{value} has the highest mean, so the tie-break clause was not needed.")
    return " ".join(sentences)


def g2_findings(result: dict) -> str:
    """The G2 section of findings.md, every number taken from the frozen evidence in choices.json."""
    ev = result["evidence"]

    def f1(method: str, key: str) -> str:
        record = ev["candidates"][method][key]
        return f"{record['mean']:.3f} +- {record['std']:.3f}"

    named = lambda m: f"{G2_METHOD_LABELS[m]} ({ev['candidates'][m]['experiment']})"  # noqa: E731
    sentences = [
        f"Gate G2 recommends {'the ' if ev['method'] == 'plain' else ''}{named(ev['method'])}, by the rule fixed in phase 06: highest mean validation mixed macro-F1; "
        "if the top two are within one std, the higher validation field macro-F1; if that is also within one std, the simpler method.",
        "Validation mixed / field macro-F1 (mean +- std over 5 splits): "
        + "; ".join(f"{named(m)} {f1(m, 'val_mixed_macro_f1')} / {f1(m, 'val_field_macro_f1')}" for m in ev["ranking"]) + ".",
    ]
    if ev["cut"]:
        sentences.append("Left out because of a cut line: " + ", ".join(f"Method {m}" for m in ev["cut"]) + ".")
    sentences.append(f"Decided by: {ev['decided_by']}.")
    for name, pair in ev["paired_differences"].items():
        a, b = name.split("_minus_")
        mixed, field = pair["val_mixed_macro_f1"], pair["val_field_macro_f1"]
        sentences.append(f"Paired {a} - {b} on validation: mixed {mixed['mean']:+.3f} +- {mixed['std']:.3f} "
                         f"({mixed['splits_ahead']} of {len(mixed['per_split'])} splits ahead), field {field['mean']:+.3f} +- {field['std']:.3f}.")
    return " ".join(sentences)


def summarize(data_root, out=print) -> None:
    """Regenerate every table, figure and findings section that the runs available so far support. Experiments that are
    incomplete or do not match the registry are skipped with a warning."""
    data_root = Path(data_root)
    choices = load_choices(data_root)
    results = load_experiments(data_root, (*ANALYSIS_EXPERIMENTS, *METHOD_EXPERIMENTS, SEGMENTER_EXPERIMENT), choices)
    optional = [exp_id for exp_id in OPTIONAL_DOMAIN_EXPERIMENTS if (runs_dir(data_root) / exp_id).is_dir()]
    results.update(load_experiments(data_root, optional, choices))
    tables = (table_input_mode(results), table_required(results, choices), table_domains(results, choices), table_methods(results, choices),
              table_segmenter(results.get(SEGMENTER_EXPERIMENT), data_root), table_per_class(results, choices),
              table_hparams(results, data_root), table_runtime(results, data_root))
    for table in tables:
        for path in write_table(data_root, table):
            out(f"summarize: wrote {path}")
    blocks = {}
    e0 = {mode: results.get(f"E0-{mode}") for mode in INPUT_MODES}
    if all(e0.values()):
        g0 = evaluate_g0(e0)
        recorded = choices.raw("input_mode")
        if recorded != g0["value"]:
            warn(f"choices.json has input_mode = {recorded!r} but the E0 runs decide {g0['value']!r}; run `gate g0`")
        blocks["g0"] = auto_block("g0", "G0 input mode", g0_findings(g0))
    else:
        warn("findings.md: G0 section skipped, the three E0 experiments are not all complete")
    recommended = choices.data.get("recommended")
    if isinstance(recommended, dict) and recommended.get("evidence"):
        blocks["g2"] = auto_block("g2", "G2 recommended method", g2_findings(recommended))
    for path in write_figures(data_root, results, choices):
        out(f"summarize: wrote {path}")
    cases = write_cases(data_root, results, choices, out)
    if any(exp_id in results for exp_id in ("E1-U", "E1-FF", "E1-WF")):
        blocks["questions"] = auto_block("questions", "Domain transfer questions (phase 04)", domain_questions_findings(results))
    if cases is not None:
        blocks["cases"] = auto_block("cases", "Success, failure and challenging cases (T7.4)", cases_findings(cases, recommended_experiment(choices)))
    hardware = hardware_findings(results, data_root)
    if hardware:
        blocks["hardware"] = auto_block("hardware", "Hardware", hardware)
    path = results_dir(data_root) / "findings.md"
    existing = read_file_bytes(path).decode("utf-8") if path.is_file() else None
    write_text_atomic(path, update_findings_text(existing, blocks))
    out(f"summarize: wrote {path}")

# ---- from 90_cli.ipynb ----
import argparse
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

DEFAULT_DATA_ROOT = "Dhan-Shomadhan"
DEVICE_CHOICES = ("auto", "cuda", "mps", "cpu")
DEFAULT_SPLITS = (0, 1, 2, 3, 4)

EXIT_OK = 0
EXIT_FAILURE = 1
EXIT_NOT_IMPLEMENTED = 3

import difflib

CHOICES_FILENAME = "choices.json"
SWEEP_LRS = (1e-4, 3e-4)  # T3.4: split-0 learning-rate sweep
# Experiment whose split-0 run is swept for each backbone (04: ResNet50 on rect, the others on their U row).
SWEEP_EXPERIMENT = {"resnet50": "E0-rect", "convnext_tiny": "E2-cnx-U", "swin_t": "E2-swin-U"}
# Used by `--fast` when choices.json does not exist yet, so that every experiment ID can be sanity-checked.
FAST_PLACEHOLDERS = {"input_mode": "rect", "backbone": "resnet50", "lr": 3e-4}
CHOICE_SOURCES = {
    "input_mode": 'the winning E0 input mode ("best of E0"), written by gate G0 (phase 04, Batch 1)',
    "backbone": 'the winning backbone ("best of E2"), written by gate G1 (phase 04, Batch 3)',
    "lr": "the learning rate of this backbone, written by `choose-lr --backbone NAME` after the split-0 sweep "
    "(`run --exp <ID> --sweep-lr`)",
    "composite_n_factor": "the composites per epoch of Method A (x the white training count), written by `choose-composites` "
    "after the split-0 comparison (`run --exp E3-A --sweep-composites`)",
    "recommended": "the recommended method's experiment ID (plain G1 unified row, E3-A or E4-B), written and frozen by gate G2 "
    "(`gate g2`, phase 06)",
}


def choices_path(data_root) -> Path:
    return results_dir(data_root) / CHOICES_FILENAME


@dataclass(frozen=True)
class Choices:
    """The contents of choices.json plus its path (for error messages)."""

    path: Path
    data: dict

    def raw(self, key: str, sub: str | None = None):
        entry = self.data.get(key)
        if sub is not None:
            entry = entry.get(sub) if isinstance(entry, dict) else None
        if isinstance(entry, dict) and "value" in entry:
            entry = entry["value"]
        return entry

    def get(self, key: str, sub: str | None = None):
        """The validated choice, or ChoicesError that says which step writes it."""
        value = self.raw(key, sub)
        label = key if sub is None else f"{key}[{sub}]"
        if value is None:
            where = f"{self.path} does not exist" if not self.path.is_file() else f"{self.path} has no such entry"
            raise ChoicesError(f"{where} (needed: {label}). It holds {CHOICE_SOURCES[key]}. Schema: see 90_cli.ipynb.")
        valid = {
            "input_mode": lambda v: v in INPUT_MODES,
            "backbone": lambda v: v in BACKBONES,
            "lr": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool) and 0 < v < 1,
            "composite_n_factor": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool) and float(v) in COMPOSITE_N_FACTORS,
            "recommended": lambda v: v in EXPERIMENTS,
        }[key]
        if not valid(value):
            options = {"input_mode": INPUT_MODES, "backbone": BACKBONES, "lr": "a number in (0, 1)",
                       "composite_n_factor": f"one of {COMPOSITE_N_FACTORS}", "recommended": "an experiment ID"}[key]
            raise ChoicesError(f"{self.path}: invalid {label} = {value!r} (expected {options})")
        return float(value) if key in ("lr", "composite_n_factor") else value


def load_choices(data_root) -> Choices:
    path = choices_path(data_root)
    if not path.is_file():
        return Choices(path, {})
    try:
        data = json.loads(read_file_bytes(path).decode("utf-8"))
    except ValueError as exc:
        raise ChoicesError(f"{path} is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ChoicesError(f"{path}: expected a JSON object at the top level")
    return Choices(path, data)


def write_choice(data_root, key: str, value, evidence=None, *, sub: str | None = None) -> Path:
    """Set choices[key] (or choices[key][sub]) to {"value": value, "evidence": evidence}, keeping the rest."""
    choices = load_choices(data_root)
    data = dict(choices.data)
    entry = {"value": value, "evidence": evidence if evidence is not None else {}}
    if sub is None:
        data[key] = entry
    else:
        group = dict(data[key]) if isinstance(data.get(key), dict) else {}
        group[sub] = entry
        data[key] = group
    write_json(choices.path, data, indent=2)
    return choices.path


def _row(exp_id: str, backbone, train, test_subsets, **kwargs) -> ExperimentConfig:
    train = tuple(train)
    return ExperimentConfig(
        exp_id=exp_id,
        backbone=backbone,
        train_domains=train,
        select_domains=train,
        test_subsets=tuple(test_subsets),
        input_mode=kwargs.pop("input_mode", None),
        **kwargs,
    )


_U, _W, _F = DOMAINS, ("white",), ("field",)
_ALL3 = ("white", "field", "mixed")
_WF_TEST = ("field", "white")  # field is the main result of a W->F row, white the reference

_ROWS = (
    # E0: input-size ablation, ResNet50 on white + field, equal pixel budget.
    _row("E0-squash", "resnet50", _U, _ALL3, input_mode="squash", note="320x320, aspect distorted"),
    _row("E0-pad", "resnet50", _U, _ALL3, input_mode="pad", note="320x320 letterbox"),
    _row("E0-rect", "resnet50", _U, _ALL3, input_mode="rect", note="448x224 (HxW)"),
    # E1: ResNet50 baseline and domain experiments at the winning E0 input mode.
    _row("E1-U", "resnet50", _U, _ALL3, alias_of_winner="E0", note="alias of the winning E0 row, no retraining"),
    _row("E1-WW", "resnet50", _W, ("white",), note="train white, test white"),
    _row("E1-FF", "resnet50", _F, ("field",), note="train field, test field"),
    _row("E1-WF", "resnet50", _W, _WF_TEST, note="train white, test field (cross-domain)"),
    # E2: ConvNeXt-T and Swin-T.
    _row("E2-cnx-U", "convnext_tiny", _U, _ALL3),
    _row("E2-cnx-WF", "convnext_tiny", _W, _WF_TEST),
    _row("E2-swin-U", "swin_t", _U, _ALL3),
    _row("E2-swin-WF", "swin_t", _W, _WF_TEST),
    # Later phases: runnable only once their hooks exist.
    _row("E3-A", None, _U, _ALL3, use_composites=True, note="Method A (phase 05): composites as extra training samples"),
    _row("E3-A-WF", None, _W, _WF_TEST, use_composites=True, note="white + composites; field images are only backgrounds"),
    _row("S-seg", "lraspp_mobilenet_v3_large", _U, (), kind="segmenter", epochs=SEG_EPOCHS, lr=SEG_LR, weight_decay=SEG_WEIGHT_DECAY,
         batch_size=SEG_BATCH_SIZE, stage1_epochs=0, warmup_epochs=0, label_smoothing=0.0, dropout=0.0, clip_norm=0.0, patience=0,
         note="leaf segmenter (phase 06): LRASPP-MobileNetV3, composites + white pseudo-masks, 512x256"),
    _row("E4-B", None, _U, _ALL3, seg_crop=True, note="Method B (phase 06): crop to the S-seg box (stored boxes.json), classify"),
    _row("X-domain-WW", None, _W, ("white",), note="best backbone, train white, test white"),
    _row("X-domain-FF", None, _F, ("field",), note="best backbone, train field, test field"),
    _row("X-gradcam", None, _U, (), kind="analysis", note="Grad-CAM shortcut analysis (phase 07), see the gradcam command"),
)
EXPERIMENTS: dict[str, ExperimentConfig] = {row.exp_id: row for row in _ROWS}
# `run --exp <GROUP>` runs every member in order.
EXPERIMENT_GROUPS = {
    "E0": ("E0-squash", "E0-pad", "E0-rect"),
    "E1": ("E1-U", "E1-WW", "E1-FF", "E1-WF"),
    "E2": ("E2-cnx-U", "E2-cnx-WF", "E2-swin-U", "E2-swin-WF"),
    "X-domain": ("X-domain-WW", "X-domain-FF"),
}
# Rows that are the same training as another row (same data, selection domains, backbone, input mode, lr and
# switches; they differ only in which test subset the report highlights). They have no run folder of their own:
# like E1-U they resolve to the target's config and folder, so nothing is trained twice. Aliases do not change
# any ExperimentConfig, so no existing fingerprint moves.
#   E1-WW: train white, select on white, same as E1-WF (whose metrics also hold the white test as reference).
FIXED_ALIASES = {"E1-WW": "E1-WF"}
#   X-domain-WW (best backbone, train white): the W->F row of the winning backbone is the same training.
#   X-domain-FF has no counterpart for ConvNeXt-T / Swin-T (there is no E2 F->F row), so it is not aliased.
BACKBONE_ALIASES = {"X-domain-WW": {"resnet50": "E1-WF", "convnext_tiny": "E2-cnx-WF", "swin_t": "E2-swin-WF"}}
NON_CLASSIFIER_MESSAGE = {
    "segmenter": "is the leaf segmenter, run with `run --exp S-seg` (it is not a classifier)",
    "analysis": "is a Grad-CAM analysis, produced by the `gradcam` command of phase 07 (07-analysis.md)",
}


def run_folder_name(exp_id: str, choices: Choices) -> str:
    """Folder (under runs/) that holds the results of an experiment ID: itself, except for the E1-U alias."""
    if exp_id not in EXPERIMENTS:
        expand_experiment_ids(exp_id)  # raises with suggestions
    if exp_id in FIXED_ALIASES:
        return run_folder_name(FIXED_ALIASES[exp_id], choices)
    if exp_id in BACKBONE_ALIASES:
        return run_folder_name(BACKBONE_ALIASES[exp_id][choices.get("backbone")], choices)
    base = EXPERIMENTS[exp_id]
    return f"{base.alias_of_winner}-{choices.get('input_mode')}" if base.alias_of_winner else exp_id


def expand_experiment_ids(text: str) -> list[str]:
    """'E0' -> its three rows; 'E1-U,E1-WW' -> two rows. Unknown IDs raise UnknownExperimentError."""
    ids: list[str] = []
    for part in (p.strip() for p in text.split(",") if p.strip()):
        for exp_id in EXPERIMENT_GROUPS.get(part, (part,)):
            if exp_id not in EXPERIMENTS:
                close = difflib.get_close_matches(exp_id, [*EXPERIMENTS, *EXPERIMENT_GROUPS], n=3)
                hint = f" Did you mean: {', '.join(close)}?" if close else ""
                raise UnknownExperimentError(
                    f"unknown experiment {exp_id!r}.{hint} Known: {', '.join([*EXPERIMENTS, *EXPERIMENT_GROUPS])}"
                )
            if exp_id not in ids:
                ids.append(exp_id)
    if not ids:
        raise UnknownExperimentError("no experiment ID given")
    return ids


@dataclass(frozen=True)
class ResolvedExperiment:
    config: ExperimentConfig  # fully concrete: backbone, input_mode and lr are set
    requested: str  # the ID that was asked for (differs from config.exp_id for the E1-U alias)
    choices_used: dict  # which values came from choices.json (or FAST placeholders), for config.json
    notes: tuple[str, ...] = ()
    composite_factor: float | None = None  # Method A rows: composites per epoch x the white training count; else None


def resolve_experiment(
    exp_id: str, choices: Choices, *, lr: float | None = None, placeholders: bool = False,
    composite_factor: float | None = None,
) -> ResolvedExperiment:
    """Turn a registry entry into a concrete config.

    ``lr`` overrides the choices.json learning rate (sweeps, ``--lr``). ``placeholders=True`` (``--fast``)
    substitutes FAST_PLACEHOLDERS for choices that do not exist yet, and says so in ``notes``. ``composite_factor``
    overrides the chosen composites-per-epoch factor of Method A rows (the split-0 comparison); without it
    `composite_n_factor` of choices.json is used, and the default 1x when `choose-composites` has not run yet.
    """
    if exp_id not in EXPERIMENTS:
        expand_experiment_ids(exp_id)  # raises with a helpful message
    base = EXPERIMENTS[exp_id]
    if base.kind == "segmenter":  # needs no choice: the architecture, lr and recipe are fixed in the registry row
        return ResolvedExperiment(base, exp_id, {}, ())
    if base.kind != "classifier":
        raise NotReadyError(f"{exp_id} {NON_CLASSIFIER_MESSAGE[base.kind]}; it cannot be run as a classifier")
    used: dict = {}
    notes: list[str] = []

    def pick(key: str, sub: str | None = None):
        label = key if sub is None else f"{key}[{sub}]"
        try:
            value = choices.get(key, sub)
            used[label] = value
            return value
        except ChoicesError as exc:
            if not placeholders:
                raise ChoicesError(f"{exp_id}: {exc}") from None
            value = FAST_PLACEHOLDERS[key]
            used[label] = value
            notes.append(f"--fast: no choice for {label}, using the placeholder {value!r}")
            return value

    if exp_id in FIXED_ALIASES or exp_id in BACKBONE_ALIASES:
        target = FIXED_ALIASES[exp_id] if exp_id in FIXED_ALIASES else BACKBONE_ALIASES[exp_id][pick("backbone")]
        inner = resolve_experiment(target, choices, lr=lr, placeholders=placeholders, composite_factor=composite_factor)
        note = f"{exp_id} is an alias of {inner.config.exp_id} (identical training): same run folder, no retraining"
        return ResolvedExperiment(inner.config, exp_id, {**inner.choices_used, **used}, (note, *inner.notes, *notes),
                                  inner.composite_factor)

    if base.alias_of_winner:
        mode = pick("input_mode")
        inner = resolve_experiment(f"{base.alias_of_winner}-{mode}", choices, lr=lr, placeholders=placeholders)
        note = f"{exp_id} is an alias of {inner.config.exp_id} (the winning input mode): same run folder, no retraining"
        return ResolvedExperiment(inner.config, exp_id, {**inner.choices_used, **used}, (note, *inner.notes, *notes),
                                  inner.composite_factor)

    backbone = base.backbone if base.backbone is not None else pick("backbone")
    mode = base.input_mode if base.input_mode is not None else pick("input_mode")
    if lr is None:
        lr = base.lr if base.lr is not None else pick("lr", backbone)
    config = replace(base, backbone=backbone, input_mode=mode, lr=lr)
    factor = None
    if config.use_composites:
        if composite_factor is not None:
            factor, used["composite_n_factor"] = float(composite_factor), float(composite_factor)
        elif choices.raw("composite_n_factor") is not None:
            factor = choices.get("composite_n_factor")
            used["composite_n_factor"] = factor
        else:
            factor = COMPOSITE_DEFAULT_FACTOR
            used["composite_n_factor"] = factor
            notes.append(f"composite_n_factor is not chosen yet (`choose-composites`): using the default {COMPOSITE_DEFAULT_FACTOR:g}x")
    return ResolvedExperiment(config, exp_id, used, tuple(notes), factor)

def cmd_download_weights(args: argparse.Namespace) -> int:
    try:
        download_weights(Path(args.data_root))
    except (ExperimentError, OSError) as exc:
        print(f"download-weights: FAIL - {exc}", file=sys.stderr)
        return EXIT_FAILURE
    return EXIT_OK

FAST_CONFIG = {"stage1_epochs": 1, "epochs": 1, "size_div": 4, "batch_size": 8}
FAST_IMAGES = 24


def pretrained_available(backbone: str, data_root) -> bool:
    """True if the pretrained file is already stored under <data_root>/_work/weights (no download is triggered)."""
    previous = os.environ.get("TORCH_HOME")
    try:
        set_torch_home(data_root, create=False)
        weights = backbone_weights(backbone) if backbone in BACKBONE_SPECS else torchvision.models.get_weight(SEG_ARCHITECTURES[backbone])
        return weight_file_ok(weight_checkpoint_path(weights))
    finally:
        if previous is None:
            os.environ.pop("TORCH_HOME", None)
        else:
            os.environ["TORCH_HOME"] = previous


def run_destination(data_root, args, cfg: ExperimentConfig, dev: bool, composite_factor: float | None = None) -> tuple[Path, str]:
    """(root folder, run name) for one resolved config; see the table in the notebook."""
    sweep_composites = getattr(args, "sweep_composites", False)
    if args.out_dir:
        root = Path(args.out_dir)
    elif dev:
        root = scratch_dir(data_root)
    else:
        root = sweep_dir(data_root) if args.sweep_lr or sweep_composites else runs_dir(data_root)
    if args.sweep_lr:
        return root, sweep_run_name(cfg.exp_id, cfg.lr)
    if sweep_composites:
        return root, composite_sweep_run_name(cfg.exp_id, composite_factor)
    suffix = "" if args.out_dir or not dev else "_fast" if args.fast else "_dev"
    return root, cfg.exp_id + suffix


def apply_run_flags(args, resolved: ResolvedExperiment, data_root) -> tuple[ResolvedExperiment, dict, int | None]:
    """Apply --fast and the dev/system overrides to a resolved experiment. Returns (resolved, overrides, limit)."""
    changes: dict = {}
    overrides: dict = {}
    limit = None
    if args.fast:
        changes.update(FAST_CONFIG)
        changes["pretrained"] = pretrained_available(getattr(args, "seg_arch", None) or resolved.config.backbone, data_root)
        overrides["fast"] = True
        limit = FAST_IMAGES
    for flag, field_name in (("epochs", "epochs"), ("stage1_epochs", "stage1_epochs"), ("lr", "lr")):
        value = getattr(args, flag, None)
        if value is not None:
            changes[field_name] = value
            overrides[flag] = value
    seg_arch = getattr(args, "seg_arch", None)
    if seg_arch is not None:
        if resolved.config.kind != "segmenter":
            raise ExperimentError(f"--seg-arch only applies to the segmenter (S-seg), not {resolved.requested}")
        changes["backbone"] = seg_arch
        overrides["seg_arch"] = seg_arch
    for flag in ("batch_size", "grad_accum"):
        value = getattr(args, flag, None)
        if value is not None:
            changes[flag] = value
    notes = resolved.notes
    if args.fast and not changes["pretrained"]:
        notes = (*notes, f"--fast: {resolved.config.backbone} weights are not downloaded, using random initialisation")
    return replace(resolved, config=replace(resolved.config, **changes), notes=notes), overrides, limit


def run_command(args) -> int:
    data_root = Path(args.data_root)
    choices = load_choices(data_root)
    device = resolve_device(args.device)
    ids = expand_experiment_ids(args.exp)
    sweep = args.sweep_lr
    sweep_composites = getattr(args, "sweep_composites", False)
    if sweep and sweep_composites:
        raise ExperimentError("--sweep-lr and --sweep-composites are two different sweeps; run them one at a time")
    if sweep and args.lr is not None:
        raise ExperimentError("--sweep-lr already sets the learning rates (1e-4 and 3e-4); do not combine it with --lr")
    if sweep_composites and ids != [COMPOSITE_SWEEP_EXPERIMENT]:
        raise ExperimentError(f"--sweep-composites compares the composites per epoch of {COMPOSITE_SWEEP_EXPERIMENT}: use --exp {COMPOSITE_SWEEP_EXPERIMENT}")
    splits = (0,) if sweep or sweep_composites else tuple(args.splits)
    if (sweep or sweep_composites) and tuple(args.splits) != DEFAULT_SPLITS and tuple(args.splits) != (0,):
        print("run: note - the sweeps always use split 0 only")
    dev = bool(args.fast or args.lr is not None or args.epochs is not None or args.stage1_epochs is not None
               or getattr(args, "seg_arch", None) is not None)
    options_base = dict(device=device, seed_offset=args.seed_offset, num_workers=args.num_workers, force=args.force,
                        weights_root=data_root, seg_dir=getattr(args, "seg_dir", None))
    weights_home = set_torch_home(data_root)
    print(f"run: device {device}, data root {data_root}, TORCH_HOME {weights_home}")
    summary, seg_summary = [], []
    for exp_id in ids:
        if sweep:
            variants = [(lr, None) for lr in SWEEP_LRS]  # (learning rate, composites factor) of each run
        elif sweep_composites:
            variants = [(None, f) for f in COMPOSITE_N_FACTORS]
        else:
            variants = [(None, None)]
        for sweep_lr, factor in variants:
            resolved = resolve_experiment(exp_id, choices, lr=sweep_lr if sweep else args.lr, placeholders=args.fast,
                                          composite_factor=factor)
            resolved, overrides, limit = apply_run_flags(args, resolved, data_root)
            cfg = resolved.config
            if sweep and cfg.exp_id != SWEEP_EXPERIMENT.get(cfg.backbone):
                print(f"run: note - choose-lr reads the sweep of {SWEEP_EXPERIMENT.get(cfg.backbone)} for {cfg.backbone}, not {cfg.exp_id}")
            root, name = run_destination(data_root, args, cfg, dev, resolved.composite_factor)
            for note in resolved.notes:
                print(f"run: {note}")
            print(f"run: {resolved.requested} -> {root / name}/split_<k>/"
                  + ("  (sweep, never a result)" if sweep or sweep_composites else "  (scratch, never a result)" if dev else ""))
            options = RunOptions(limit=limit, overrides=tuple(overrides.items()), **options_base)
            for split_seed in splits:
                runner = run_seg_split if cfg.kind == "segmenter" else run_split
                result = runner(resolved, split_seed, data_root=data_root, out_dir=split_dir(root / name, split_seed),
                                options=options, log=lambda text: print(text, flush=True))
                metrics = result["metrics"]
                if cfg.kind == "segmenter":
                    seg_summary.append((name, split_seed, result["status"], metrics["val_iou_composite"], metrics["val_iou_white"]))
                else:
                    summary.append((name, split_seed, result["status"], metrics["val"]["mixed"]["macro_f1"], metrics["test"]["mixed"]["macro_f1"]))
    if summary:
        print("run: summary (macro-F1)")
        print(f"  {'run':<22}{'split':>5}  {'status':<8}{'val mixed':>10}{'test mixed':>11}")
        for name, split_seed, status, val_f1, test_f1 in summary:
            print(f"  {name:<22}{split_seed:>5}  {status:<8}{fmt3(val_f1):>10}{fmt3(test_f1):>11}")
    if seg_summary:
        print("run: summary (segmenter, IoU on validation images)")
        print(f"  {'run':<22}{'split':>5}  {'status':<8}{'composites':>11}{'white':>8}")
        for name, split_seed, status, composite_iou, white_iou in seg_summary:
            print(f"  {name:<22}{split_seed:>5}  {status:<8}{fmt3(composite_iou):>11}{fmt3(white_iou):>8}")
    return EXIT_OK


def cmd_run(args: argparse.Namespace) -> int:
    try:
        return run_command(args)
    except (ExperimentError, DatasetError) as exc:
        print(f"run: FAIL - {exc}", file=sys.stderr)
        return EXIT_FAILURE


def choose_lr(data_root, backbone: str, out=print) -> dict:
    """T3.4 rule: of the two split-0 sweep runs, take the lr with the higher validation mixed macro-F1."""
    if backbone not in SWEEP_EXPERIMENT:
        raise ExperimentError(f"unknown backbone {backbone!r}, expected one of {', '.join(SWEEP_EXPERIMENT)}")
    exp_id = SWEEP_EXPERIMENT[backbone]
    scores, shas = {}, set()
    for lr in SWEEP_LRS:
        run_dir = split_dir(sweep_dir(data_root) / sweep_run_name(exp_id, lr), 0)
        metrics = read_metrics(run_dir)
        if metrics is None:
            raise ExperimentError(f"missing sweep result {run_dir / 'metrics.json'}; run `run --exp {exp_id} --sweep-lr` first")
        if metrics.get("fast") or metrics.get("overrides"):
            raise ExperimentError(f"{run_dir} is a --fast / dev-override run, not a real sweep run; re-run the sweep without those flags")
        if metrics.get("backbone") != backbone or abs(metrics.get("lr", -1) - lr) > 1e-12:
            raise ExperimentError(f"{run_dir}: expected backbone {backbone} at lr {lr}, found {metrics.get('backbone')} at {metrics.get('lr')}")
        scores[lr] = metrics["val"]["mixed"]["macro_f1"]
        shas.add(metrics["split_sha256"])
    if len(shas) != 1:
        raise ExperimentError("the two sweep runs used different splits; re-run both")
    best = max(SWEEP_LRS, key=lambda lr: (scores[lr], -lr))  # ties: the smaller lr
    evidence = {
        "experiment": exp_id, "split": 0, "split_sha256": shas.pop(),
        "val_mixed_macro_f1": {lr_tag(lr): scores[lr] for lr in SWEEP_LRS},
        "rule": "higher validation mixed macro-F1 on split 0; ties go to the smaller lr",
    }
    path = write_choice(data_root, "lr", best, evidence, sub=backbone)
    out(f"choose-lr: {backbone}: " + ", ".join(f"lr {lr_tag(lr)} -> val mixed F1 {fmt3(scores[lr])}" for lr in SWEEP_LRS)
        + f"  =>  lr {lr_tag(best)}  (written to {path})")
    try:
        reuse = reuse_sweep_run(data_root, backbone, best)
        message = {
            "copied": f"the sweep run at lr {lr_tag(best)} was copied to split 0 of {run_folder_name(exp_id, load_choices(data_root))} "
            "(same training; the real run will skip split 0)",
            "exists": "the real split 0 already exists and was left untouched",
        }[reuse]
    except (ExperimentError, DatasetError) as exc:
        reuse, message = "not reused", f"sweep run not reused for split 0 ({exc}); the real run will train it"
    out(f"choose-lr: {message}")
    return {"lr": best, "evidence": evidence, "split_0": reuse}


PROVENANCE_FILENAME = "provenance.json"


def reuse_sweep_run(data_root, backbone: str, lr: float) -> str:
    """Copy the sweep run at ``lr`` to split 0 of the real run folder of the backbone's sweep experiment.

    Returns "copied" or "exists" (a real split 0 is already there and is left untouched). Raises ExperimentError
    when the sweep run is not the same training as the real run: different config fingerprint (including a changed
    lr in choices.json), different split sha256, or a --fast / dev-override run."""
    data_root = Path(data_root)
    exp_id = SWEEP_EXPERIMENT[backbone]
    choices = load_choices(data_root)
    sweep_split = split_dir(sweep_dir(data_root) / sweep_run_name(exp_id, lr), 0)
    metrics = read_metrics(sweep_split)
    if metrics is None:
        raise ExperimentError(f"no sweep result at {sweep_split / 'metrics.json'}")
    if metrics.get("fast") or metrics.get("overrides"):
        raise ExperimentError(f"{sweep_split} is a --fast / dev-override run")
    resolved = resolve_experiment(exp_id, choices)  # the config a real run would use, with the lr now in choices.json
    expected = config_fingerprint(resolved.config, {"seed_offset": 0, "limit": None})
    if metrics.get("config_fingerprint") != expected:
        raise ExperimentError(
            f"the sweep run's config fingerprint differs from the real {resolved.config.exp_id} run "
            f"(lr in choices.json is {resolved.config.lr:g}, the sweep run used {metrics.get('lr')}, or the recipe changed)"
        )
    if metrics.get("split_sha256") != load_split(data_root, 0)["sha256"]:
        raise ExperimentError("the sweep run's split sha256 differs from the committed split_0")
    real_root = runs_dir(data_root) / run_folder_name(exp_id, choices)
    destination = split_dir(real_root, 0)
    if destination.exists() and any(destination.iterdir()):
        return "exists"
    provenance = {
        "copied_from": "/".join(sweep_split.relative_to(runs_dir(data_root)).parts),
        "reason": "choose-lr: the sweep run at the chosen lr is the same training as split 0 of this run "
        "(identical config fingerprint and split sha256), so it was copied instead of retrained",
        "config_fingerprint": expected, "split_sha256": metrics["split_sha256"], "lr": lr,
    }
    staging = destination.with_name(destination.name + f".tmp{os.getpid()}")
    if staging.exists():
        shutil.rmtree(staging)
    shutil.copytree(sweep_split, staging)
    write_json(staging / PROVENANCE_FILENAME, provenance, indent=2)
    if destination.exists():  # empty leftover folder
        destination.rmdir()
    os.replace(staging, destination)
    return "copied"


COMPOSITE_SWEEP_EXPERIMENT = "E3-A"


def read_composite_sweep(data_root) -> tuple[dict, str]:
    """({factor: metrics of the split-0 sweep run}, split sha256). Refuses missing, --fast / dev, mismatching runs."""
    runs, shas = {}, set()
    for factor in COMPOSITE_N_FACTORS:
        run_dir = split_dir(sweep_dir(data_root) / composite_sweep_run_name(COMPOSITE_SWEEP_EXPERIMENT, factor), 0)
        metrics = read_metrics(run_dir)
        if metrics is None:
            raise ExperimentError(
                f"missing sweep result {run_dir / 'metrics.json'}; run `run --exp {COMPOSITE_SWEEP_EXPERIMENT} --sweep-composites` first")
        if metrics.get("fast") or metrics.get("overrides"):
            raise ExperimentError(f"{run_dir} is a --fast / dev-override run, not a real sweep run; re-run the sweep without those flags")
        used = (metrics.get("composites") or {}).get("n_factor")
        if used is None or abs(used - factor) > 1e-12:
            raise ExperimentError(f"{run_dir}: expected composites per epoch factor {factor:g}, found {used}")
        runs[factor] = metrics
        shas.add(metrics["split_sha256"])
    if len(shas) != 1:
        raise ExperimentError("the two composite sweep runs used different splits; re-run both")
    return runs, shas.pop()


def reuse_composite_sweep_run(data_root, factor: float) -> str:
    """Copy the sweep run at ``factor`` to split 0 of `_work/runs/E3-A/` ("copied", or "exists" when a real split 0 is
    there). ExperimentError when it is not the same training: other config fingerprint (recipe, backbone, lr, factor
    changed since) or other split."""
    data_root = Path(data_root)
    choices = load_choices(data_root)
    sweep_split = split_dir(sweep_dir(data_root) / composite_sweep_run_name(COMPOSITE_SWEEP_EXPERIMENT, factor), 0)
    metrics = read_metrics(sweep_split)
    resolved = resolve_experiment(COMPOSITE_SWEEP_EXPERIMENT, choices)  # with the factor now in choices.json
    expected = config_fingerprint(resolved.config, {"seed_offset": 0, "limit": None,
                                                    **composite_fingerprint_extra(resolved.config, resolved.composite_factor)})
    if metrics is None or metrics.get("config_fingerprint") != expected:
        raise ExperimentError(
            "the sweep run's config fingerprint differs from the real E3-A run (the recipe, backbone or lr changed since the sweep)")
    if metrics.get("split_sha256") != load_split(data_root, 0)["sha256"]:
        raise ExperimentError("the sweep run's split sha256 differs from the committed split_0")
    destination = split_dir(runs_dir(data_root) / run_folder_name(COMPOSITE_SWEEP_EXPERIMENT, choices), 0)
    if destination.exists() and any(destination.iterdir()):
        return "exists"
    provenance = {
        "copied_from": "/".join(sweep_split.relative_to(runs_dir(data_root)).parts),
        "reason": "choose-composites: the sweep run at the chosen composites-per-epoch factor is the same training as split 0 "
        "of this run (identical config fingerprint and split sha256), so it was copied instead of retrained",
        "config_fingerprint": expected, "split_sha256": metrics["split_sha256"], "n_factor": factor,
    }
    staging = destination.with_name(destination.name + f".tmp{os.getpid()}")
    if staging.exists():
        shutil.rmtree(staging)
    shutil.copytree(sweep_split, staging)
    write_json(staging / PROVENANCE_FILENAME, provenance, indent=2)
    if destination.exists():
        destination.rmdir()
    os.replace(staging, destination)
    return "copied"


def choose_composites(data_root, out=print) -> dict:
    """T5.3 rule: of the two split-0 sweep runs of E3-A (0.5x and 1x white-train count composites per epoch), take the
    factor with the higher **validation** mixed macro-F1; a tie goes to 1x, the default. Records it in choices.json."""
    runs, sha = read_composite_sweep(data_root)
    scores = {f: runs[f]["val"]["mixed"]["macro_f1"] for f in COMPOSITE_N_FACTORS}
    best = max(COMPOSITE_N_FACTORS, key=lambda f: (scores[f], f == COMPOSITE_DEFAULT_FACTOR))
    evidence = {
        "experiment": COMPOSITE_SWEEP_EXPERIMENT, "split": 0, "split_sha256": sha,
        "val_mixed_macro_f1": {composite_factor_tag(f): scores[f] for f in COMPOSITE_N_FACTORS},
        "n_per_epoch": {composite_factor_tag(f): runs[f]["composites"]["n_per_epoch"] for f in COMPOSITE_N_FACTORS},
        "rule": "higher validation mixed macro-F1 on split 0; a tie goes to 1x (the default)",
    }
    path = write_choice(data_root, "composite_n_factor", best, evidence)
    out("choose-composites: " + ", ".join(f"{composite_factor_tag(f)}x -> val mixed F1 {fmt3(scores[f])}" for f in COMPOSITE_N_FACTORS)
        + f"  =>  {composite_factor_tag(best)}x  (written to {path})")
    try:
        reuse = reuse_composite_sweep_run(data_root, best)
        message = {
            "copied": f"the sweep run at {composite_factor_tag(best)}x was copied to split 0 of E3-A (same training; the real run will skip split 0)",
            "exists": "the real split 0 already exists and was left untouched",
        }[reuse]
    except (ExperimentError, DatasetError) as exc:
        reuse, message = "not reused", f"sweep run not reused for split 0 ({exc}); the real run will train it"
    out(f"choose-composites: {message}")
    return {"n_factor": best, "evidence": evidence, "split_0": reuse}


def cmd_choose_composites(args: argparse.Namespace) -> int:
    try:
        choose_composites(Path(args.data_root))
    except (ExperimentError, DatasetError) as exc:
        print(f"choose-composites: FAIL - {exc}", file=sys.stderr)
        return EXIT_FAILURE
    return EXIT_OK


def cmd_choose_lr(args: argparse.Namespace) -> int:
    try:
        choose_lr(Path(args.data_root), args.backbone)
    except (ExperimentError, DatasetError) as exc:
        print(f"choose-lr: FAIL - {exc}", file=sys.stderr)
        return EXIT_FAILURE
    return EXIT_OK

def cmd_predict(args: argparse.Namespace) -> int:
    data_root = Path(args.data_root)
    try:
        if args.run_dir is not None:
            run_dir = Path(args.run_dir)
        else:
            choices = load_choices(data_root)
            exp_id = args.exp or choices.raw("recommended")
            if not exp_id:
                raise ExperimentError(
                    f"no --exp given and {choices.path} has no 'recommended' experiment (written by gate G2, phase 06). "
                    "Pass --exp ID, for example --exp E1-U, or --run-dir PATH"
                )
            run_dir = split_dir(runs_dir(data_root) / run_folder_name(exp_id, choices), args.split)
        if not Path(args.image).is_file():
            raise ExperimentError(f"image {args.image} does not exist")
        predict_image(run_dir, args.image, resolve_device(args.device), data_root, seg_dir=args.seg_dir)
    except (ExperimentError, DatasetError) as exc:
        print(f"predict: FAIL - {exc}", file=sys.stderr)
        return EXIT_FAILURE
    return EXIT_OK

def cmd_gate(args: argparse.Namespace) -> int:
    try:
        run_gate(Path(args.data_root), args.gate, cut=tuple(args.cut or ()), force=args.force)
    except (ExperimentError, DatasetError) as exc:
        print(f"gate {args.gate}: FAIL - {exc}", file=sys.stderr)
        return EXIT_FAILURE
    return EXIT_OK


def cmd_summarize(args: argparse.Namespace) -> int:
    try:
        summarize(Path(args.data_root))
    except (ExperimentError, DatasetError) as exc:
        print(f"summarize: FAIL - {exc}", file=sys.stderr)
        return EXIT_FAILURE
    return EXIT_OK


def cmd_benchmark(args: argparse.Namespace) -> int:
    try:
        run_benchmark(Path(args.data_root), resolve_device(args.device))
    except (ExperimentError, DatasetError, RuntimeError) as exc:
        print(f"benchmark: FAIL - {exc}", file=sys.stderr)
        return EXIT_FAILURE
    return EXIT_OK

def resolve_device(requested: str = "auto") -> str:
    """Map the --device flag to a concrete torch device name; raise if it is unavailable."""
    import torch

    available = {
        "cuda": torch.cuda.is_available(),
        "mps": torch.backends.mps.is_available(),
        "cpu": True,
    }
    if requested == "auto":
        return next(name for name in ("cuda", "mps", "cpu") if available[name])
    if not available.get(requested, False):
        raise RuntimeError(f"device {requested!r} was requested but is not available here")
    return requested

def cmd_prepare(args: argparse.Namespace) -> int:
    """Index, cache, near-duplicate audit, splits, tables and figures (phase 02), then the white pseudo-masks and QC sheets
    (T5.1), the composite figures (T5.2) and the annotation selection (T6.1).
    Idempotent."""
    started = time.time()
    try:
        data_root = Path(args.data_root)
        prepare_data(data_root, workers=args.workers)
        records = load_index(data_root)
        prepare_pseudo_masks(data_root, records, workers=args.workers)
        prepare_composites(data_root, records)
        prepare_annotations(data_root, records)
    except DatasetError as exc:
        print(f"prepare: FAIL - {exc}", file=sys.stderr)
        return EXIT_FAILURE
    print(f"prepare: done in {time.time() - started:.0f} s")  # the last line: every step above has finished
    return EXIT_OK


def smoke_split(selected: list[Record], seed: int = 0) -> dict:
    """A deterministic tiny split of the smoke images: every class x domain stratum contributes to train, and
    val / test get the other members alternately (the real splits need >= 7 images per stratum, the smoke
    images have ~2)."""
    parts: dict[str, list[str]] = {"train": [], "val": [], "test": []}
    by_stratum: dict = {}
    for record in sorted(selected, key=lambda r: r.filename):
        by_stratum.setdefault(record.stratum, []).append(record.filename)
    for (cls, domain), names in by_stratum.items():
        even = (CLASS_NAMES.index(cls) + DOMAINS.index(domain)) % 2 == 0
        cycle = ("train", "val" if even else "test", "test" if even else "val", "train")
        for k, name in enumerate(names):
            parts[cycle[k % 4]].append(name)
    train, val, test = (sorted(parts[key]) for key in ("train", "val", "test"))
    return {"seed": seed, "train": train, "val": val, "test": test, "sha256": split_sha256(seed, train, val, test)}


def classifier_smoke(data_root, tmp_root, selected: list[Record], log=print) -> None:
    """One tiny experiment (E0-rect, ResNet50, 1 epoch per stage, input size / 4) through the real `run` code
    path on CPU, with a complete run folder written under ``tmp_root``; then `predict` on one image of it."""
    started = time.time()
    write_index(tmp_root, selected)
    split = smoke_split(selected)
    smoke_require(all(split[k] for k in ("train", "val", "test")), "tiny split has an empty part")
    write_json(split_path(tmp_root, 0), split)
    resolved = resolve_experiment("E0-rect", Choices(choices_path(tmp_root), {}), lr=3e-4)
    pretrained = pretrained_available(resolved.config.backbone, data_root)
    resolved = replace(resolved, config=replace(resolved.config, pretrained=pretrained, **FAST_CONFIG))
    options = RunOptions(device="cpu", num_workers=2, weights_root=Path(data_root))
    run_dir = split_dir(tmp_root / WORK_DIRNAME / "runs" / "E0-rect_smoke", 0)
    lines: list[str] = []
    result = run_split(resolved, 0, data_root=tmp_root, out_dir=run_dir, options=options, log=lines.append)
    smoke_require(result["status"] == "done", "the tiny run did not train")
    for name in (*RUN_FILES, "best.pt"):
        smoke_require((run_dir / name).is_file(), f"run folder lacks {name}")
    smoke_require(not list(run_dir.glob("*.tmp*")), "temporary files left behind (non-atomic write)")
    metrics = read_metrics(run_dir)
    smoke_require(metrics["split_sha256"] == split["sha256"] and metrics["wall_time_s"] > 0, "metrics.json is incomplete")
    for part in ("val", "test"):
        with open(run_dir / f"predictions_{part}.csv", newline="") as handle:
            rows = list(csv.reader(handle))
        smoke_require(rows[0][:4] == ["filename", "domain", "true", "pred"] and len(rows) - 1 == len(split[part]),
                      f"predictions_{part}.csv has the wrong rows")
    again = run_split(resolved, 0, data_root=tmp_root, out_dir=run_dir, options=options, log=lines.append)
    smoke_require(again["status"] == "skipped", "a finished split was not skipped (idempotence)")
    image = Path(data_root) / selected[0].rel_path
    probs = predict_image(run_dir, image, "cpu", data_root, out=lambda text: None)
    smoke_require(probs.shape == (NUM_CLASSES,) and abs(float(probs.sum()) - 1.0) < 1e-4, "predict returned bad probabilities")
    log(f"smoke: OK - tiny {resolved.config.exp_id} run ({'pretrained' if pretrained else 'random'} weights, "
        f"{len(split['train'])}/{len(split['val'])}/{len(split['test'])} train/val/test images, workers 2): complete run folder, "
        f"skipped on rerun, predict OK ({time.time() - started:.0f} s)")


def method_a_smoke(data_root, tmp_root, selected: list[Record], log=print) -> None:
    """Method A on the tiny smoke set (everything in ``tmp_root``): pseudo-masks of the white images and a QC sheet,
    one composite per class (reproducible from its seed), and one tiny E3-A run whose training set contains
    composites, through the real `run_split` path."""
    started = time.time()
    stats = build_white_masks(tmp_root, selected, workers=1)
    white = [r for r in selected if r.domain == "white"]
    smoke_require(stats.total == len(white) and stats.built == len(white), "pseudo-masks were not built for every white image")
    for record in white:
        mask = read_white_mask(tmp_root, record.filename)
        smoke_require(mask.shape == read_cached_rgb(tmp_root, record.filename).shape[:2] and mask.any(),
                      f"{record.filename}: the pseudo-mask is empty or has the wrong size")
    smoke_require(build_white_masks(tmp_root, selected, workers=1).built == 0, "second mask run is not idempotent")
    sheets = save_mask_qc_sheets(tmp_root, selected, rejects=set())
    smoke_require(all(p.stat().st_size > 1000 for p in sheets), "QC sheets were not written")
    split = smoke_split(selected)
    pool = CompositePool(tmp_root, 0, selected, exclusions=set())
    smoke_require(pool.leaves and all(r.filename in split["train"] for r in pool.leaves), "composite pool is empty or leaks")
    classes = sorted({r.cls_idx for r in pool.leaves})
    for cls_idx in classes:
        leaf, background = pool.sample(np.random.default_rng(cls_idx), cls_idx)
        image, mask, label = make_composite(leaf, background, np.random.default_rng(7), data_root=tmp_root)
        again, _, _ = make_composite(leaf, background, np.random.default_rng(7), data_root=tmp_root)
        smoke_require(label == cls_idx and image.shape[:2] == mask.shape and mask.any() and np.array_equal(image, again),
                      f"composite of class {cls_idx} is empty or not reproducible")
    resolved = resolve_experiment("E3-A", Choices(choices_path(tmp_root), {}), placeholders=True)
    resolved = replace(resolved, config=replace(resolved.config, pretrained=False, **FAST_CONFIG))
    run_dir = split_dir(tmp_root / WORK_DIRNAME / "runs" / "E3-A_smoke", 0)
    result = run_split(resolved, 0, data_root=tmp_root, out_dir=run_dir, options=RunOptions(device="cpu", num_workers=0), log=lambda _: None)
    metrics = result["metrics"]
    smoke_require(metrics["composites"]["n_per_epoch"] > 0 and metrics["n_train"] > len(split["train"]) - 1, "E3-A trained without composites")
    log(f"smoke: OK - Method A: {stats.built} pseudo-masks and QC sheet, composites of {len(classes)} classes (reproducible), "
        f"tiny E3-A run with {metrics['composites']['n_per_epoch']} composites per epoch ({time.time() - started:.0f} s)")


def method_b_smoke(data_root, tmp_root, selected: list[Record], log=print) -> None:
    """Method B on the tiny smoke set (everything in ``tmp_root``, after `method_a_smoke` built the pseudo-masks): one tiny
    segmenter epoch through `run_seg_split` (run folder, boxes of every image, no annotation touched), a tiny E4-B run that
    crops by those boxes, and `predict` on the E4-B run (segmenter, crop, classifier)."""
    started = time.time()
    resolved = resolve_experiment("S-seg", Choices(choices_path(tmp_root), {}))
    pretrained = pretrained_available(resolved.config.backbone, data_root)
    resolved = replace(resolved, config=replace(resolved.config, pretrained=pretrained, **FAST_CONFIG))
    seg_run = split_dir(runs_dir(tmp_root) / "S-seg", 0)
    result = run_seg_split(resolved, 0, data_root=tmp_root, out_dir=seg_run,
                           options=RunOptions(device="cpu", num_workers=0, limit=FAST_IMAGES, weights_root=Path(data_root)), log=lambda _: None)
    for name in ("config.json", "env.json", "history.csv", "metrics.json", "best.pt", BOXES_FILENAME, SEG_METRICS_FILENAME):
        smoke_require((seg_run / name).is_file(), f"segmenter run folder lacks {name}")
    smoke_require(not list(seg_run.glob("*.tmp*")), "temporary files left behind (segmenter run)")
    seg_metrics = read_seg_metrics(seg_run)
    smoke_require("dev" not in seg_metrics and "eval" not in seg_metrics, "a training run must not touch the annotations")
    boxes = load_boxes(tmp_root, 0)
    smoke_require(set(boxes) == {r.filename for r in selected}, "boxes.json does not cover every cached image")
    smoke_require(all(e["fallback"] or (e["box"][0] < e["box"][2] and e["box"][1] < e["box"][3]) for e in boxes.values()), "a box has no area")
    smoke_require(run_seg_split(resolved, 0, data_root=tmp_root, out_dir=seg_run, options=RunOptions(device="cpu", num_workers=0, limit=FAST_IMAGES,
                  weights_root=Path(data_root)), log=lambda _: None)["status"] == "skipped", "a finished segmenter split was not skipped")
    b = resolve_experiment("E4-B", Choices(choices_path(tmp_root), {}), placeholders=True)
    b = replace(b, config=replace(b.config, pretrained=False, **FAST_CONFIG))
    run_dir = split_dir(runs_dir(tmp_root) / "E4-B_smoke", 0)
    outcome = run_split(b, 0, data_root=tmp_root, out_dir=run_dir, options=RunOptions(device="cpu", num_workers=0), log=lambda _: None)
    smoke_require(outcome["metrics"]["seg_boxes_sha256"] == result["metrics"]["boxes_sha256"], "E4-B did not record the boxes it used")
    probs = predict_image(run_dir, Path(data_root) / selected[0].rel_path, "cpu", tmp_root, out=lambda text: None)
    smoke_require(probs.shape == (NUM_CLASSES,) and abs(float(probs.sum()) - 1.0) < 1e-4, "predict (E4-B) returned bad probabilities")
    fallbacks = result["metrics"]["fallbacks"]
    log(f"smoke: OK - Method B: tiny segmenter epoch ({'pretrained' if pretrained else 'random'} weights, {result['metrics']['n_train_per_epoch']} samples), "
        f"boxes for {len(boxes)} images ({sum(c['fallback'] for c in fallbacks.values())} fallbacks), tiny E4-B run cropping by them, "
        f"predict = segment + crop + classify ({time.time() - started:.0f} s)")


def smoke_extra_checks(data_root, tmp_root, selected: list[Record]) -> None:
    classifier_smoke(data_root, tmp_root, selected)
    method_a_smoke(data_root, tmp_root, selected)
    method_b_smoke(data_root, tmp_root, selected)


def cmd_smoke(args: argparse.Namespace) -> int:
    """Tiny end-to-end check: data root, image discovery, library imports, device, the data path (index, EXIF
    read, cache, dHash, splits, figures on ~20 images in a temp folder) and one tiny classifier experiment
    through the real `run` code path on CPU, followed by `predict`, then Method A (pseudo-masks, composites, a tiny E3-A run)
    and Method B (a tiny segmenter epoch, boxes, a tiny E4-B run, `predict` with the segmenter); everything in a temp folder."""
    data_root = Path(args.data_root)
    print(f"smoke: data root = {data_root.resolve()}")
    if not data_root.is_dir():
        print(f"smoke: FAIL - data root {data_root} is not a directory (see --data-root)", file=sys.stderr)
        return EXIT_FAILURE
    images = find_images(data_root)
    if not images:
        print(f"smoke: FAIL - no JPEG images found under {data_root}", file=sys.stderr)
        return EXIT_FAILURE
    print(f"smoke: OK - found {len(images)} JPEG images (excluding {WORK_DIRNAME}/)")

    import cv2
    import matplotlib
    import numpy
    import skimage
    import sklearn
    import torch
    import torchvision

    print(f"smoke: python {sys.version.split()[0]}")
    for module in (numpy, matplotlib, cv2, sklearn, skimage, torch, torchvision):
        print(f"smoke: {module.__name__} {module.__version__}")
    device = resolve_device(args.device)
    print(f"smoke: OK - device = {device} (requested: {args.device}), fast = {args.fast}")
    try:
        run_data_smoke(data_root, extra_checks=lambda tmp_root, selected: smoke_extra_checks(data_root, tmp_root, selected))
    except (DatasetError, ExperimentError) as exc:
        print(f"smoke: FAIL - {exc}", file=sys.stderr)
        return EXIT_FAILURE
    print("smoke: PASSED")
    return EXIT_OK


def not_implemented(command: str, phase: str) -> Callable[[argparse.Namespace], int]:
    """Placeholder handler: say which phase will provide the command and exit non-zero."""

    def handler(args: argparse.Namespace) -> int:
        print(f"{command}: not implemented yet (phase {phase})", file=sys.stderr)
        return EXIT_NOT_IMPLEMENTED

    return handler

def parse_splits(text: str) -> tuple[int, ...]:
    """Parse '0,1,2' into (0, 1, 2); duplicates are dropped, order is kept."""
    try:
        values = [int(part) for part in text.split(",") if part.strip() != ""]
    except ValueError:
        raise argparse.ArgumentTypeError(f"expected comma-separated integers, got {text!r}") from None
    if not values or min(values) < 0:
        raise argparse.ArgumentTypeError(f"expected one or more non-negative integers, got {text!r}")
    return tuple(dict.fromkeys(values))


def add_global_flags(parser: argparse.ArgumentParser, *, is_subcommand: bool) -> None:
    """Add the global flags. On subparsers the defaults are suppressed so that a flag given
    before the command is not overwritten by the subparser's default."""

    def default(value):
        return argparse.SUPPRESS if is_subcommand else value

    group = parser.add_argument_group("global flags (accepted before or after the command)")
    group.add_argument(
        "--data-root",
        type=Path,
        default=default(Path(DEFAULT_DATA_ROOT)),
        help=f"dataset folder, relative to the working directory (default: {DEFAULT_DATA_ROOT})",
    )
    group.add_argument(
        "--device",
        choices=DEVICE_CHOICES,
        default=default("auto"),
        help="compute device (default: auto = cuda, then mps, then cpu)",
    )
    group.add_argument(
        "--seed-offset",
        type=int,
        default=default(0),
        help="added to every seed, for repeating an experiment with different randomness (default: 0)",
    )
    group.add_argument(
        "--fast",
        action="store_true",
        default=default(False),
        help="smoke settings: tiny subsets, 1 epoch",
    )


def _configure_prepare(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--workers",
        type=int,
        default=None,
        metavar="N",
        help="worker processes for image caching (default: number of CPU cores, at most 8)",
    )


def _configure_run(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--exp", required=True, metavar="ID", help="experiment ID (E1-U), a group (E0, E1, E2, X-domain) or a comma-separated list")
    parser.add_argument(
        "--splits",
        type=parse_splits,
        default=DEFAULT_SPLITS,
        metavar="LIST",
        help="comma-separated split seeds (default: 0,1,2,3,4)",
    )
    parser.add_argument("--force", action="store_true", help="retrain splits whose metrics.json already exists")
    parser.add_argument("--sweep-lr", action="store_true",
                        help="learning-rate sweep: split 0 at lr 1e-4 and 3e-4 into _work/runs/sweep/ (never a result)")
    parser.add_argument("--sweep-composites", action="store_true",
                        help="Method A: split 0 of --exp E3-A with 0.5x and 1x composites per epoch into _work/runs/sweep/ (never a result)")
    parser.add_argument("--batch-size", type=int, default=None, metavar="N", help="batch size (default 32; 16 + --grad-accum 2 if memory is short)")
    parser.add_argument("--grad-accum", type=int, default=None, metavar="N", help="gradient accumulation steps (default 1)")
    parser.add_argument("--num-workers", type=int, default=None, metavar="N", help="data-loading processes (default: cores - 1, at most 4)")
    parser.add_argument("--out-dir", type=Path, default=None, metavar="DIR", help="write DIR/<ID>/split_<k>/ instead of _work/runs/<ID>/")
    dev = parser.add_argument_group("dev overrides (output goes to _work/runs/scratch/, never counted as a result)")
    dev.add_argument("--lr", type=float, default=None, metavar="LR", help="fine-tuning learning rate instead of choices.json")
    dev.add_argument("--epochs", type=int, default=None, metavar="N", help="fine-tuning epochs (default 30)")
    dev.add_argument("--stage1-epochs", type=int, default=None, metavar="N", help="linear-probe epochs (default 2)")
    dev.add_argument("--seg-arch", default=None, choices=tuple(SEG_ARCHITECTURES), metavar="ARCH",
                     help="S-seg only: try another segmenter architecture (the one swap 06 allows, decided on the dev annotations)")
    parser.add_argument("--seg-dir", type=Path, default=None, metavar="DIR",
                        help="Method B (E4-B): the S-seg runs folder whose split_<k>/boxes.json to use (default: _work/runs/S-seg)")


def _configure_choose_lr(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--backbone", required=True, choices=BACKBONES, help="backbone whose split-0 sweep to evaluate")


def _configure_gate(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("gate", choices=("g0", "g1", "g2"), help="g0: input mode (after E0), g1: backbone (after E1-U, E2-cnx-U, E2-swin-U), "
                        "g2: recommended method (plain G1 model vs E3-A vs E4-B)")
    parser.add_argument("--cut", action="append", choices=("A", "B"), default=None, metavar="METHOD",
                        help="g2 only: leave Method A or B out because it was cut (cut lines of the README); repeat for both")
    parser.add_argument("--force", action="store_true",
                        help="g2 only: overwrite a recommendation that an earlier `gate g2` froze with a different outcome")


def _configure_gradcam(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--exp", required=True, metavar="ID", help="experiment ID")
    parser.add_argument("--split", type=int, required=True, metavar="K", help="split seed")


def _configure_predict(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--exp", default=None, metavar="ID", help="experiment ID (default: the recommended one in choices.json)")
    parser.add_argument("--split", type=int, default=0, metavar="K", help="split seed (default: 0)")
    parser.add_argument("--image", type=Path, required=True, metavar="PATH", help="image to classify")
    parser.add_argument("--run-dir", type=Path, default=None, metavar="DIR", help="use DIR/best.pt directly instead of the run folder of --exp")
    parser.add_argument("--seg-dir", type=Path, default=None, metavar="DIR",
                        help="Method B: the S-seg runs folder with the segmenter checkpoints (default: next to the experiment's folder)")


def _configure_seg_eval(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--set", required=True, choices=SEG_EVAL_SETS,
                        help="dev: the 10 development annotations (any time); eval: the 20 reporting annotations (needs --final)")
    parser.add_argument("--splits", type=parse_splits, default=DEFAULT_SPLITS, metavar="LIST", help="comma-separated split seeds (default: 0,1,2,3,4)")
    parser.add_argument("--final", action="store_true", help="--set eval only: confirm that these are the final segmenters (the eval images are looked at once)")
    parser.add_argument("--again", action="store_true", help="--set eval only: measure a segmenter again that was already measured")
    parser.add_argument("--seg-dir", type=Path, default=None, metavar="DIR", help="the S-seg runs folder to read (default: _work/runs/S-seg)")
    parser.add_argument("--figure", type=Path, default=None, metavar="PATH", help="where to write the examples figure (default: see seg-eval in 40_segmentation.ipynb)")


@dataclass(frozen=True)
class Command:
    name: str
    help: str
    handler: Callable[[argparse.Namespace], int]
    configure: Callable[[argparse.ArgumentParser], None] | None = None


COMMANDS = (
    Command(
        "download-weights",
        "fetch the torchvision pretrained weights into <data-root>/_work/weights/ (idempotent)",
        cmd_download_weights,
    ),
    Command(
        "prepare",
        "index, cache, near-duplicate audit, splits, tables and figures (idempotent)",
        cmd_prepare,
        _configure_prepare,
    ),
    Command("run", "train and evaluate one experiment over the given splits", cmd_run, _configure_run),
    Command(
        "choose-lr",
        "record the learning rate of a backbone from its split-0 sweep (T3.4 rule) in choices.json",
        cmd_choose_lr,
        _configure_choose_lr,
    ),
    Command(
        "choose-composites",
        "record the composites per epoch of Method A from its split-0 sweep (validation only) in choices.json",
        cmd_choose_composites,
    ),
    Command(
        "gate",
        "recompute decision gate g0 (input mode), g1 (backbone) or g2 (recommended method) from the runs and record it in choices.json",
        cmd_gate,
        _configure_gate,
    ),
    Command(
        "seg-eval",
        "segmenter metrics on the annotated field images: --set dev (development) or --set eval --final (reporting, once)",
        cmd_seg_eval,
        _configure_seg_eval,
    ),
    Command("summarize", "aggregate all runs into tables, figures, failure cases and findings", cmd_summarize),
    Command(
        "benchmark",
        "time inference per image of the three backbones on this device and write _work/results/inference_benchmark.json (summarize reads it)",
        cmd_benchmark,
    ),
    Command("gradcam", "Grad-CAM figures for one experiment and split", not_implemented("gradcam", "07"), _configure_gradcam),
    Command("predict", "classify a single image and print class probabilities", cmd_predict, _configure_predict),
    Command("smoke", "tiny end-to-end check: imports, device, data path, one tiny experiment and predict", cmd_smoke),
    Command(
        "reproduce",
        "download-weights, prepare, every reported experiment, summarize",
        not_implemented("reproduce", "08"),
    ),
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=Path(__file__).name,
        description="CSCI935 rice leaf disease classification - reproduces every reported number.",
        epilog="Global flags may be placed before or after the command.",
    )
    add_global_flags(parser, is_subcommand=False)
    subparsers = parser.add_subparsers(dest="command", required=True, metavar="COMMAND")
    for command in COMMANDS:
        sub = subparsers.add_parser(command.name, help=command.help, description=command.help)
        if command.configure is not None:
            command.configure(sub)
        add_global_flags(sub, is_subcommand=True)
        sub.set_defaults(handler=command.handler)
    return parser

def run_cli(argv: list[str] | None = None) -> int:
    """Parse argv and run the chosen command. Returns the process exit code."""
    args = build_parser().parse_args(argv)
    return args.handler(args)


def main() -> None:
    sys.exit(run_cli())

if __name__ == "__main__":
    main()
