# coding=utf-8
from django.apps import apps
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import FieldDoesNotExist, PermissionDenied
from django.db import models, transaction
from django.db.models import Q
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _

# Inline formset mixins (for CreateView / UpdateView)
class MultipleInlineFormsetMixin:
    """
    Handle MULTIPLE inline formsets on a CreateView / UpdateView.

    Usage:
        inline_formsets = [
            {
                'model': ChildModel,          # class or 'app_label.ModelName'
                'form': ChildModelForm,       # optional
                'extra': 1,
                'can_delete': True,
                'formset_name': 'child_formset',   # context variable name
                'fk_name': 'parent',          # optional, needed if ambiguous
            }
        ]
    """
    inline_formsets = []
    priority_fields = ('user',)                       # FK names preferred when ambiguous
    audit_fields = ('created_by', 'updated_by', 'deleted_by')

    def get_model_class(self, model_config):
        """Convert 'app.Model' string to a model class."""
        if isinstance(model_config, str):
            try:
                app_label, model_name = model_config.split('.')
            except ValueError:
                raise ValueError(
                    f"Model string '{model_config}' must be in format "
                    f"'app_name.ModelName'"
                )
            return apps.get_model(app_label, model_name)
        return model_config

    def get_foreign_key_field(self, formset_config):
        """Find the FK on the child model that points to the parent model."""
        if formset_config.get('fk_name'):
            return formset_config['fk_name']

        model = self.get_model_class(formset_config['model'])
        parent_model = self.model

        candidates = [
            f for f in model._meta.get_fields()
            if isinstance(f, models.ForeignKey) and f.related_model == parent_model
        ]
        # Ignore audit fields (created_by...) unless they are the only choice.
        pool = [f for f in candidates if f.name not in self.audit_fields] or candidates

        if len(pool) == 1:
            return pool[0].name

        one_to_ones = [f for f in pool if isinstance(f, models.OneToOneField)]
        if len(one_to_ones) == 1:
            return one_to_ones[0].name

        for name in self.priority_fields:
            for f in pool:
                if f.name == name:
                    return name

        raise ValueError(
            f"Could not determine the foreign key in {model.__name__} "
            f"that points to {parent_model.__name__} "
            f"({len(pool)} candidates). Please specify 'fk_name' in your "
            f"formset configuration."
        )

    def create_formset_class(self, formset_config):
        """Build a formset class from a config dict."""
        model = self.get_model_class(formset_config['model'])
        fk_name = self.get_foreign_key_field(formset_config)

        factory_kwargs = dict(
            parent_model=self.model,
            model=model,
            extra=formset_config.get('extra', 1),
            can_delete=formset_config.get('can_delete', True),
            can_order=formset_config.get('can_order', False),
            max_num=formset_config.get('max_num'),
            min_num=formset_config.get('min_num'),
            validate_max=formset_config.get('validate_max', False),
            validate_min=formset_config.get('validate_min', False),
            fk_name=fk_name,
        )

        if formset_config.get('form'):
            factory_kwargs['form'] = formset_config['form']

        if formset_config.get('exclude'):
            factory_kwargs['exclude'] = formset_config['exclude']
        else:
            factory_kwargs['fields'] = formset_config.get('fields', '__all__')

        return inlineformset_factory(**factory_kwargs)

    def get_formset_instances(self):
        """
        Build formsets once and cache them, so get_context_data, form_valid
        and form_invalid all share the same instances (data + errors).
        """
        if not hasattr(self, '_formset_instances'):
            instances = {}
            parent = getattr(self, 'object', None)
            for config in self.inline_formsets:
                name = config.get('formset_name')
                if not name:
                    raise ValueError(
                        "Each formset configuration must have a 'formset_name'"
                    )
                formset_class = self.create_formset_class(config)
                if self.request.method == 'POST':
                    instances[name] = formset_class(
                        self.request.POST, self.request.FILES, instance=parent
                    )
                else:
                    instances[name] = formset_class(instance=parent)
            self._formset_instances = instances
        return self._formset_instances

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data.update(self.get_formset_instances())
        return data

    def form_valid(self, form):
        formsets = self.get_formset_instances()
        if not formsets:
            return super().form_valid(form)

        # Use a list (not a generator) so EVERY formset is validated and
        # shows its errors, instead of stopping at the first invalid one.
        if not all([fs.is_valid() for fs in formsets.values()]):
            return self.form_invalid(form)

        with transaction.atomic():
            # super() saves the parent once, sets self.object, builds redirect
            # (and keeps the MRO chain intact for e.g. SuccessMessageMixin).
            response = super().form_valid(form)
            for fs in formsets.values():
                fs.instance = self.object
                fs.save()
        return response

    def form_invalid(self, form):
        # Validate formsets too so their errors appear with the main form's.
        for fs in self.get_formset_instances().values():
            fs.is_valid()
        return super().form_invalid(form)


# ---------------------------------------------------------------------------
# Extra (non-inline) forms on the same page
# ---------------------------------------------------------------------------
class MultiFormMixin:
    """
    Put extra forms next to the main form on the same page.

    Config:
        inline_forms_config = [
            {'form_class': FormClass, 'prefix': '...', 'context_name': '...'}
        ]

    NOTE: this mixin only BUILDS the forms (bound on POST) and adds them to
    the template context. Validating / saving them is the view's job.
    """
    inline_forms_config = []

    def get_inline_forms(self):
        # Cached so the same bound forms (with errors) are reused.
        if not hasattr(self, '_inline_forms_cache'):
            cache = {}
            for config in self.inline_forms_config:
                form_class = config['form_class']
                prefix = config.get('prefix')
                if self.request.method == 'POST':
                    cache[config['context_name']] = form_class(
                        self.request.POST, self.request.FILES, prefix=prefix
                    )
                else:
                    cache[config['context_name']] = form_class(prefix=prefix)
            self._inline_forms_cache = cache
        return self._inline_forms_cache

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_inline_forms())
        return context


# ---------------------------------------------------------------------------
# List view: search + status filter
# ---------------------------------------------------------------------------
class SearchFilterMixin:
    """
    Generic search / status filter for list views.

    View attributes:
        model
        search_fields   - e.g. ['name', 'customer__name']
        status_field    - model field to filter on
        status_param    - GET parameter name (defaults to status_field)
        status_choices  - choices shown in the status dropdown
        default_status  - status applied when none is given
        list_display    - fields shown as table headers
    """
    status_field = 'status'
    status_param = None
    search_param = 'search'
    search_fields = ()
    status_choices = ()
    default_status = None
    list_display = ()

    def get_status_param(self):
        return self.status_param or self.status_field

    def get_current_status(self):
        return self.request.GET.get(self.get_status_param()) or self.default_status

    def get_verbose_name(self, model, field_path):
        """Verbose name of a field; supports nested paths like 'a__b'."""
        try:
            parts = field_path.split('__')
            field = model._meta.get_field(parts[0])
            if len(parts) > 1 and field.is_relation:
                return self.get_verbose_name(field.related_model, '__'.join(parts[1:]))
            return field.verbose_name
        except (FieldDoesNotExist, AttributeError):
            return field_path.replace('__', ' ').replace('_', ' ').capitalize()

    def get_queryset(self):
        queryset = super().get_queryset()

        status = self.get_current_status()
        if status:
            queryset = queryset.filter(**{self.status_field: status})

        search_query = self.request.GET.get(self.search_param, '').strip()
        if search_query and self.search_fields:
            q_obj = Q()
            for field in self.search_fields:
                q_obj |= Q(**{f"{field}__icontains": search_query})
            # distinct(): searching across relations can return duplicate rows
            queryset = queryset.filter(q_obj).distinct()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['status_choices'] = self.status_choices
        context['current_status'] = self.get_current_status()
        context['status_field'] = self.status_field
        context['status_param'] = self.get_status_param()

        context['search_param'] = self.search_param
        context['search_query'] = self.request.GET.get(self.search_param, '')

        if self.list_display:
            context['headers'] = [
                {'field': field, 'label': self.get_verbose_name(self.model, field)}
                for field in self.list_display
            ]
        return context
