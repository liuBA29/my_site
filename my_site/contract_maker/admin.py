from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import Contract, Customer, WorkType


class ContractInline(admin.TabularInline):
    model = Contract
    extra = 0
    show_change_link = True
    fields = ("contract_number", "doc_date", "total_cost", "created_at")
    readonly_fields = ("contract_number", "doc_date", "total_cost", "created_at")
    ordering = ("-created_at",)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("org_name", "client_type_label", "rep_name", "unp", "created_at", "created_by")
    list_filter = ("client_type", "created_at")
    inlines = [ContractInline]

    def client_type_label(self, obj):
        return obj.get_client_type_display()
    client_type_label.short_description = "Статус"

    search_fields = ("org_name", "rep_name", "unp", "address")
    ordering = ("org_name",)


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = (
        "contract_number",
        "doc_date",
        "customer",
        "total_cost",
        "created_at",
        "created_by",
        "download_links",
    )
    list_filter = ("created_at", "is_prepay", "customer")
    list_select_related = ("customer",)
    search_fields = ("contract_number", "doc_date", "customer_data")
    readonly_fields = (
        "contract_number",
        "doc_date",
        "act_date",
        "location",
        "total_cost",
        "work_list",
        "customer_data",
        "contract_filename",
        "act_filename",
        "payment_percent",
        "is_prepay",
        "created_at",
        "created_by",
    )
    date_hierarchy = "created_at"
    autocomplete_fields = ("customer",)

    def download_links(self, obj):
        if not obj.contract_filename and not obj.act_filename:
            return "—"
        links = []
        if obj.contract_filename:
            url = reverse("contract_maker:download", args=[obj.contract_filename])
            links.append(f'<a href="{url}" target="_blank">Договор</a>')
        if obj.act_filename:
            url = reverse("contract_maker:download", args=[obj.act_filename])
            links.append(f'<a href="{url}" target="_blank">Акт</a>')
        return mark_safe(" | ".join(links)) if links else "—"

    download_links.short_description = "Скачать"


@admin.register(WorkType)
class WorkTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "order")
    list_editable = ("order",)
    ordering = ("order", "name")
    search_fields = ("name",)
