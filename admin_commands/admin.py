# admin_commands/admin.py

import io
import sys
import os
import contextlib
from django.contrib import admin, messages
from django.urls import path, reverse
from django.http import HttpResponseRedirect, FileResponse, HttpResponseForbidden
from django.core.management import call_command
from django.shortcuts import render
from django.conf import settings

class CommandAdminSite(admin.AdminSite):
    site_header = "Administração de Comandos"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('', self.admin_view(self.command_page), name='command_page'),
            path('run-command/<str:command_name>/', self.admin_view(self.run_command_view), name='run-command'),
            path('db/', self.admin_view(self.db_page), name='db_page'),
            path('download-db/', self.admin_view(self.download_db), name='download_db'),
        ]
        return custom_urls + urls

    def command_page(self, request):
        command_groups = [
            {
                'group_name': 'Atualizações de Dados',
                'commands': [
                    {'name': 'update', 'description': 'Atualiza todos os dados'},
                    {'name': 'get_historical_currency', 'description': 'Atualiza o histórico de moedas'},
                    {'name': 'update_cripto_price', 'description': 'Atualiza os preços das criptomoedas'},
                    {'name': 'update_currencies_price', 'description': 'Atualiza os preços das moedas'},
                    {'name': 'update_from_google', 'description': 'Atualiza dados do Google'},
                    {'name': 'update_from_fmp', 'description': 'Atualiza dados do Financial Modeling Prep'},
                    {'name': 'update_from_fundamentus', 'description': 'Atualiza dados do Fundamentus'},
                    {'name': 'update_from_yahoo', 'description': 'Atualiza dados do Yahoo Finance'},
                    {'name': 'update_total_dividends', 'description': 'Atualiza o total de dividendos'},
                    {'name': 'update_total_today', 'description': 'Atualiza o total de hoje'},
                ],
            },
            {
                'group_name': 'Cálculos',
                'commands': [
                    {
                        'name': 'calculate_evolution',
                        'description': 'Calcula a evolução',
                        'args': [
                            {
                                'name': 'tipo',
                                'type': 'choice',
                                'options': [
                                    {'value': 'D', 'label': 'Diogo'},
                                    {'value': 'I', 'label': 'Isabel'},
                                    {'value': 'G', 'label': 'Graciela'},
                                ],
                            },
                        ],
                    },
                    {
                        'name': 'properties_rents',
                        'description': 'Atualiza aluguéis de propriedades',
                        'args': [
                            {
                                'name': 'mes',
                                'type': 'text',
                                'placeholder': 'Mês (opcional)',
                            },
                            {
                                'name': 'ano',
                                'type': 'text',
                                'placeholder': 'Ano (opcional)',
                            },
                        ],
                    },
                ],
            },
            {
                'group_name': 'Históricos de Ativos',
                'commands': [
                    {'name': 'get_historical_br_assets', 'description': 'Atualiza histórico de ativos brasileiros'},
                    {'name': 'get_historical_us_assets', 'description': 'Atualiza histórico de ativos americanos'},
                ],
            },
            {
                'group_name': 'Outros Comandos',
                'commands': [
                    {'name': 'get_opgions_price_status_invest', 'description': 'Atualiza preços de opções do Status Invest'},
                    {'name': 'dividends_from_smartfolio', 'description': 'Atualiza dividendos do Smartfolio'},
                ],
            },
        ]

        # Recupera a saída da sessão, se existir
        command_output = request.session.pop('command_output', None)
        return render(request, 'admin/command_page.html', {
            'command_groups': command_groups,
            'command_output': command_output,
        })

    def run_command_view(self, request, command_name):
        if request.method == 'POST':
            # Coleta todos os argumentos passados no formulário
            command_args = []
            for key in request.POST:
                if key not in ('csrfmiddlewaretoken',):
                    value = request.POST.get(key)
                    if value:  # Adiciona apenas se o valor não for vazio
                        command_args.append(value)
            out = io.StringIO()
            try:
                # Redireciona o sys.stdout para capturar os prints
                with contextlib.redirect_stdout(out):
                    if command_args:
                        call_command(command_name, *command_args)
                    else:
                        call_command(command_name)
                output = out.getvalue()
                messages.success(request, f"Comando '{command_name}' executado com sucesso!")
                request.session['command_output'] = output
            except Exception as e:
                output = out.getvalue()
                messages.error(request, f"Erro ao executar o comando '{command_name}': {e}")
                request.session['command_output'] = output
            finally:
                out.close()
            return HttpResponseRedirect(reverse('admin_commands:command_page'))
        else:
            return HttpResponseRedirect(reverse('admin_commands:command_page'))

    def db_page(self, request):
        if not request.user.is_superuser:
            messages.error(request, "Você não tem permissão para acessar esta página.")
            return HttpResponseRedirect(reverse('admin:index'))

        return render(request, 'admin/db_page.html')

    def download_db(self, request):
        if not request.user.is_superuser:
            return HttpResponseForbidden("Você não tem permissão para acessar este arquivo.")

        db_path = settings.DATABASES['default']['NAME']
        if not os.path.exists(db_path):
            messages.error(request, "O arquivo de banco de dados não foi encontrado.")
            return HttpResponseRedirect(reverse('admin_commands:db_page'))

        response = FileResponse(open(db_path, 'rb'), content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(db_path)}"'
        return response

admin_site = CommandAdminSite(name='admin_commands')