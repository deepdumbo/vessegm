import numpy as np
from image_util import BaseDataProvider
import img_processing as proc



class LungDataProvider(BaseDataProvider):
    channels = 1
    classes = 2
    img_list = []
    label_list = []
    img_idx = 0
    n_cur_img = -1
    num_slices = 100
    max_patches = 100
    id_patch = 0
    lim_x = 100
    lim_y = 100


    def _load_data_and_label(self):
        data, label = self._next_data()

        train_data = self._process_data(data)
        labels = self._process_labels(label)

        #train_data, labels = self._post_process(train_data, labels)
        nz = train_data.shape[1]
        nx = train_data.shape[2]
        ny = train_data.shape[3]

        return train_data.reshape(1, nz, nx, ny, self.channels), labels.reshape(1, nz, nx, ny, self.n_class)

    def _process_labels(self, label):
        if self.n_class == 2:
            nz = label.shape[1]
            nx = label.shape[2]
            ny = label.shape[3]
            labels = np.zeros((1, nz, nx, ny, self.n_class), dtype=np.float32)

            labels[..., 1] = np.ceil(label[..., 0] / (label.max() + 0.0001))
            labels[..., 0] = 1 - labels[..., 1]
            return labels

        return label

    def __call__(self, *args, **kwargs):
        return self._load_data_and_label()

    def __init__(self, img_folder, label_folder, nx=352, ny=480, a_min=None, a_max=None):
        self.a_min = a_min if a_min is not None else -np.inf
        self.a_max = a_max if a_min is not None else np.inf
        super(BaseDataProvider, self).__init__()
        self.img_list = proc.get_file_list(img_folder, pattern='*.gif')
        self.label_list = proc.get_file_list(label_folder, pattern='*.gif')
        self.n_examples = len(self.label_list)
        self.img_arr = proc.get_array_from_gif(self.img_list[0], norm=True)
        self.label_arr = proc.get_array_from_gif(self.label_list[0], norm=True)
        self.img_idx = 1
        self.id_patch = 0
        self.nz = self.img_arr.shape[0]
        self.nx = self.img_arr.shape[1]
        self.ny = self.img_arr.shape[2]
        print("Number of images = %d" % self.n_examples)

    def _next_data(self):
        print("img #%d" % self.img_idx)
        print("patch #%d" % self.id_patch)
        if self.img_idx >= self.n_examples:
            print("No more images left.")
            return
        if self.max_patches < self.id_patch:
            self.img_arr = proc.get_array_from_gif(self.img_list[self.img_idx], norm=True)
            self.label_arr = proc.get_array_from_gif(self.label_list[self.img_idx], norm=True)
            self.img_idx += 1
            self.id_patch = 0
            self.nz = self.img_arr.shape[0]
            self.nx = self.img_arr.shape[1]
            self.ny = self.img_arr.shape[2]

        self.id_patch += 1
        idz = np.random.randint(0, self.nz - self.num_slices - 1)
        idx = np.random.randint(0, self.nx - self.lim_x - 1)
        idy = np.random.randint(0, self.ny - self.lim_y - 1)
        print("idz = %d, idx = %d, idy = %d" % (idz, idx, idy))
        X = np.reshape(self.img_arr[idz:idz + self.num_slices, idx:idx + self.lim_x, idy:idy + self.lim_y],
                       (1, self.num_slices, self.lim_x, self.lim_y, 1))
        y = np.reshape(self.label_arr[idz:idz + self.num_slices, idx:idx + self.lim_x, idy:idy + self.lim_y],
                       (1, self.num_slices, self.lim_x, self.lim_y, 1))

        #del img_arr, label_arr

        return X, y


