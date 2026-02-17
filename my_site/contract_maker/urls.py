from django.urls import path
from . import views

app_name = "contract_maker"

urlpatterns = [
    path("", views.contract_maker_form, name="form"),
    path("contracts/", views.contract_list, name="contract_list"),
    path("contracts/<int:pk>/edit/", views.contract_edit, name="contract_edit"),
    path("contracts/<int:pk>/delete/", views.contract_delete, name="contract_delete"),
    path("act-for-contract/", views.act_for_contract, name="act_for_contract"),
    path("api/customer/add/", views.api_add_customer, name="api_add_customer"),
    path("preview/", views.contract_maker_preview, name="preview"),
    path("preview/generate-act/", views.preview_generate_act, name="preview_generate_act"),
    path("save-preview/", views.contract_maker_save_preview, name="save_preview"),
    path("success/", views.contract_maker_success, name="success"),
    path("download/<str:filename>", views.contract_maker_download, name="download"),
]
