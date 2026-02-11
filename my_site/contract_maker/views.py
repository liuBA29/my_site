# Генератор договоров и актов — только для авторизованных staff/суперпользователя
import os
import uuid
from datetime import date
from pathlib import Path

import json

from django.conf import settings
from django.contrib import messages
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.urls import reverse

from .forms import ActForContractForm, ContractEditForm, ContractMakerForm, ContractManualForm, CustomerForm
from .models import Contract, Customer, WorkType
from . import generator_config
from .document_generator import generate_contract, generate_act


def _staff_required(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def _get_customers_queryset():
    """Список клиентов для выбора (текущий пользователь + общие)."""
    return Customer.objects.all().order_by("org_name")


def _json_response(data, status=200):
    return HttpResponse(
        json.dumps(data, ensure_ascii=False),
        content_type="application/json; charset=utf-8",
        status=status,
    )


@csrf_exempt
@require_http_methods(["POST"])
def api_add_customer(request):
    """
    Тестовый API для бота: добавить клиента. POST JSON.
    Тело: {"org_name": "ООО Рога", "client_type": "legal", "rep_name": "...", ...}
    Опционально заголовок X-Bot-Token или поле "token" в JSON (значение из CONTRACT_MAKER_BOT_TOKEN).
    Потом убрать.
    """
    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return _json_response({"ok": False, "error": "Invalid JSON"}, status=400)

    token = getattr(settings, "CONTRACT_MAKER_BOT_TOKEN", None)
    if token:
        header_token = request.headers.get("X-Bot-Token")
        body_token = body.get("token")
        if header_token != token and body_token != token:
            return _json_response({"ok": False, "error": "Invalid token"}, status=403)

    org_name = (body.get("org_name") or "").strip()
    if not org_name:
        return _json_response({"ok": False, "error": "org_name is required"}, status=400)

    client_type = body.get("client_type") or Customer.CLIENT_TYPE_LEGAL
    if client_type not in (Customer.CLIENT_TYPE_INDIVIDUAL, Customer.CLIENT_TYPE_LEGAL):
        client_type = Customer.CLIENT_TYPE_LEGAL

    customer = Customer(
        client_type=client_type,
        org_name=org_name,
        rep_position=(body.get("rep_position") or "").strip()[:100],
        rep_name=(body.get("rep_name") or "").strip()[:255],
        basis=(body.get("basis") or "Устава").strip()[:255],
        short_name=(body.get("short_name") or "").strip()[:100],
        address=(body.get("address") or "").strip()[:500],
        unp=(body.get("unp") or "").strip()[:20],
        okpo=(body.get("okpo") or "").strip()[:20],
        iban=(body.get("iban") or "").strip()[:50],
        created_by=None,
    )
    customer.save()
    return _json_response({
        "ok": True,
        "id": customer.pk,
        "org_name": customer.org_name,
    })


@login_required
@user_passes_test(_staff_required, login_url="/accounts/login/")
def contract_maker_form(request):
    """Страница с формой: ввод данных заказчика и параметров договора/акта."""
    customers = _get_customers_queryset()

    if request.method == "POST":
        form = ContractMakerForm(customers_queryset=customers, data=request.POST)
        if form.is_valid():
            customer_obj = form.cleaned_data["customer"]
            customer = customer_obj.to_customer_dict()
            contract_number = form.cleaned_data["contract_number"].strip()
            doc_date = form.cleaned_data["doc_date"].strip()
            act_date = (form.cleaned_data.get("act_date") or "").strip() or doc_date
            location = form.cleaned_data["location"].strip()
            total_cost = float(form.cleaned_data["total_cost"])
            for new_name in form.get_work_list_extra_parsed():
                if new_name:
                    WorkType.objects.get_or_create(name=new_name)
            work_list = form.get_work_list()
            payment_percent = form.cleaned_data.get("payment_percent") or 100
            is_prepay = form.cleaned_data.get("is_prepay", True)

            save_dir = generator_config.OUTPUT_DIR
            contract_filename = ""
            act_filename = ""

            try:
                path_contract = generate_contract(
                        customer=customer,
                        work_list=work_list,
                        contract_number=contract_number,
                        doc_date=doc_date,
                        location=location,
                        total_cost=total_cost,
                        payment_percent=payment_percent,
                        is_prepay=is_prepay,
                        save_dir=save_dir,
                    )
                contract_filename = os.path.basename(path_contract)
            except Exception as e:
                messages.error(request, f"Ошибка при генерации: {e}")
                form.fields["customer"].queryset = customers
                return render(request, "contract_maker/form.html", {"form": form, "customers": customers})

            request.session["contract_maker_preview"] = {
                "contract_file": contract_filename,
                "act_file": act_filename,
                "contract_number": contract_number,
                "doc_date": doc_date,
                "act_date": act_date,
                "location": location,
                "total_cost": total_cost,
                "work_list": work_list,
                "customer_data": customer,
                "customer_id": customer_obj.pk,
                "payment_percent": payment_percent,
                "is_prepay": is_prepay,
            }
            return redirect(reverse("contract_maker:preview"))
        form.fields["customer"].queryset = customers
        return render(request, "contract_maker/form.html", {"form": form, "customers": customers})

    # GET: опционально подставить выбранного клиента из ?customer=id
    initial = {}
    customer_id = request.GET.get("customer")
    if customer_id:
        try:
            cust = Customer.objects.get(pk=customer_id)
            initial["customer"] = cust
        except (Customer.DoesNotExist, ValueError):
            pass
    form = ContractMakerForm(customers_queryset=customers, initial=initial if initial else None)
    return render(request, "contract_maker/form.html", {"form": form, "customers": customers})


@login_required
@user_passes_test(_staff_required, login_url="/accounts/login/")
def customer_add(request):
    """Добавить клиента в базу. После сохранения — редирект на форму договора с подставленным клиентом."""
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            cust = Customer(
                client_type=form.cleaned_data.get("client_type") or Customer.CLIENT_TYPE_LEGAL,
                org_name=form.cleaned_data["org_name"].strip(),
                rep_position=form.cleaned_data.get("rep_position") or "",
                rep_name=form.cleaned_data.get("rep_name") or "",
                basis=form.cleaned_data.get("basis") or "Устава",
                short_name=form.cleaned_data.get("short_name") or "",
                address=form.cleaned_data.get("address") or "",
                unp=form.cleaned_data.get("unp") or "",
                okpo=form.cleaned_data.get("okpo") or "",
                iban=form.cleaned_data.get("iban") or "",
                created_by=request.user,
            )
            cust.save()
            messages.success(request, "Клиент добавлен в базу.")
            return redirect(reverse("contract_maker:form") + f"?customer={cust.pk}")
        return render(request, "contract_maker/customer_add.html", {"form": form})

    form = CustomerForm()
    return render(request, "contract_maker/customer_add.html", {"form": form})


@login_required
@user_passes_test(_staff_required, login_url="/accounts/login/")
def act_for_contract(request):
    """Создать акт к выбранному договору (у которого ещё нет акта)."""
    if request.method == "POST":
        form = ActForContractForm(request.POST)
        if form.is_valid():
            contract = form.cleaned_data["contract"]
            act_date = (form.cleaned_data.get("act_date") or "").strip() or contract.doc_date
            customer = contract.get_customer_dict()
            work_list = list(contract.work_list) if contract.work_list else ["Услуги по договору"]
            total_cost = float(contract.total_cost)
            save_dir = generator_config.OUTPUT_DIR
            try:
                path_act = generate_act(
                    customer=customer,
                    work_list=work_list,
                    contract_number=contract.contract_number,
                    doc_date=contract.doc_date,
                    act_date=act_date,
                    total_cost=total_cost,
                    save_dir=save_dir,
                )
                act_filename = os.path.basename(path_act)
                contract.act_filename = act_filename
                contract.act_date = act_date
                contract.save(update_fields=["act_filename", "act_date"])
                request.session["contract_maker_last"] = {"act_file": act_filename}
                messages.success(request, "Акт создан и привязан к договору.")
                return redirect(reverse("contract_maker:success"))
            except Exception as e:
                messages.error(request, f"Ошибка при генерации акта: {e}")
        return render(request, "contract_maker/act_for_contract.html", {"form": form})

    initial = {"act_date": date.today().strftime("%d.%m.%Y")}
    form = ActForContractForm(initial=initial)
    return render(request, "contract_maker/act_for_contract.html", {"form": form})


@login_required
@user_passes_test(_staff_required, login_url="/accounts/login/")
def contract_maker_preview(request):
    """Страница предпросмотра: открыть документ для просмотра или сохранить в БД."""
    preview = request.session.get("contract_maker_preview")
    if not preview:
        return redirect(reverse("contract_maker:form"))
    show_act_form = request.GET.get("show_act") == "1"
    return render(request, "contract_maker/preview.html", {"preview": preview, "show_act_form": show_act_form})


@login_required
@user_passes_test(_staff_required, login_url="/accounts/login/")
def preview_generate_act(request):
    """Сформировать акт из данных договора в предпросмотре (только дата акта от пользователя)."""
    if request.method != "POST":
        return redirect(reverse("contract_maker:preview"))
    preview = request.session.get("contract_maker_preview")
    if not preview or not preview.get("contract_file"):
        return redirect(reverse("contract_maker:form"))
    act_date = (request.POST.get("act_date") or "").strip() or preview.get("doc_date", "")
    if not act_date:
        messages.error(request, "Укажите дату акта.")
        return redirect(reverse("contract_maker:preview") + "?show_act=1")
    try:
        path_act = generate_act(
            customer=preview["customer_data"],
            work_list=preview["work_list"],
            contract_number=preview["contract_number"],
            doc_date=preview["doc_date"],
            act_date=act_date,
            total_cost=float(preview["total_cost"]),
            save_dir=generator_config.OUTPUT_DIR,
        )
        act_filename = os.path.basename(path_act)
        preview["act_file"] = act_filename
        preview["act_date"] = act_date
        request.session["contract_maker_preview"] = preview
        request.session.modified = True
        messages.success(request, "Акт сформирован. Данные взяты из договора.")
    except Exception as e:
        messages.error(request, f"Ошибка при генерации акта: {e}")
    return redirect(reverse("contract_maker:preview"))


@login_required
@user_passes_test(_staff_required, login_url="/accounts/login/")
def contract_maker_save_preview(request):
    """Сохранить предпросмотренный документ в БД и перейти на success."""
    if request.method != "POST":
        return redirect(reverse("contract_maker:form"))
    preview = request.session.pop("contract_maker_preview", None)
    if not preview:
        return redirect(reverse("contract_maker:form"))
    customer_id = preview.get("customer_id")
    Contract.objects.create(
        customer_id=customer_id,
        contract_number=preview["contract_number"],
        doc_date=preview["doc_date"],
        act_date=preview["act_date"],
        location=preview["location"],
        total_cost=preview["total_cost"],
        work_list=preview["work_list"],
        customer_data=preview["customer_data"],
        contract_filename=preview.get("contract_file", ""),
        act_filename=preview.get("act_file", ""),
        payment_percent=preview.get("payment_percent"),
        is_prepay=preview.get("is_prepay", True),
        created_by=request.user,
    )
    last = {}
    if preview.get("contract_file"):
        last["contract_file"] = preview["contract_file"]
    if preview.get("act_file"):
        last["act_file"] = preview["act_file"]
    request.session["contract_maker_last"] = last
    return redirect(reverse("contract_maker:success"))


def _save_uploaded_pdf(file_obj, prefix):
    """Сохранить загруженный PDF в OUTPUT_DIR, вернуть имя файла."""
    suffix = (file_obj.name or "file.pdf").lower()
    if not suffix.endswith(".pdf"):
        suffix = "upload.pdf"
    else:
        suffix = suffix[-4:]  # .pdf
    name = f"{prefix}_upload_{uuid.uuid4().hex[:12]}{suffix}"
    path = Path(generator_config.OUTPUT_DIR) / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        for chunk in file_obj.chunks():
            f.write(chunk)
    return name


@login_required
@user_passes_test(_staff_required, login_url="/accounts/login/")
def contract_list(request):
    """Список договоров: просмотр, редактирование, удаление."""
    contracts = Contract.objects.select_related("customer").order_by("-created_at")
    return render(request, "contract_maker/contract_list.html", {"contracts": contracts})


@login_required
@user_passes_test(_staff_required, login_url="/accounts/login/")
def contract_add_manual(request):
    """Добавить договор/акт вручную: загрузить PDF и заполнить данные."""
    customers = _get_customers_queryset()
    if request.method == "POST":
        form = ContractManualForm(customers_queryset=customers, data=request.POST, files=request.FILES)
        if form.is_valid():
            customer_obj = form.cleaned_data["customer"]
            contract_number = form.cleaned_data["contract_number"].strip()
            doc_date = form.cleaned_data["doc_date"].strip()
            act_date = (form.cleaned_data.get("act_date") or "").strip() or doc_date
            location = (form.cleaned_data.get("location") or "").strip() or "—"
            total_cost = form.cleaned_data.get("total_cost") or 0
            work_list = form.cleaned_data["work_list"]

            contract_filename = _save_uploaded_pdf(form.cleaned_data["contract_file"], "contract")
            act_filename = ""
            if form.cleaned_data.get("act_file"):
                act_filename = _save_uploaded_pdf(form.cleaned_data["act_file"], "act")

            Contract.objects.create(
                customer=customer_obj,
                customer_data=customer_obj.to_customer_dict(),
                contract_number=contract_number,
                doc_date=doc_date,
                act_date=act_date,
                location=location,
                total_cost=total_cost,
                work_list=work_list,
                contract_filename=contract_filename,
                act_filename=act_filename,
                created_by=request.user,
            )
            messages.success(request, "Договор и акт добавлены в базу (PDF).")
            return redirect(reverse("contract_maker:contract_list"))
    else:
        form = ContractManualForm(customers_queryset=customers)
    return render(request, "contract_maker/contract_add_manual.html", {"form": form})


@login_required
@user_passes_test(_staff_required, login_url="/accounts/login/")
def contract_edit(request, pk):
    """Редактирование договора (реквизиты, даты, сумма, перечень работ)."""
    try:
        contract = Contract.objects.select_related("customer").get(pk=pk)
    except Contract.DoesNotExist:
        messages.error(request, "Договор не найден.")
        return redirect(reverse("contract_maker:contract_list"))
    customers = _get_customers_queryset()
    if request.method == "POST":
        form = ContractEditForm(customers_queryset=customers, data=request.POST, files=request.FILES)
        if form.is_valid():
            customer_obj = form.cleaned_data["customer"]
            contract.customer = customer_obj
            contract.customer_data = customer_obj.to_customer_dict()
            contract.contract_number = form.cleaned_data["contract_number"].strip()
            contract.doc_date = form.cleaned_data["doc_date"].strip()
            contract.act_date = (form.cleaned_data.get("act_date") or "").strip() or contract.doc_date
            contract.location = form.cleaned_data["location"].strip()
            contract.total_cost = form.cleaned_data["total_cost"]
            contract.work_list = form.cleaned_data["work_list"]
            contract.payment_percent = form.cleaned_data.get("payment_percent") or 100
            contract.is_prepay = form.cleaned_data.get("is_prepay", True)
            if form.cleaned_data.get("contract_file"):
                old_path = Path(generator_config.OUTPUT_DIR) / contract.contract_filename if contract.contract_filename else None
                contract.contract_filename = _save_uploaded_pdf(form.cleaned_data["contract_file"], "contract")
                if old_path and old_path.is_file():
                    try:
                        old_path.unlink()
                    except OSError:
                        pass
            if form.cleaned_data.get("act_file"):
                old_path = Path(generator_config.OUTPUT_DIR) / contract.act_filename if contract.act_filename else None
                contract.act_filename = _save_uploaded_pdf(form.cleaned_data["act_file"], "act")
                if old_path and old_path.is_file():
                    try:
                        old_path.unlink()
                    except OSError:
                        pass
            contract.save()
            messages.success(request, "Договор сохранён.")
            return redirect(reverse("contract_maker:contract_list"))
    else:
        work_list_text = "\n".join(contract.work_list) if contract.work_list else ""
        form = ContractEditForm(
            customers_queryset=customers,
            initial={
                "customer": contract.customer,
                "contract_number": contract.contract_number,
                "doc_date": contract.doc_date,
                "act_date": contract.act_date or contract.doc_date,
                "location": contract.location,
                "total_cost": contract.total_cost,
                "work_list": work_list_text,
                "payment_percent": contract.payment_percent or 100,
                "is_prepay": contract.is_prepay,
            },
        )
    return render(request, "contract_maker/contract_edit.html", {"form": form, "contract": contract})


@login_required
@user_passes_test(_staff_required, login_url="/accounts/login/")
def contract_delete(request, pk):
    """Удаление договора и привязанных файлов."""
    try:
        contract = Contract.objects.get(pk=pk)
    except Contract.DoesNotExist:
        messages.error(request, "Договор не найден.")
        return redirect(reverse("contract_maker:contract_list"))
    if request.method == "POST":
        for name in (contract.contract_filename, contract.act_filename):
            if name:
                path = Path(generator_config.OUTPUT_DIR) / name
                if path.is_file():
                    try:
                        path.unlink()
                    except OSError:
                        pass
        contract.delete()
        messages.success(request, "Договор удалён.")
        return redirect(reverse("contract_maker:contract_list"))
    return render(request, "contract_maker/contract_confirm_delete.html", {"contract": contract})


@login_required
@user_passes_test(_staff_required, login_url="/accounts/login/")
def contract_maker_success(request):
    """Страница после успешной генерации: ссылки на скачивание договора и акта."""
    last = request.session.get("contract_maker_last")
    if not last:
        return redirect(reverse("contract_maker:form"))
    return render(request, "contract_maker/success.html", {"last": last})


def _get_content_type(filename):
    """Content-Type по расширению (договоры и акты — docx или pdf)."""
    if filename and filename.lower().endswith(".pdf"):
        return "application/pdf"
    return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


@login_required
@user_passes_test(_staff_required, login_url="/accounts/login/")
def contract_maker_download(request, filename):
    """Скачивание или открытие файла договора/акта (.docx или .pdf). ?inline=1 — открыть в браузере."""
    allowed_prefixes = ("contract_", "act_")
    if ".." in filename or "/" in filename or "\\" in filename:
        raise Http404("File not found")
    if not any(filename.startswith(p) for p in allowed_prefixes):
        raise Http404("File not found")
    if not (filename.lower().endswith(".docx") or filename.lower().endswith(".pdf")):
        raise Http404("File not found")

    file_path = Path(generator_config.OUTPUT_DIR) / filename
    if not file_path.is_file():
        raise Http404("File not found")
    try:
        file_path.resolve().relative_to(Path(generator_config.OUTPUT_DIR).resolve())
    except ValueError:
        raise Http404("File not found")

    as_attachment = request.GET.get("inline") != "1"
    response = FileResponse(open(file_path, "rb"), as_attachment=as_attachment, filename=filename)
    response["Content-Type"] = _get_content_type(filename)
    if not as_attachment:
        response["Content-Disposition"] = "inline; filename=\"" + filename + "\""
    return response
