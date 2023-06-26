from search import Tokens

from PIL import Image, ImageEnhance


def create_collage(
    query,
    image_searcher,

    background_count=1,

    graphics_count=3,
    graphics_square_percentage=0.8,
    graphics_max_size_differ=3,

    objects_count=3,
    objects_square_percentage=0.5,
    objects_max_size_differ=3,

    size=(1000, 1000),
):

    def _get_sizes(count, square_percentage, max_size_differ):
        result = [
            int(random.randint(100, int(100 * max_size_differ)) / 100 / count * square_percentage * size[0])
            for i in range(count)
        ]
        result.sort()
        return result

    def _paste_images(collage, images, img_sizes, imgs_token):
        for i in range(min(len(images[imgs_token]), len(img_sizes))):
            img = Image.open(images[imgs_token][i])
            imgsize = (int(img_sizes[i]), int(img_sizes[i] * img.size[1] / img.size[0]))
            imgpos = (random.randint(0, size[0] - imgsize[0]), random.randint(0, size[1] - imgsize[1]))
            img = img.resize(imgsize)
            collage.paste(img, imgpos, mask=img)

    images = image_searcher.search(query, graphics_count=graphics_count*2, objects_count=objects_count)

    collage = Image.new("RGBA", size)
    collage.paste(Image.open(images[Tokens.BACKGROUND][0]).resize(size))

    graphics_sizes = _get_sizes(graphics_count, graphics_square_percentage, graphics_max_size_differ)
    objects_sizes = _get_sizes(objects_count, objects_square_percentage, objects_max_size_differ)

    _paste_images(collage, images, graphics_sizes, Tokens.GRAPHICS)
    _paste_images(collage, images, objects_sizes, Tokens.OBJECTS)

    return collage
