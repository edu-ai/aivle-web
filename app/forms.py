from django import forms
from django.forms.widgets import HiddenInput
from bootstrap_datepicker_plus import DateTimePickerInput
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from .models import Task, Submission, Course

class HideableForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        hidden = kwargs.pop('hidden', False)
        super().__init__(*args, **kwargs)
        if hidden:
            for fieldname in self.Meta.fields:
                self.fields[fieldname].widget = HiddenInput()

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'description', 'daily_submission_limit', 'runtime_limit', 'max_upload_size', 'opened_at', 'closed_at', 'leaderboard']
        labels = {
            "max_upload_size": "Max upload size (KB)",
        }
        widgets = {
            'opened_at': DateTimePickerInput().start_of('open range'),
            'closed_at': DateTimePickerInput().end_of('open range'),
        }

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name', 
            'description', 
            Row(
                Column('daily_submission_limit', css_class='col-4'), 
                Column('runtime_limit', css_class='col-4'), 
                Column('max_upload_size', css_class='col-4'), css_class="row"),
            Row(
                Column('opened_at', css_class='col-6'), 
                Column('closed_at', css_class='col-6'), css_class="row"),
            'leaderboard',
            Submit('submit', 'Submit', css_class="btn btn-success")
        )
        super().__init__(*args, **kwargs)


class SubmissionForm(forms.ModelForm):
    runner = forms.ChoiceField(choices=Submission.RUNNERS)

    class Meta:
        model = Submission
        fields = ['runner', 'file', 'metadata', 'description']
        labels = {
            "file": "File (.zip)",
        }
        widgets = {
            'file': forms.FileInput(attrs={'accept':'application/zip', 'class': 'clearablefileinput form-control'}),
            'metadata': forms.Textarea(attrs={'rows': 4})
        }

    def show_file_error(self):
        # Hack: fix inherent bug error not showing on file field
        self.fields['file'].widget.attrs['class'] =  'clearablefileinput form-control is-invalid'

    def clean(self):
        cleaned_data = super(SubmissionForm, self).clean()
        metadata = cleaned_data.get('metadata', False)
        file = cleaned_data.get('file', False)
        runner = cleaned_data.get('runner', False)
        if not metadata and runner == Submission.RUNNER_DOCKER:
            raise forms.ValidationError({'metadata': 'Metadata required for Docker runner.'}, code='metadata_required')
        if not file and runner == Submission.RUNNER_PYTHON:
            self.show_file_error()
            raise forms.ValidationError({'file': 'File required for Python runner.'}, code='file_required')

    def clean_file(self):
        file = self.cleaned_data.get('file', False)
        runner = self.cleaned_data.get('runner', False)
        if file: 
            message = None
            if file.size > self.instance.task.max_upload_size * 1024:
                message = "File size is too large ({}KB > {}KB).".format(round(file.size/1024), self.instance.task.max_upload_size)
            if file.content_type != 'application/zip':
                message = "File type is not supported."
            if message:
                show_file_error()
                raise forms.ValidationError(message, code='file_requirement_error')
        return file

class CourseForm(HideableForm):
    class Meta:
        model = Course
        fields = ('code', 'academic_year', 'semester')