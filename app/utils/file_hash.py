import hashlib

from django.core.files.storage import default_storage
from django.db import models


class ExtraFileField(models.FileField):
    def __init__(self, verbose_name=None, name=None, upload_to='', after_file_save=None, storage=None, **kwargs):
        self.after_file_save = after_file_save
        super().__init__(verbose_name, name, upload_to=upload_to, storage=storage or default_storage, **kwargs)

    def pre_save(self, model_instance, add):
        file = super().pre_save(model_instance, add)
        self.after_file_save(model_instance)
        return file


def hash_file(file, block_size=65536):
    hasher = hashlib.md5()
    while True:
        data = file.read(block_size)
        if not data:
            break
        hasher.update(data)
    return hasher.hexdigest()


def make_safe_filename(s):
    def safe_char(c):
        if c.isalnum():
            return c
        else:
            return "_"

    return "".join(safe_char(c) for c in s).rstrip("_")


def submission_path(instance, filename):
    return 'courses/{}/tasks/{}/submissions/{}/{}'.format(
        instance.task.course.id, make_safe_filename(instance.task.name), instance.user.id, filename
    )


def task_grader_path(instance, filename):
    return 'courses/{}/tasks/{}/grader/{}'.format(
        instance.course.id, make_safe_filename(instance.name), filename
    )


def task_template_path(instance, filename):
    return 'courses/{}/tasks/{}/template/{}'.format(
        instance.course.id, make_safe_filename(instance.name), filename
    )


def compute_file_hash(instance):
    with instance.file.open():
        instance.file_hash = hash_file(instance.file)
