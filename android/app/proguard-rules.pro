# Add project specific ProGuard rules here.
# You can control the set of applied configuration files using the
# proguardFiles setting in build.gradle.

# For more details, see
#   http://developer.android.com/guide/developing/tools/proguard.html

# Keep class names for Room entities
#-keep class * extends androidx.room.RoomDatabase { *; }

# Preserve the special static methods that are required in all enumeration classes.
-keepclassmembers enum * {
    public static **[] values();
    public static ** valueOf(java.lang.String);
}

# Uncomment for debugging
# -dontobfuscate
# -keepattributes SourceFile,LineNumberTable
