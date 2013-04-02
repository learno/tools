#coding=utf8

import Image
from plistlib import writePlist as write_plist

ROW_RANGE = 5

def search_box(x, y, width, height, alphas):
    left, upper, right, lower = x, y, x + 1, y + 1
    nexts = [(x, y)]
    alphas[y * width + x] = 0
    while nexts:
        x, y = nexts.pop()
        left = min(left, x)
        upper = min(upper, y)
        right = max(right, x + 1)
        lower = max(lower, y + 1)
        base_xs = [max(x - 1, 0), x, min(x + 1, width - 1)]
        base_ys = [max(y - 1, 0), y, min(y + 1, height - 1)]
        search_points = [(x, y) for x in base_xs for y in base_ys]
        for x, y in search_points:
            alpha = alphas[y * width + x]
            if alpha == 0:
                continue
            alphas[y * width + x] = 0
            nexts.append((x, y))
    #if (right - left) * (lower - upper) < 10:
        #print left, upper, right, lower
    return left, upper, right, lower


def out_plist(boxes, width, height, image_name):
    pl = dict(
        frames={},
        metadata=dict(
            format=2,
            realTextureFileName=image_name,
            size='{%s,%s}' % (width, height),
            #smartupdate='$TexturePacker:SmartUpdate:7c234510d12efcbc8b7f8ad89486946f$',
            textureFileName=image_name,
        )
    )
    name = image_name.split('.')[0]
    row, column= 0, 0
    pre_upper = boxes[0][1] if boxes else -1
    for left, upper, right, lower in boxes:
        if upper - pre_upper > ROW_RANGE:
            row += 1
            column = 0
        width = right - left
        height = lower - upper
        box_info = dict(
            frame='{{%s,%s},{%s,%s}}' % (left, upper, width, height),
            offset='{0,0}',
            rotated=False,
            sourceColorRect='{{0,0},{%s,%s}}' % (width, height),
            sourceSize='{%s,%s}' % (width, height),
        )
        pl['frames']['%s_%02d_%s.png' % (name, row, column)] = box_info
        column += 1
        pre_upper = upper
    plist_name = name + '.plist'
    write_plist(pl, plist_name)

def boxes_cmp(box0, box1):
    x0, y0 = box0[:2]
    x1, y1 = box1[:2]
    return cmp (x0, x1) if abs(y0 - y1) <= ROW_RANGE else cmp(y0, y1)


def handle_png(image_name, ):
    im = Image.open(image_name)
    im.load()
    width, height = im.size
    alpha_bands = im.split()[-1]
    alphas = list(alpha_bands.im)

    boxes = []
    for y in xrange(height):
        for x in xrange(width):
            alpha = alphas[y * width + x]
            if alpha == 0:
                continue
            box = search_box(x, y, width, height, alphas)
            boxes.append(box)
    boxes.sort(cmp=lambda (x0, y0, _x0, _y0), (x1, y1, _x1, _y1):
        cmp(x0, x1) if abs(y0 - y1) <= ROW_RANGE else cmp(y0, y1)
    )
    out_plist(boxes, width, height, image_name)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='...')
    parser.add_argument('image_name', metavar='image name',
                       nargs='?', default='test.png',
                       help='...')
    args = parser.parse_args()

    from time import time as timestamp
    start = timestamp()
    handle_png(args.image_name)

    print 'used time:', timestamp() - start
