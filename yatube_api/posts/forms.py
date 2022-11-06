from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    """Post creation form class."""

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Текст поста',
            'group': 'Группа'
        }
        help_texts = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост'
        }
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control'}),
            'group': forms.Select(attrs={'class': 'form-control'})
        }

    def clean_text(self):
        """Clean-function for field 'text'."""
        text = self.cleaned_data['text']
        if not text or text.isspace():
            raise forms.ValidationError('Необходимо заполнить текст поста!')

        return text


class CommentForm(forms.ModelForm):
    """Comment creation form class."""

    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control'})
        }

    def clean_text(self):
        """Clean-function for field 'text'."""
        text = self.cleaned_data['text']
        if not text or text.isspace():
            raise forms.ValidationError('Текст комментария не заполнен!')

        return text
