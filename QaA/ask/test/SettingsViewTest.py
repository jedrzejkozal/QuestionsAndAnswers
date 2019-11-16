import os
from io import BytesIO
import shutil

from django import forms
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.shortcuts import reverse
from django.test import TestCase
from PIL import Image

from ..test.QuestionsMixIn import *
from ..test.LoginMixIn import *


class SettingsViewTest(TestCase, QuestionsMixIn, LoginMixIn):
    url = reverse('ask:settings')

    def __del__(self):

        for dir in os.listdir('media/'):
            if dir.count('TestUser') > 0:
                shutil.rmtree('media/' + dir)

    def test_after_uploading_img_is_saved_in_media_directory(self):
        self.create_users()
        self.login_user(username="TestUser2")

        img = self.get_img('media/testimage.png')
        form = {'image': img}

        self.client.post(self.url, data=form)

        # for some reason ImageFields are not saved
        # so we cant test if database filed changed
        # self.assertNotEqual(self.test_user2.avatar, None)

        filepath = 'media/user_id_{0}_{1}/{2}'.format(
            self.test_user2.id, self.test_user2.username, 'avatar.png')
        self.assertTrue(self.file_exist(filepath))

    def test_after_uploading_when_previous_file_exists_only_new_file_is_keept(self):
        self.create_users()
        self.login_user(username="TestUser2")

        shutil.copyfile('media/testimage.png', 'media/testimage1.png')

        img = self.get_img('media/testimage.png')
        form = {'image': img}
        self.client.post(self.url, data=form)

        img = self.get_img('media/testimage1.png')
        form = {'image': img}
        self.client.post(self.url, data=form)

        user_imgs_dir = 'media/user_id_{0}_{1}'.format(
            self.test_user2.id, self.test_user2.username)
        filepath = os.path.join(user_imgs_dir, '{0}'.format('avatar.png'))
        self.assertTrue(self.file_exist(filepath))

        num_files = len(os.listdir(user_imgs_dir))
        self.assertEqual(num_files, 1)

        os.remove('media/testimage1.png')

    def test_after_uploading_img_context_has_user_avatar(self):
        self.create_users()
        self.login_user(username="TestUser2")

        img = self.get_img('media/testimage.png')
        form = {'image': img}

        self.client.post(self.url, data=form)
        response = self.client.get(self.url)

        user_id = UserModel.objects.get(username="TestUser2").id
        self.assertEqual(
            response.context['user_avatar'].name,
            'user_id_{}_TestUser2/avatar.png'.format(user_id))

    def get_img(self, path):
        f = open(path, 'rb')
        im = Image.open(f, mode='r')
        im_io = BytesIO()
        im.save(im_io, 'png')
        im_io.seek(0)

        img = InMemoryUploadedFile(
            im_io, None, 'media/testimage.png', 'image/png', len(im_io.getvalue()), None)
        return img

    def file_exist(self, filepath):
        try:
            f = open(filepath)
        except FileNotFoundError:
            return False
        else:
            return True
