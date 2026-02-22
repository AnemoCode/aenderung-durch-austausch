import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

CHART_DATA = [
    {'date': '12. Okt', 'words': 4500, 'pages': 12},
    {'date': '13. Okt', 'words': 5200, 'pages': 14},
    {'date': '14. Okt', 'words': 5200, 'pages': 14},
    {'date': '15. Okt', 'words': 6800, 'pages': 18},
    {'date': '16. Okt', 'words': 8100, 'pages': 22},
    {'date': '17. Okt', 'words': 9500, 'pages': 26},
    {'date': '18. Okt', 'words': 11200, 'pages': 31},
    {'date': '19. Okt', 'words': 14500, 'pages': 40},
]

PROJECTS = [
    {
        'id': 1,
        'name': 'Masterarbeit_Physik',
        'git_url': 'https://git.overleaf.com/6538...',
        'words': 14500,
        'pages': 40,
        'status': 'OK',
        'last_sync': 'Vor 10 Min',
        'shared_with': 'Prof. Müller (Reviewer)',
    },
    {
        'id': 2,
        'name': 'Paper_NeurIPS_2024',
        'git_url': 'https://git.overleaf.com/8821...',
        'words': 4200,
        'pages': 8,
        'status': 'OK',
        'last_sync': 'Vor 1 Std',
        'shared_with': 'ML Research Group',
    },
    {
        'id': 3,
        'name': 'Gruppenarbeit_Verteilte_Systeme',
        'git_url': 'https://git.overleaf.com/1192...',
        'words': 1250,
        'pages': 3,
        'status': 'AUTH_ERROR',
        'last_sync': 'Vor 2 Tagen',
        'shared_with': 'Studienkollegen',
    },
]

GROUPS = [
    {'id': 1, 'name': 'ML Research Group', 'members': 5, 'shared_projects': 2, 'role': 'Admin'},
    {'id': 2, 'name': 'Studienkollegen', 'members': 3, 'shared_projects': 1, 'role': 'Member'},
    {'id': 3, 'name': 'Prof. Müller (Reviewer)', 'members': 2, 'shared_projects': 1, 'role': 'Admin'},
]


@login_required
def index(request):
    return render(request, 'dashboard/index.html', {
        'active_nav': 'index',
        'chart_data_json': json.dumps(CHART_DATA),
        'projects': PROJECTS,
        'stats': {
            'total_words': 19950,
            'total_pages': 51,
            'active_projects': 3,
            'next_sync': 'In 45 Min',
        },
    })


@login_required
def projects(request):
    return render(request, 'dashboard/projects.html', {
        'active_nav': 'projects',
        'projects': PROJECTS,
    })


@login_required
def groups(request):
    return render(request, 'dashboard/groups.html', {
        'active_nav': 'groups',
        'groups': GROUPS,
    })


@login_required
def settings_view(request):
    return render(request, 'dashboard/settings.html', {
        'active_nav': 'settings',
    })
