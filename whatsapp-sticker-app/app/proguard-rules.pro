# WhatsApp Sticker App ProGuard Rules

# Keep ContentProvider (WhatsApp queries it by class name)
-keep class com.bobastickers.whatsapp.StickerContentProvider { *; }

# Keep data models used by Gson
-keep class com.bobastickers.whatsapp.StickerPack { *; }
-keep class com.bobastickers.whatsapp.Sticker { *; }

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
