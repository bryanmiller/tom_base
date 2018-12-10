from django.shortcuts import render

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView, DeleteView, CreateView, UpdateView
from django_filters.views import FilterView
from django.views.generic import View, ListView
from django.views.generic.detail import DetailView
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from django.core.cache.utils import make_template_fragment_key

from .models import DataProduct, DataProductGroup
from .forms import AddProductToGroupForm, DataProductUploadForm
from tom_targets.models import Target
from tom_observations.models import ObservationRecord
from tom_observations.facility import get_service_class

class DataProductSaveView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        service_class = get_service_class(request.POST['facility'])
        observation_record = ObservationRecord.objects.get(pk=kwargs['pk'])
        products = request.POST.getlist('products')
        if products[0] == 'ALL':
            products = service_class.save_data_products(observation_record, request=self.request)
            messages.success(request, 'Saved all available data products')
        else:
            for product in products:
                products = service_class.save_data_products(observation_record, product, request=self.request)
                messages.success(request, 'Successfully saved: {0}'.format('\n'.join([str(p) for p in products])))
        return redirect(reverse('tom_observations:detail', kwargs={'pk': observation_record.id}))


class DataProductTagView(LoginRequiredMixin, UpdateView):
    model = DataProduct
    fields = ['tag']
    template_name = 'tom_dataproducts/dataproduct_tag.html'

    def get_success_url(self):
        observation_id = self.object.observation_record.id
        return reverse('tom_observations:detail', kwargs={'pk': observation_id})


class ManualDataProductUploadView(LoginRequiredMixin, FormView):
    form_class = DataProductUploadForm
    template_name = 'tom_dataproducts/dataproduct_import.html'

    def get_success_url(self):
        return reverse('tom_observations:detail', kwargs={'pk': self.kwargs.get('pk', None)})

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            observation_record = form.cleaned_data['observation_record']
            tag = form.cleaned_data['tag']
            data_product_files = request.FILES.getlist('files')
            for f in data_product_files:
                dp = DataProduct(target=observation_record.target, observation_record=observation_record, data=f, product_id=None, tag=tag)
                dp.save()
            return super().form_valid(form)
        else:
            return super().form_invalid(form)


class DataProductDeleteView(LoginRequiredMixin, DeleteView):
    model = DataProduct

    #TODO: check success url
    def get_success_url(self):
        return reverse('tom_observations:detail', kwargs={'pk': self.object.observation_record.id})

    def delete(self, request, *args, **kwargs):
        self.get_object().data.delete()
        return super().delete(request, *args, **kwargs)


class DataProductListView(FilterView):
    model = DataProduct
    template_name = 'tom_dataproducts/dataproduct_list.html'
    paginate_by = 25
    filterset_fields = ['target__name', 'observation_record__facility']
    strict = False

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['product_groups'] = DataProductGroup.objects.all()
        return context


class DataProductFeatureView(View):
    def get(self, request, *args, **kwargs):
        product_id = kwargs.get('pk', None)
        product = DataProduct.objects.get(pk=product_id)
        try:
            current_featured = DataProduct.objects.get(featured=True, tag=product.tag)
            current_featured.featured = False
            current_featured.save()
            featured_image_cache_key = make_template_fragment_key('featured_image', str(current_featured.target.id))
            cache.delete(featured_image_cache_key)
        except DataProduct.DoesNotExist:
            pass
        product.featured = True
        product.save()
        return redirect(reverse('tom_targets:detail', kwargs={'pk': request.GET.get('target_id')}))


class DataProductGroupDetailView(DetailView):
    model = DataProductGroup

    def post(self, request, *args, **kwargs):
        group = self.get_object()
        for product in request.POST.getlist('products'):
            group.dataproduct_set.remove(DataProduct.objects.get(pk=product))
        group.save()
        return redirect(reverse('tom_dataproducts:data-group-detail', kwargs={'pk': group.id}))


class DataProductGroupListView(ListView):
    model = DataProductGroup


class DataProductGroupCreateView(LoginRequiredMixin, CreateView):
    model = DataProductGroup
    success_url = reverse_lazy('tom_dataproducts:data-group-list')
    fields = ['name']


class DataProductGroupDeleteView(LoginRequiredMixin, DeleteView):
    success_url = reverse_lazy('tom_dataproducts:data-group-list')
    model = DataProductGroup


class GroupDataView(LoginRequiredMixin, FormView):
    form_class = AddProductToGroupForm
    template_name = 'tom_dataproducts/add_product_to_group.html'

    def form_valid(self, form):
        group = form.cleaned_data['group']
        group.dataproduct_set.add(*form.cleaned_data['products'])
        group.save()
        return redirect(reverse('tom_dataproducts:data-group-detail', kwargs={'pk': group.id}))
