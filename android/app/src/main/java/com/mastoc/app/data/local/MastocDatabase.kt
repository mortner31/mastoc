package com.mastoc.app.data.local

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase

@Database(
    entities = [
        ClimbEntity::class,
        HoldEntity::class,
        FaceEntity::class
    ],
    version = 3,
    exportSchema = false
)
abstract class MastocDatabase : RoomDatabase() {

    abstract fun climbDao(): ClimbDao
    abstract fun holdDao(): HoldDao
    abstract fun faceDao(): FaceDao

    companion object {
        private const val DATABASE_NAME = "mastoc_db"

        @Volatile
        private var INSTANCE: MastocDatabase? = null

        fun getInstance(context: Context): MastocDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    MastocDatabase::class.java,
                    DATABASE_NAME
                )
                    .fallbackToDestructiveMigration()
                    .build()
                INSTANCE = instance
                instance
            }
        }
    }
}
