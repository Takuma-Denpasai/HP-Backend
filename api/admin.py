from django.contrib import admin
from .models import (
    UserData, OrganizationData, OrganizationPermissionData,
    OrganizationPermissionInspectionData, PermissionData, NewsData,
    NewsImageData, NewsInspectionData, EventData, EventImageData,
    EventInspectionData, ShopData, ShopImageData, ShopInspectionData,
    MenuData, MenuInspectionData, PostData, PostImageData,
    PostInspectionData, BandData, BandInspectionData, BandSongData,
    BandSongInspectionData, KaraokeData, KaraokeInspectionData
)

# 各モデルを管理サイトに登録
admin.site.register(UserData)
admin.site.register(OrganizationData)
admin.site.register(OrganizationPermissionData)
admin.site.register(OrganizationPermissionInspectionData)
admin.site.register(PermissionData)
admin.site.register(NewsData)
admin.site.register(NewsImageData)
admin.site.register(NewsInspectionData)
admin.site.register(EventData)
admin.site.register(EventImageData)
admin.site.register(EventInspectionData)
admin.site.register(ShopData)
admin.site.register(ShopImageData)
admin.site.register(ShopInspectionData)
admin.site.register(MenuData)
admin.site.register(MenuInspectionData)
admin.site.register(PostData)
admin.site.register(PostImageData)
admin.site.register(PostInspectionData)
admin.site.register(BandData)
admin.site.register(BandInspectionData)
admin.site.register(BandSongData)
admin.site.register(BandSongInspectionData)
admin.site.register(KaraokeData)
admin.site.register(KaraokeInspectionData)