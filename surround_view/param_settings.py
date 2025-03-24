import os
import cv2
'''
该py为以下参数的存放

首先在车身的四角摆放四个标定板，标定板的图案大小并无特殊要求，只要尺寸一致，能在图像中清晰看到即可。每个标定板应当恰好位于相邻的两个相机视野的重合区域中。
在上面拍摄的相机画面中车的四周铺了一张标定布，这个具体是标定板还是标定布不重要，只要能清楚的看到特征点就可以了。
然后我们需要设置几个参数：(以下所有参数均以厘米为单位)
innerShiftWidth, innerShiftHeight：标定板内侧边缘与车辆左右两侧的距离，标定板内侧边缘与车辆前后方的距离。
shiftWidth, shiftHeight：这两个参数决定了在鸟瞰图中向标定板的外侧看多远。这两个值越大，鸟瞰图看的范围就越大，相应地远处的物体被投影后的形变也越严重，所以应酌情选择。
totalWidth, totalHeight：这两个参数代表鸟瞰图的总宽高，在我们这个项目中标定布宽 6m 高 10m，于是鸟瞰图中地面的范围为 (600 + 2 * shiftWidth, 1000 + 2 * shiftHeight)。为方便计我们让每个像素对应 1 厘米，于是鸟瞰图的总宽高为
totalWidth = 600 + 2 * shiftWidth
totalHeight = 1000 + 2 * shiftHeight
车辆所在矩形区域的四角 (图中标注的红色圆点)，这四个角点的坐标分别为 (xl, yt), (xr, yt), (xl, yb), (xr, yb) (l 表示 left, r 表示 right，t 表示 top，b 表示 bottom)。这个矩形区域相机是看不到的，我们会用一张车辆的图标来覆盖此处。
注意这个车辆区域四边的延长线将整个鸟瞰图分为前左 (FL)、前中 (F)、前右 (FR)、左 (L)、右 (R)、后左 (BL)、后中 (B)、后右 (BR) 八个部分，其中 FL (区域 I)、FR (区域 II)、BL (区域 III)、BR (区域 IV) 是相邻相机视野的重合区域，也是我们重点需要进行融合处理的部分。F、R、L、R 四个区域属于每个相机单独的视野，不需要进行融合处理。
'''

camera_names = ["front", "back", "left", "right"]

# --------------------------------------------------------------------
# (shift_width, shift_height): how far away the birdview looks outside
# of the calibration pattern in horizontal and vertical directions
shift_w = 300
shift_h = 300

# size of the gap between the calibration pattern and the car
# in horizontal and vertical directions
inn_shift_w = 20
inn_shift_h = 50

# total width/height of the stitched image
total_w = 600 + 2 * shift_w
total_h = 1000 + 2 * shift_h

# four corners of the rectangular region occupied by the car
# top-left (x_left, y_top), bottom-right (x_right, y_bottom)
xl = shift_w + 180 + inn_shift_w
xr = total_w - xl
yt = shift_h + 200 + inn_shift_h
yb = total_h - yt
# --------------------------------------------------------------------

project_shapes = {
    "front": (total_w, yt),
    "back":  (total_w, yt),
    "left":  (total_h, xl),
    "right": (total_h, xl)
}

# pixel locations of the four points to be chosen.
# you must click these pixels in the same order when running
# the get_projection_map.py script
# 标志点
project_keypoints = {
    "front": [(shift_w + 120, shift_h),
              (shift_w + 480, shift_h),
              (shift_w + 120, shift_h + 160),
              (shift_w + 480, shift_h + 160)],

    "back":  [(shift_w + 120, shift_h),
              (shift_w + 480, shift_h),
              (shift_w + 120, shift_h + 160),
              (shift_w + 480, shift_h + 160)],

    "left":  [(shift_h + 280, shift_w),
              (shift_h + 840, shift_w),
              (shift_h + 280, shift_w + 160),
              (shift_h + 840, shift_w + 160)],

    "right": [(shift_h + 160, shift_w),
              (shift_h + 720, shift_w),
              (shift_h + 160, shift_w + 160),
              (shift_h + 720, shift_w + 160)]
}

car_image = cv2.imread(os.path.join(os.getcwd(), "images", "car.png"))
car_image = cv2.resize(car_image, (xr - xl, yb - yt))
