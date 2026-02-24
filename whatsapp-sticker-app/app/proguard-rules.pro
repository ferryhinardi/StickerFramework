# WhatsApp Sticker App ProGuard Rules

# Keep ContentProvider (WhatsApp queries it by class name)
-keep class com.yourbrand.stickers.StickerContentProvider { *; }

# Keep data models used by Gson
-keep class com.yourbrand.stickers.StickerPack { *; }
-keep class com.yourbrand.stickers.Sticker { *; }

# OkHttp
-dontwarn okhttp3.**
-keep class okhttp3.** { *; }

# Gson
-keep class com.google.gson.** { *; }
-keepattributes Signature
-keepattributes *Annotation*

# Glide
-keep public class * implements com.bumptech.glide.module.GlideModule
-keep class * extends com.bumptech.glide.module.AppGlideModule { <init>(...); }
