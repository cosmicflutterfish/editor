import json
import uuid

from django.conf import settings
from django.core import serializers
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, HttpResponseServerError
from django.forms.models import model_to_dict
from django.shortcuts import render
from django.template import loader, Context
from django.views.generic import CreateView, DeleteView, DetailView, FormView, ListView, UpdateView
from django.views.generic import View

from editor.forms import ExamForm, NewExamForm, ExamQuestionFormSet, ExamSearchForm, QuestionForm
from editor.models import Exam, ExamQuestion, Question
from editor.views.generic import SaveContentMixin, Preview
from extra_views import InlineFormSet, UpdateWithInlinesView

class ExamPreviewView(DetailView, Preview):
    
    """Exam preview."""
    
    model = Exam
    
    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            try:
                e = self.get_object()
                e.content = request.POST['content']
                exam_question_form = ExamQuestionFormSet(
                    request.POST, instance=e)
                # Don't like this...
                if not exam_question_form.is_valid():
                    message = 'Error in examquestion form'
                    return HttpResponseServerError(message)
                exam_question_form.save(commit=False)
                questions = []
                for eq in exam_question_form.cleaned_data:
                    if eq:
                        questions.append(eq['question'])
                        
                # Strip off the final brace.  The template adds it back in.
                e.content = e.content.rstrip()[:-1]
                t = loader.get_template('temporary.exam')
                c = Context({
                    'exam': e,
                    'questions': questions
                })
            except Exam.DoesNotExist:
                message = 'No such exam exists in the database.'
                return HttpResponseServerError(message)
            return self.preview_compile(t, c, e.filename)
        raise Http404
    
    def get(self, request, *args, **kwargs):
        raise Http404
    
    
def testview(request):
    """For testing."""
    if request.method == 'POST':
        form = ExamForm(request.POST)
        print ExamQuestionFormSet(request.POST)
        inlines = [ExamQuestionFormSet(request.POST)]
        if form.is_valid():
            for formset in inlines:
                if formset.is_valid():
                    print "valid"
    else:
        form = ExamForm()
        inlines = [ExamQuestionFormSet()]
    return render(request, 'exam/new.html', {'form': form, 'inlines': inlines})


class ExamQuestionInline(InlineFormSet):
    
    """Inline ExamQuestion view, to be used in Exam views."""
    
    model = ExamQuestion
#    form_class = ExamQuestionForm
#    extra = 0
    

class ExamCreateView(CreateView, SaveContentMixin):
    
    """Create an exam."""
    
    model = Exam
    form_class = NewExamForm
    template_name = 'exam/new.html'
    
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.content = "{name: %s}" % self.object.name
        self.object.filename = str(uuid.uuid4())
        return self.write_content(settings.GLOBAL_SETTINGS['EXAM_SUBDIR'],
                                  form)
    
    def get_success_url(self):
        return reverse('exam_edit', args=(self.object.pk,self.object.slug,))
    
        
class ExamDeleteView(DeleteView):
    
    """Delete an exam."""
    
    model = Exam
    template_name = 'exam/delete.html'
    
    def get_success_url(self):
        return reverse('exam_index')
    
    
class ExamUpdateView(UpdateView, SaveContentMixin):
    
    """Edit an exam."""
    
    model = Exam
    template_name = 'exam/edit.html'
    
    def post(self, request, *args, **kwargs):
        request.JSON = json.loads(request.POST['json'])
#        print(json.loads(request.POST['json']))
        exam = self.get_object()
#        print(exam)
        exam.content = request.JSON['content']
        exam.save()
        questions = request.JSON['questions']
        exam.questions.clear() 
        for i,q in enumerate(questions):
            question = Question.objects.get(pk=q['id'])
            exam_question = ExamQuestion(exam=exam, question=question, qn_order=i)
            exam_question.save()
        return HttpResponse('success')
        
#    def get(self, request, *args, **kwargs):
#        self.object = self.get_object()
#        print(self.object)
    
#    def forms_valid(self, form, inlines):
#        self.object = form.save(commit=False)
#        return self.write_content(settings.GLOBAL_SETTINGS['EXAM_SUBDIR'],
#                                  form, inlines=inlines)
#        
    def get_context_data(self, **kwargs):
        context = super(ExamUpdateView, self).get_context_data(**kwargs)
        context['exam_JSON'] = json.dumps(model_to_dict(self.object))
#        context['exam_JSON'] = serializers.serialize('json', [self.object])
#        print(context['exam_JSON'])
        return context
#    
    def get_success_url(self):
        return reverse('exam_edit', args=(self.object.pk,self.object.slug,))
    
    
class ExamSearchView(FormView):
    
    """Search for an exam."""
    
    form_class = ExamSearchForm
    template_name = 'exam/search.html'
    
    def form_valid(self, form):
#        exam = form.cleaned_data['name']
        exam_list = Exam.objects.filter(
            name__icontains=form.cleaned_data['name'])
        return render(self.request, 'exam/index.html', {'exam_list': exam_list})
    
    
class ExamListView(ListView):
    model=Exam
    template_name='exam/index.html'

#    def get_queryset(self):
#        if 'exam' in self.kwargs:
#            print "hello"
#        return Exam.objects.all()
