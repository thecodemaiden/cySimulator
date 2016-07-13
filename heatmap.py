import numpy as np
class Heatmap(object):
    """description of class"""
    heatMapValues = np.array( [[36,    0,    0],
                                [73,    0,    0],
                                [109,    0,    0],
                                [146,    0,    0],
                                [182,    0,    0],
                                [219,    0,    0],
                                [255,    0,    0],
                                [255,   36,    0],
                                [255,   73,    0],
                                [255,  109,    0],
                                [255,  146,    0],
                                [255,  182,    0],
                                [255,  219,    0],
                                [255,  255,    0],
                                [255,  255,   43],
                                [255,  255,   85],
                                [255,  255,  128],
                                [255,  255,  170],
                                [255,  255,  213],
                                [255,  255,  255]], dtype='u1')
    @classmethod
    def getHeatmapValue(cls, v, minVal, maxVal):
        if (maxVal == minVal):
            m = 0
        else:
            m = float(v - minVal) / float(maxVal - minVal)
        idx = int(m*len(cls.heatMapValues))
        if idx == len(cls.heatMapValues):
            idx -= 1
        return cls.heatMapValues[idx]





