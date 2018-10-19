# forms.py

# django
from django import forms
from apps.models import models
# project
from apps.models.fields import GroupedModelChoiceField


class ContactForm(forms.Form):
    """ Form to create a list. """

    subject = forms.CharField(label="Subject", required=True,
              help_text="Email subject.")
    body    = forms.CharField(label="Body", required=True, widget=forms.Textarea,
              help_text="Email content.")


class ListCreateForm(forms.Form):
    """ Form to create a list. """

    name        = forms.CharField(label="List name", required=True)
    body        = forms.CharField(label="Description", required=False, widget=forms.Textarea,
                  help_text="Provide an optional description for your list.")
    public      = forms.BooleanField(label="Public", initial=True,
                  help_text="Check if you want the list to be publicly visible.")

class ListItemCreateForm(forms.Form):
    """ Form to add items to lists. """

    def group_label(user):
        """ Function to create the label of the optgroups in list field. """
        return user.username

    # fields
    list    = GroupedModelChoiceField(queryset=models.CuratedList.objects.order_by('user', 'name'),
                                      label='Add/suggest to', group_by_field='user', group_label=group_label,
                                      empty_label='Please select a list')
    comment = forms.CharField(label="Comment", required=False, widget=forms.Textarea, help_text="An optional comment that will be displayed under "
                              "the item in the list.")
    suggestion = forms.CharField(label="Suggestion comment", required=False, widget=forms.Textarea, help_text=" If the list is not yours "
                                 "use this field to comment to the owner why do "
                                 "you think this item might be included in the list. Provide email or other mean of communication to "
                                 "ease further discussion.")
    public = forms.BooleanField(label="Public", initial=True, required=False)

    def __init__(self, *args, **kwargs):
        self.user    = kwargs.pop('user')
        self.item_pk = kwargs.pop('item_pk')
        self.item_ct = kwargs.pop('item_ct')
        super(ListItemCreateForm, self).__init__(*args, **kwargs)

    def clean_suggestion(self):
        list       = self.cleaned_data.get('list')
        suggestion = self.cleaned_data.get('suggestion')
        if list.user == self.user and suggestion:
            raise forms.ValidationError('This field is useless if you\'re the owner of the list.')
        if list.user != self.user and not suggestion:
            raise forms.ValidationError('If you\'re not the owner of the list you should comment why do you suggest this content item.')
        return suggestion

    def clean_comment(self):
        list       = self.cleaned_data.get('list')
        comment = self.cleaned_data.get('comment')
        if list.user != self.user and comment:
            raise forms.ValidationError('Comments are reserved for list owners.')
        return comment

    def clean(self):
        list     = self.cleaned_data.get('list')
        item_already_exists = models.CuratedListElement.objects.filter(
            list         = list,
            content_type = self.item_ct,
            object_id    = self.item_pk,
        ).exists()
        if item_already_exists:
            raise forms.ValidationError('That item already exists in that list.')
        return self.cleaned_data

class ListLinkCreateForm(forms.Form):
    """ Form to add items to lists. """

    # fields
    url     = forms.URLField(label="URL", required=True)
    title   = forms.CharField(label="Title", required=True)
    comment = forms.CharField(label="Comment", required=False, widget=forms.Textarea, help_text="An optional comment that will be displayed under "
                              "the item in the list. If the list is not yours "
                              "use this field to comment to the owner why do "
                              "you think this item might be included in the list")

class ListLinkUpdateForm(forms.Form):
    """ Form to add items to lists. """

    # fields
    url     = forms.URLField(label="URL", required=True)
    title   = forms.CharField(label="Title", required=True)
    comment = forms.CharField(label="Comment", required=False, widget=forms.Textarea, help_text="An optional comment that will be displayed under "
                              "the item in the list. If the list is not yours "
                              "use this field to comment to the owner why do "
                              "you think this item might be included in the list")
    date    = forms.DateField(label="Date", required=False,
              help_text="The date the item was included in the list, in the format YYYY-MM-DD. The items are displayed in chronological order using this date. You can tweak the dates to change the sort order.")
    public  = forms.BooleanField(label="Public", required=False,
              help_text="Check if you want the list to be publicly visible.")
