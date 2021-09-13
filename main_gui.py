import sys

import cv2 as cv
import numpy as np

from PyQt5.QtWidgets import (QApplication, QFileDialog, QColorDialog,
                             QMainWindow)

from gui import *
from lib.utils import get_image_view, OcrReader, check_dir
from lib.threads import TimelineThread, GenSubThread
from lib.core.split import if_srt_frame


class MyWindow(QMainWindow, Ui_pdf_ocr):
    # 初始化
    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent)
        self.setupUi(self)

        # self.videoView.my_scene.setSceneRect(0, 0, 544, 306)
        # self.clipView.my_scene.setSceneRect(0, 0, 920, 90)

        # 注册监听
        # 选择输出目录的项
        self.outdirButton.clicked.connect(self.get_out_dir)

        # 开始转换pdf的按钮
        self.start.clicked.connect(self.pdf_ocr)

        # 初始化实例变量
        self.output_dir = None
        self.pdf = None
        self.pdf_total_pages = 0
        self.page_idx = 0
        self.page = None
        self.hasOpen = False

        check_dir()

    def get_out_dir(self):
        """
        选择输出目录
        """
        output_dir = QFileDialog.getExistingDirectory(self, "目录", ".",)
        if not output_dir:
            return

        self.output_dir = output_dir
        self.outdir.setText(self.output_dir)

    def pdf_ocr(self):
        if not self.hasOpen:
            return

        rec_pos = self.videoView.rect.getRect()
        if sum(rec_pos) == 0:
            return
        view_height = self.videoView.my_scene.height()
        view_width = self.videoView.my_scene.width()
        frame_height = self.frame.shape[0]
        frame_width = self.frame.shape[1]
        vid_x = self.videoView.old_img_item.x()
        vid_y = self.videoView.old_img_item.y()

        h_ratio = frame_height / (view_height - 2 * vid_y)
        w_ratio = frame_width / (view_width - 2 * vid_x)

        box = [[int((rec_pos[1] - vid_y) * h_ratio), int((rec_pos[1] + rec_pos[3] - vid_y) * h_ratio)],
               [int((rec_pos[0] - vid_x) * w_ratio), int((rec_pos[0] + rec_pos[2] - vid_x) * w_ratio)]]

        ocr_method = self.ocrMethod.itemText(self.ocrMethod.currentIndex())
        # lang = ['ch_sim']
        lang_box_text = self.langBox.itemText(self.langBox.currentIndex())
        lang = [lang_box_text] if lang_box_text != "dual" else ['ch_sim', 'en']
        # TODO: 自动转成各种OCR需要的缩写
        ocr_reader = OcrReader(ocr_method, lang)
        ass_path = "output/split_vision.ass"
        # ocr_with_timeline(self.video, box, ocr_reader, ass_path, lang, self.progressBar)
        gen_sub_thread = GenSubThread(self.video, self.video_path, box,
                                      ocr_reader, lang, self, self.progressBar)
        gen_sub_thread.run()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = MyWindow()
    myWin.show()
    sys.exit(app.exec_())
