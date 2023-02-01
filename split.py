import os
import shutil
import math
from tqdm import tqdm


'''
将指定文件夹下的文件，拆分为n份;
如现有目录：
- rootDir
-- dir1
---- file_1
---- file_2
...
---- file_n

-- dir2
---- file_1
---- file_2
...
---- file_n

split_path_root = rootDir
split_num = 2

则运行后，目录变为：
- rootDir
-- dir1
---- file_1
---- file_2
...
---- file_n
%新增部分-开始%
--- 1
---- file_1
---- file_2
--- 2
---- file_3
---- file_4
...
%新增部分-结束%

-- dir2
---- file_1
---- file_2
...
---- file_n
%新增部分-开始%
--- 1
---- file_1
---- file_2
--- 2
---- file_3
---- file_4
...
%新增部分-结束%
'''


# 待拆分的文件夹路径
split_path_root = r'C:\Users\SXF\Desktop\新建文件夹'
# 每份文件夹里多少个文件
split_num = 500


for item in os.listdir(split_path_root):
    dir_path = os.path.join(split_path_root, item)
    if not os.path.isdir(dir_path):
        continue
    print(dir_path)
    img_lists = list(filter(lambda x: os.path.isfile(os.path.join(dir_path, x)), os.listdir(dir_path)))
    split_cnt = math.ceil(len(img_lists)/split_num)
    for i in range(split_cnt):
        index_start = i * split_num
        index_end = (i+1) * split_num
        sub_dir_path = os.path.join(dir_path, str(i))
        if not os.path.exists(sub_dir_path):
            os.mkdir(sub_dir_path)
        for file_name in tqdm(img_lists[index_start: index_end]):
            src_file_path = os.path.join(dir_path, file_name)
            dst_file_path = os.path.join(sub_dir_path, file_name)
            if not os.path.exists(dst_file_path):
                shutil.copy(src_file_path, dst_file_path)
print('done!')




