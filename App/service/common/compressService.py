import imageio
from PIL import Image, ImageSequence
import glob

def gif(self):
    file_path = 'C:/Users/ming.wen/phpweb/images'
    files = find_gif_files(file_path)

    for file in files:
        # 设置压缩尺寸，这里设置压缩尺寸为500
        rp = 150

        img_list = []

        # 读取原gif动图
        img = Image.open(file)

        # 对原动图进行压缩，并存入img_list
        for i in ImageSequence.Iterator(img):
            i = i.convert('RGB')
            if max(i.size[0], i.size[1]) > rp:
                i.thumbnail((rp, rp))
            img_list.append(i)

        # 计算帧的频率
        try:
            durt = (img.info)['duration'] / 1000
            # 读取img_list合成新的gif
            imageio.mimsave(file, img_list, duration=durt)
        except Exception as e:
            print(e)

    return True

def find_gif_files(dir_path):
    # dir_path = 'C:/Users/ming.wen/phpweb/images'

    # gif_files = find_gif_files(dir_path)
    return glob.glob(f'{dir_path}/*.gif', recursive=True)



