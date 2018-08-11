#!/usr/bin/env bash
THUMBNAIL_PREFIX="_thumbnail"
ICON_FILE="_icon.jpg"

# Determine the original image used to make _icon.jpg (for directory thumbnails)
dir_icon_original_image=""
if [ -e ${ICON_FILE} ]; then
    ret=$(~/git/scratch/preview.mikeroburst.com/scripts/convert_icon_files.py ${ICON_FILE})
    if [[ $? == 0 ]]; then
        dir_icon_original_image=${ret}
    fi
fi

# Create thumbnails for each file for each size
for height in 20 100 250 500; do
    thumbnail_dir="${THUMBNAIL_PREFIX}/${height}"
    if [ ! -d ${thumbnail_dir} ]; then
        mkdir -p ${thumbnail_dir}
    fi
    for filename in "$@"; do
        if [ -f ${filename} ]; then
            convert -limit memory 2048gb -resize "x${height}" -sharpen 1x1 -compress JPEG -quality 45 ${filename} ${thumbnail_dir}/${filename}
        fi
    done

    # Create directory thumbnails if we know what image to use
    if [ ! -z ${dir_icon_original_image} ] && [ -f ${dir_icon_original_image} ]; then
        convert -limit memory 2048gb -resize "x${height}" -sharpen 1x1 -compress JPEG -quality 45 ${dir_icon_original_image} ${thumbnail_dir}/${ICON_FILE}
    fi
done
