<!doctype html>
<html lang="uk">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{{ $title }} · {{ config('app.name') }}</title>
    @viteReactRefresh
    @vite(['resources/css/admin.css', 'resources/js/admin.jsx'])
</head>
<body class="admin-shell">
    <a class="admin-skip" href="#main-content">Перейти до вмісту</a>
    <aside class="admin-sidebar">
        <a class="admin-brand" href="{{ route('admin.overview') }}">
            <svg aria-hidden="true" viewBox="0 0 28 28" fill="none">
                <path d="M5 9h16l-4-4m4 4-4 4M23 19H7l4 4m-4-4 4-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span>{{ config('app.name') }}</span>
        </a>
        <div class="admin-sidebar__workspace">Керування каталогом</div>
        <nav class="admin-nav" aria-label="Адміністративне меню">
            @foreach ([
                ['admin.overview', 'Огляд', 'M3 3h7v7H3zM14 3h7v7h-7zM3 14h7v7H3zM14 14h7v7h-7z'],
                ['admin.products', 'Позиції каталогу', 'M4 7l8-4 8 4v10l-8 4-8-4zm0 0 8 4 8-4m-8 4v10'],
                ['admin.categories', 'Категорії', 'M4 7h6l2 2h8v9H4zm0 0V5h6l2 2h8v2'],
            ] as [$route, $label, $icon])
                <a href="{{ route($route) }}" class="admin-nav__link" @if (request()->routeIs($route)) aria-current="page" @endif>
                    <svg aria-hidden="true" viewBox="0 0 24 24" fill="none">
                        <path d="{{ $icon }}" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    <span>{{ $label }}</span>
                </a>
            @endforeach
        </nav>
        <div class="admin-sidebar__footer">
            <a class="admin-sidebar__catalog" href="{{ route('catalog.index') }}">
                <span>Публічний каталог</span><span aria-hidden="true">↗</span>
            </a>
        </div>
    </aside>

    <main id="main-content" class="admin-page">
        <header class="admin-page__header">
            <div class="admin-page__context">{{ config('app.name') }} <span aria-hidden="true">/</span> Адміністрування</div>
            <div class="admin-page__heading">
                <div>
                    <h1>{{ $title }}</h1>
                    <p>{{ $description }}</p>
                </div>
                <span class="admin-page__badge">Навчальний каталог</span>
            </div>
        </header>
        <div id="admin-content" data-screen="{{ $screen }}">
            <noscript><p>Для відображення даних потрібен JavaScript.</p></noscript>
        </div>
    </main>
</body>
</html>
