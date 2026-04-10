from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('menu/', include('apps.menu.urls', namespace='menu')),
    path('orders/', include('apps.orders.urls', namespace='orders')),
    path('inventory/', include('apps.inventory.urls', namespace='inventory')),
    path('billing/', include('apps.billing.urls', namespace='billing')),
    path('intelligence/', include('apps.intelligence.urls', namespace='intelligence')),
    path('', RedirectView.as_view(url='/orders/dashboard/', permanent=False)),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
