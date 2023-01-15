import glob
import os
from datetime import datetime

from PIL import Image

in_dir = './data/test2'
out_dir = in_dir + '/output'
img_width = 20
img_height = 27
sections = ['GFP', 'DAPI']
horizontal_overlap = 125
vertical_overlap = 90


def merge_row(images, overlap=0):
    w = sum(img.size[0] for img in images) - (len(images) - 1) * overlap
    h = max(images, key=lambda img: img.size[1]).size[1]
    result = Image.new("I;16", (w, h))
    current_w = 0
    for idx, image in enumerate(images):
        result.paste(image, (current_w, 0))
        current_w += image.size[0] - overlap
    return result


def merge_column(images, overlap=0):
    w = max(images, key=lambda img: img.size[0]).size[0]
    h = sum(img.size[1] for img in images) - (len(images) - 1) * overlap
    result = Image.new("I;16", (w, h))
    current_h = 0
    for idx, image in enumerate(images):
        result.paste(image, (0, current_h))
        current_h += image.size[1] - overlap
    return result


def extract_file_number(filename, section):
    try:
        num = filename.split('_')[filename.split('_').index(section) - 1]
        return int(num)
    except AttributeError:
        return filename


def main():
    now = datetime.now().strftime("%Y-%m-%d_%Hh%Mmin%Ss")

    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)

    for section in sections:
        section_output = (out_dir + '/%s-%s.png') % (section, now)

        section_files = glob.glob((in_dir + '/*%s*.tif') % section)
        section_files = sorted(section_files, key=lambda file: extract_file_number(file, section), reverse=False)

        if len(section_files) != img_width * img_height:
            print('ERROR: number of file in section %s is not correct!' % section)
            continue

        # merge section files
        print('\n======== [START] Merging section : %s =========' % section)

        image_rows = []
        image_current_row = []

        for idx, section_file in enumerate(section_files):
            print('merging image : %s ...' % os.path.basename(section_file))
            current_image = Image.open(section_file)
            image_current_row.append(current_image)

            if (idx + 1) % img_width == 0:
                image_rows.append(merge_row(image_current_row, horizontal_overlap))
                image_current_row = []

        image_result = merge_column(image_rows, vertical_overlap)
        print('\n\n==> Saving image as %s...' % os.path.basename(section_output))
        image_result.save(section_output, "PNG")
        image_result.close()
        print(
            '======== [END] Merging section : %s ==> [%s] =========\n\n' % (section, os.path.basename(section_output)))


if __name__ == '__main__':
    main()
