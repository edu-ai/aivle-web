from django.contrib.auth.models import User
from django.db import models


class Course(models.Model):
    class Meta:
        unique_together = (('code', 'academic_year', 'semester'),)
        permissions = [
            ("view_invisible_course", "Can view invisible courses")
        ]

    code = models.CharField(max_length=6)
    academic_year = models.CharField(max_length=30)
    semester = models.PositiveSmallIntegerField()
    visible = models.BooleanField(default=True)
    participants = models.ManyToManyField(
        User,
        through='Participation',
        through_fields=('course', 'user'),
    )
    use_whitelist = models.BooleanField(default=False)

    def __str__(self):
        return "{} - {} Semester {}".format(self.code, self.academic_year, self.semester)

    def __eq__(self, other):
        if not isinstance(other, Course):
            return False
        return self.code == other.code and self.academic_year == other.academic_year and self.semester == other.semester

    def __hash__(self):
        return hash((self.code, self.academic_year, self.semester))
