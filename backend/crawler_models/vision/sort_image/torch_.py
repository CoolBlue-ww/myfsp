import torch
import torch.nn as nn


shape = (3, 4, 4)
tensor = torch.ones(shape)

"""
输入通道数， 输出通道数， 卷积核大小， 卷积步长， 零填充， 卷积核扩张率， 分组卷积组数， 是否开启偏置
"""
conv_layer = nn.Conv2d(in_channels=3, out_channels=2, kernel_size=3, stride=1, padding=1, dilation=1, groups=1, bias=True)
output = conv_layer(tensor)
print(tensor)
print(output)

